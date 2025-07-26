import json
import datetime

from decimal import Decimal
from pydantic import Field
from typing import List


from models.queues import ProductConfiguration
from models.order_configs import OrderConfigurationMapping
from models.api import Position

from utils.logger import logger as log
from utils.api_client import ProviderClient, notify_assistant
from utils.lambda_client import LambdaClient
from utils.common import send_message_to_queue, ULID, Env, ASSISTANT_NOTIFICATION_MESSAGE
from utils import exceptions

SERVICE = "strategy"


class MomentumStrategy(ProductConfiguration):
    correlation_id: str = Field(..., alias="correlation_id")
    positions: List[Position] = Field(..., alias="positions")
    portfolio: dict = Field(..., alias="portfolio")
    strategy_term: str = Field(..., alias="strategy_term")

    def review_positions(self, data):
        OPERATION = "REVIEW_POSITIONS"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
        )

        if not self.positions:
            logger.warning(
                "NO_POSITIONS_FOUND",
                message="No positions found.",
                product_id=self.product_id,
                provider=self.provider,
            )
            return []

        positions_with_profit = []
        for position in self.positions:
            try:
                self.analyze_historical_data_selling(
                    data, position.filled_size, position.average_filled_price, position.position_id
                )
            except exceptions.AnalyzeSellPricesException as e:
                logger.warning("REVIEW_MARKET_ANALYZE_EXCEPTION", **e.__dict__)
                continue
            except Exception as e:
                logger.error(
                    "REVIEW_MARKET_GENERAL_EXCEPTION",
                    message="Error analyzing sell prices",
                    error=str(e),
                )
                raise e
            positions_with_profit.append(position)

        return positions_with_profit

    def order_side(self, historical_data, side=None):
        OPERATION = "ORDER_SIDE"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
        )
        if self.strategy_term == "SHORT_TERM":
            # For short term trading, this will always be a buy
            return "BUY", [], f"{SERVICE}_{OPERATION}_HIGH"
        elif self.strategy_term == "MEDIUM_TERM":
            # If we get a side from the event, this is our only option
            if side == "BUY":
                self.analyze_historical_data_buying(historical_data)
                return side, self.positions, f"{SERVICE}_{OPERATION}_MED"
            elif side == "SELL":
                positions = self.review_positions(historical_data)
                if not positions:
                    logger.warning(
                        "ORDER_SIDE_NO_POSITIONS",
                        message="No positions found.",
                        product_id=self.product_id,
                        provider=self.provider,
                    )
                    raise exceptions.RequestedSellNoPositions("No positions found.")
                return side, positions, f"{SERVICE}_{OPERATION}_MED"
            else:
                # No side so we check first for any positions
                # and then we check for any buying opportunities
                try:
                    # Check positions for any profit based on historical data
                    positions = self.review_positions(historical_data)
                except Exception as e:
                    logger.error("LOOK_FOR_PROFIT_EXCEPTION", message=str(e), side=side)
                    raise e

                if positions:
                    risk = f"{SERVICE}_{OPERATION}_LOW"
                    side = "SELL"

                else:
                    side = "BUY"
                    risk = f"{SERVICE}_{OPERATION}_MED"
                    self.analyze_historical_data_buying(historical_data)

                return side, positions, risk

    def validate_price_diff_pct(self, historical_data):
        """ This function checks the max min diff percentage"""
        OPERATION = "PRICE_DIFF_PCT"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
        )
        
        latest_price = historical_data[0]["close"] or 0
        opening_price = historical_data[-1]["close"] or 0

        try:
            _diff = Decimal(latest_price) - Decimal(opening_price)
            try:
                x = _diff / Decimal(opening_price)
            except ZeroDivisionError:
                x = 0
            diff_pct = (x) * 100

            if self.strategy_term == "SHORT_TERM":
                price_diff_pct_max_threshold = Decimal("1.0")
                price_diff_pct_min_threshold = Decimal("1.0")
                if price_diff_pct_max_threshold <= diff_pct <= price_diff_pct_min_threshold:  # TODO: Configurable
                    return False, diff_pct
            elif self.strategy_term == "MEDIUM_TERM":
                price_diff_pct_max_threshold = Decimal("-5.0")
                price_diff_pct_min_threshold = Decimal("-10.0")
                # For MEDIUM_TERM, we return False if the diff_pct is in the restricted range (-10% to -5%)
                if price_diff_pct_min_threshold <= diff_pct <= price_diff_pct_max_threshold:
                    return False, diff_pct
            elif self.strategy_term == "LONG_TERM":
                pass
                # price_diff_pct_max_threshold = self.price_diff_pct_max_threshold
                # price_diff_pct_min_threshold = self.price_diff_pct_min_threshold
            else:
                raise ValueError(
                    f"Invalid strategy term: {self.strategy_term}"
                )
        except Exception as e:
            logger.error("ERROR_VALIDATING_PRICE_DIFF_PCT", message=str(e))
            raise

        return True, diff_pct

    def validate_support_resistance(self, historical_data, tolerance=0.05):
        from statistics import mean
        """ This function checks the support and resistance levels"""
        OPERATION = "VALIDATE_SUPPORT_RESISTANCE"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
        )
        try:
            highs = [Decimal(candle["high"]) for candle in historical_data]
            lows = [Decimal(candle["low"]) for candle in historical_data]

            # Find potential support and resistance levels
            support_levels = []
            resistance_levels = []

            for low in lows:
                if all(abs(low - other_low) / low <= tolerance for other_low in lows):
                    support_levels.append(low)

            for high in highs:
                if all(abs(high - other_high) / high <= tolerance for other_high in highs):
                    resistance_levels.append(high)

            # Average the clustered levels
            support = mean(support_levels) if support_levels else None
            resistance = mean(resistance_levels) if resistance_levels else None
        except Exception as e:
            logger.error("ERROR_VALIDATING_SUPPORT_RESISTANCE", message=str(e))
            raise e

        
        return {"support": support, "resistance": resistance}
    
    def detect_bullish_engulfing(self, historical_data):
        # Assumes data is a list of dicts with 'open', 'close', 'high', 'low'
        for i in range(1, len(historical_data)):
            prev = historical_data[len(historical_data)-i]
            curr = historical_data[(len(historical_data)-i)-1]

            prev_open = Decimal(prev["open"])
            prev_close = Decimal(prev["close"])
            curr_open = Decimal(curr["open"])
            curr_close = Decimal(curr["close"])
            
            # Previous candle bearish, current candle bullish and engulfs previous
            if prev_close < prev_open and curr_close > curr_open:
                if curr_close > prev_open and curr_open < prev_close:
                    return True
        return False

    def detect_bearish_engulfing(self, historical_data):
        for i in range(1, len(historical_data)):
            prev = historical_data[len(historical_data)-i]
            curr = historical_data[(len(historical_data)-i)-1]

            prev_open = Decimal(prev["open"])
            prev_close = Decimal(prev["close"])
            curr_open = Decimal(curr["open"])
            curr_close = Decimal(curr["close"])

            if prev_close > prev_open and curr_close < curr_open:
                if curr_open > prev_close and curr_close < prev_open:
                    return True
        return False
    
    def confirm_side_with_trend(self, historical_data, side):
        levels = self.validate_support_resistance(historical_data)
        support = levels["support"]
        resistance = levels["resistance"]
        latest_close = Decimal(historical_data[0]["close"])
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation="CONFIRM_SIDE_WITH_TREND",
            strategy_term=self.strategy_term,
        )

        candle_stick_scope = 12
        support_level_threshold = Decimal("0.01")  # TODO: Configurable
        resistance_level_threshold = Decimal("0.01")  # TODO: Configurable

        bullish = self.detect_bullish_engulfing(historical_data[:candle_stick_scope]) 
        bearish = self.detect_bearish_engulfing(historical_data[:candle_stick_scope])

        if (support and (abs(latest_close - support) / support < support_level_threshold) and bullish and side == "BUY") or \
           (resistance and (abs(latest_close - resistance) / resistance < resistance_level_threshold) and bearish and side == "SELL"):  # TODO: Configurable
            return True

        logger.warning(
            "CONFIRM_SIDE_WITH_TREND_WARNING",
            message="Trend confirmation failed",
            side=side,
            support=support,
            resistance=resistance,
            latest_close=latest_close,
            bullish=bullish,
            bearish=bearish
        )        
        raise exceptions.InvalidSideException(
            f"Invalid side: {side}. Support: {support}, Resistance: {resistance}, Latest Close: {latest_close}"
        )

    def handle_historical_data(self):
        OPERATION = "HANDLE_HISORTICAL_DATA"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
        )
        if self.strategy_term == "SHORT_TERM":
            # UNIX value for 4 hours ago
            start = int(
                (datetime.datetime.now() - datetime.timedelta(hours=5)).timestamp()  # TODO: Configurable
            )
            granularity = 1  # TODO: Configurable 1 minute candles

            end = int(datetime.datetime.now().timestamp())

            try:
                provider_client = ProviderClient(
                    provider=self.provider,
                    correlation_id=self.correlation_id,
                    service=SERVICE,
                    operation=OPERATION,
                )
                response = provider_client.get_candles(self.product_id, start=start, end=end, granularity=granularity)
            except exceptions.GetProviderCandlesException as e:
                logger.error("GET_CANDLES_EXCEPTION", message=str(e))
                raise e

            candles = response["candles"]

            # send this data to data collection service
            msg_body = {
                "data_collection_type": "CANDLE_STICK",
                "candle_stick_data": candles,
            }
            msg_attributes = {
                "provider": {
                    "stringValue": self.provider,
                    "dataType": "String",
                },
                "product_id": {
                    "stringValue": self.product_id,
                    "dataType": "String",
                },
                "correlation_id": {
                    "stringValue": self.correlation_id,
                    "dataType": "String",
                },
            }
            send_message_to_queue(
                Env.QUEUE_DATA_COLLECTION_URL,
                msg_body,
                msg_attrs=msg_attributes,
            )
        elif self.strategy_term == "MEDIUM_TERM":
            # UNIX value for 5 days ago
            start = int(
                (datetime.datetime.now() - datetime.timedelta(days=5)).timestamp()
            )
            granularity = 4 # TODO: Configurable 1 hour candles
            end = int(datetime.datetime.now().timestamp())

            try:
                provider_client = ProviderClient(
                    provider=self.provider,
                    correlation_id=self.correlation_id,
                    service=SERVICE,
                    operation=OPERATION,
                )
                response = provider_client.get_candles(self.product_id, start=start, end=end, granularity=granularity)
            except exceptions.GetProviderCandlesException as e:
                logger.error("GET_CANDLES_EXCEPTION", message=str(e))
                raise e

            candles = response["candles"]
        else:
            raise ValueError(
                f"Invalid strategy term: {self.strategy_term}"
            )
        
        

        return candles

    def analyze_historical_data_buying(self, data):
        """
        Here we will look at previous prices
        to determine when is the best time to buy
        """
        # We skip adding the trend to our sum for our first
        # price since that's just used to get the prev trend
        # for our initial price
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation="ANALYZE_BUY_DATA",
        )
      
        maxmin_diffpct_check_passed, diff_pct = self.validate_price_diff_pct(data)
        if not maxmin_diffpct_check_passed:
            logger.warning(
                "MAX_MIN_DIFF_PCT_CHECK_FAILED",
                message="Max min diff pct check failed",
                diff_pct=diff_pct,
            )
            raise exceptions.AnalyzeBuyPricesException(
                "Max min diff pct check failed"
            )

    def analyze_historical_data_selling(self, data, size, at_price, position_id):
        """
        Args:
            temp_dict (_type_): _description_
            pending_order_id_list (_type_): _description_
        """
        current_price = Decimal(data[0]["close"])
        profit_target_pct_max = self.profit_target
        profit_target_pct_min = Decimal("4.0")  # TODO: Configurable

        current_amt = current_price * size
        bought_amt = at_price * size

        profit_amt_dlrs = current_amt - bought_amt
        profit_pct = (profit_amt_dlrs / bought_amt) * 100

        if profit_target_pct_min <= profit_pct <= profit_target_pct_max:
            message = ASSISTANT_NOTIFICATION_MESSAGE.format(
                product_id=self.product_id,
                provider=self.provider,
                strategy_term=self.strategy_term,
                size=size,
                current_price=current_price,
                at_price=at_price,
                profit_pct=profit_pct,
                profit_amt_dlrs=profit_amt_dlrs,
                current_amt=current_amt,
                bought_amt=bought_amt,
                position_id=position_id
            )
            
            notify_assistant(
                self.correlation_id,
                message
            )
            raise exceptions.AnalyzeSellPricesException(
                "Price is too low to sell profit",
                profit_pct=profit_pct,
                profit_amt_dlrs=profit_amt_dlrs,
                current_amt=current_amt,
                bought_amt=bought_amt,
            )
        elif profit_pct <= profit_target_pct_min:
            raise exceptions.AnalyzeSellPricesException(
                "Price is too low to sell profit",
                profit_pct=profit_pct,
                profit_amt_dlrs=profit_amt_dlrs,
                current_amt=current_amt,
                bought_amt=bought_amt,
            )

    def ta_indicators(self, historical_data):
        """
        This function will calculate the technical analysis indicators
        for the historical data.
        """
        OPERATION = "TA_INDICATORS"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
        )

        try:
            lambda_client = LambdaClient(
                correlation_id=self.correlation_id
            )
        except Exception as e:
            logger.error("LAMBDA_CLIENT_EXCEPTION", message=str(e))
            raise e

        payload = {
            "historical_data": historical_data,
            "product_id": self.product_id,
            "provider": self.provider,
            "n1": 14,  # TODO: Configurable
            "n2": 50,  # TODO: Configurable
            "strategy_term": self.strategy_term,
            "correlation_id": self.correlation_id,
            "indicators": [
                "sma",  # Simple Moving Average
                # "ema",  # Exponential Moving Average
                # "rsi",  # Relative Strength Index
                # "macd",  # Moving Average Convergence Divergence
                # "bollinger_bands",  # Bollinger Bands
            ],
            "candle_stick_scope": 12,  # TODO: Configurable
            "support_resistance_tolerance": 0.05,  # TODO: Configurable
        }
        
        try:
            response = lambda_client.invoke_lambda_function(
                json.dumps(payload)
            )
            
        except Exception as e:
            logger.error("INVOKE_LAMBDA_EXCEPTION", message=str(e))
            raise e
        
        response = json.loads(response)
        if response.get("status") != "success":
            logger.error(
                "BAD_LAMBDA_RESPONSE",
                message="Error calculating technical indicators",
                error=response.get("error", "Unknown error"),
            )
            raise Exception(
                str(response)
            )

        return response.get("signals", [])

    def run(self, side=None):
        OPERATION = "STRATEGY_RUN"
        logger = log.bind(
            correlation_id=self.correlation_id,
            product_id=self.product_id,
            provider=self.provider,
            service=SERVICE,
            operation=OPERATION,
            strategy_term=self.strategy_term,
        )

        risk_flags = []

        try:
            historical_data = self.handle_historical_data()
        except Exception as e:
            logger.error("HANDLE_TICKER_EXCEPTION", message=str(e), side=side)
            raise e
        
        try:
            signals = self.ta_indicators(historical_data)
        except Exception as e:
            logger.error("TA_INDICATORS_EXCEPTION", message=str(e), side=side)
            raise e
        
        try:
            side, positions, risk = self.order_side(historical_data, side)
        except exceptions.RequestedSellNoPositions as e:
            raise e
        except Exception as e:
            logger.error("ORDER_SIDE_GENERAL_EXCEPTION", message=str(e), side=side)
            raise Exception("ORDER_SIDE_GENERAL_EXCEPTION")

        risk_flags.append(risk)

        try:
            self.confirm_side_with_trend(historical_data, side)
            risk_flags.append(f"{SERVICE}_{OPERATION}_LOW")
        except exceptions.InvalidSideException as e:
            risk_flags.append(f"{SERVICE}_{OPERATION}_HIGH")
        except Exception as e:
            logger.error("CONFIRM_TREND_EXCEPTION", message=str(e))
            raise e
            
            
        return side, historical_data, positions, risk_flags

class StrategyHandler:
    @classmethod
    def create(cls, **kwargs):
        strategy_term = kwargs.get("strategy_term")
        strategy_type = kwargs.get("strategy_type")
        if strategy_term == "MEDIUM_TERM":
            return MomentumStrategy(**kwargs)
        elif strategy_term == "SHORT_TERM":
            return MomentumStrategy(**kwargs)
        else:
            raise ValueError(f"INVALID_STRATEGY: TYPE {strategy_type}, TERM {strategy_term}")


def handler(event, context):
    """ Handles events from Assets service """
    OPERATION = "ASSETS_HANDLER"
    record = event["Records"][0] or {}
    event_body_dict = json.loads(record.get("body", {}))
    portfolio = event_body_dict.get("portfolio")
    correlation_id = event_body_dict.get("correlation_id", str(ULID()))
    provider = event_body_dict.get("provider")
    product = event_body_dict.get("product")
    strategy_term = event_body_dict.get("strategy_term")
    product_id = product.get("product_id")
    assets_requested_side = event_body_dict.get("side")
    risk_flags = event_body_dict.get("risk_flags", [])

    config_dict = event_body_dict.get("config")

    positions = event_body_dict.get("positions", [])
    assistant_event = event_body_dict.get("assistant_event", False)

    logger = log.bind(
        correlation_id=correlation_id,
        product_id=product_id,
        provider=provider,
        service=SERVICE,
        operation=OPERATION,
        strategy_term=strategy_term,
    )

    strategy = StrategyHandler.create(
        provider=provider,
        product_id=product_id,
        portfolio=portfolio,
        positions=positions,
        correlation_id=correlation_id,
        strategy_term=strategy_term,
        **config_dict,
    )

    try:
        side, historical_data, positions, new_risk_flags = strategy.run(assets_requested_side)
    except exceptions.RequestedSellNoPositions:
        return {
            "statusCode": 200,
        }
    except Exception as e:
        logger.error(
            "STRATEGY_FAILED",
            message="Failed to analyze product for buying/selling",
            error=str(e),
        )
        raise e

    positions_dict = [
        position.model_dump()
        for position in positions
    ]

    # Add risk flags to the list
    risk_flags.extend(new_risk_flags)

    msg_body = {}
    msg_body["portfolio"] = portfolio
    msg_body["product"] = product
    msg_body["correlation_id"] = correlation_id
    msg_body["provider"] = provider
    msg_body["config"] = config_dict
    msg_body["side"] = side
    msg_body["positions"] = positions_dict
    msg_body["strategy_term"] = strategy_term
    msg_body["historical_data"] = historical_data
    msg_body["risk_flags"] = risk_flags
    msg_body["assistant_event"] = assistant_event

    send_message_to_queue(Env.QUEUE_RISK_URL, msg_body)

    logger.info(
        "STRATEGY_COMPLETE",
        message="Analyzed product for buying/selling",
        product_id=product_id,
        provider=provider
    )

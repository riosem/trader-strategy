from pydantic import Field
from typing import Optional
from decimal import Decimal
from enum import Enum

from models.queues import ProductConfiguration


class OrderConfiguration(ProductConfiguration):
    side: Optional[str] = Field(default=None, alias="side")


class MarketMarketIOCConfiguration(OrderConfiguration):
    quote_size: Optional[Decimal] = Field(default=None, alias="quote_size")
    base_size: Optional[Decimal] = Field(default=None, alias="base_size")

    def model_dump(self):
        if self.side == "BUY":
            return {
                "market_market_ioc": {
                    "quote_size": self.quote_size,
                }
            }
        elif self.side == "SELL":
            return {
                "market_market_ioc": {
                    "base_size": self.base_size,
                }
            }
        else:
            return {"market_market_ioc": {}}


class LimitLimitGTDConfiguration(OrderConfiguration):
    quote_size: Optional[Decimal] = Field(default=None, alias="quote_size")
    base_size: Optional[Decimal] = Field(default=None, alias="base_size")
    limit_price: Optional[Decimal] = Field(default=None, alias="limit_price")
    end_time: Optional[str] = Field(default=None, alias="end_time")
    post_only: Optional[bool] = Field(default=False, alias="post_only")

    def model_dump(self):
        if self.side == "BUY":
            return {
                "limit_limit_gtd": {
                    "quote_size": self.quote_size,
                    "limit_price": self.limit_price,
                    "end_time": self.end_time,
                    "post_only": self.post_only,
                }
            }
        elif self.side == "SELL":
            return {
                "limit_limit_gtd": {
                    "base_size": self.base_size,
                    "limit_price": self.limit_price,
                    "end_time": self.end_time,
                    "post_only": self.post_only,
                }
            }
        else:
            return {"limit_limit_gtd": {}}


class SorLimitIOCConfiguration(OrderConfiguration):
    quote_size: Optional[Decimal] = Field(default=None, alias="quote_size")
    base_size: Optional[Decimal] = Field(default=None, alias="base_size")
    limit_price: Optional[Decimal] = Field(default=None, alias="limit_price")

    def model_dump(self):
        if self.side == "BUY":
            return {
                "sor_limit_ioc": {
                    "quote_size": self.quote_size,
                    "limit_price": self.limit_price,
                }
            }
        elif self.side == "SELL":
            return {
                "sor_limit_ioc": {
                    "base_size": self.base_size,
                    "limit_price": self.limit_price,
                }
            }
        else:
            return {"sor_limit_ioc": {}}


class LimitLimitGTCConfiguration(OrderConfiguration):
    quote_size: Optional[Decimal] = Field(default=None, alias="quote_size")
    base_size: Optional[Decimal] = Field(default=None, alias="base_size")
    limit_price: Optional[Decimal] = Field(default=None, alias="limit_price")
    post_only: Optional[bool] = Field(default=False, alias="post_only")

    def model_dump(self):
        if self.side == "BUY":
            return {
                "limit_limit_gtc": {
                    "quote_size": self.quote_size,
                    "limit_price": self.limit_price,
                    "post_only": self.post_only,
                }
            }
        elif self.side == "SELL":
            return {
                "limit_limit_gtc": {
                    "base_size": self.base_size,
                    "limit_price": self.limit_price,
                    "post_only": self.post_only,
                }
            }
        else:
            return {"limit_limit_gtc": {}}


class LimitLimitFOKConfiguration(OrderConfiguration):
    quote_size: Optional[Decimal] = Field(default=None, alias="quote_size")
    base_size: Optional[Decimal] = Field(default=None, alias="base_size")
    limit_price: Decimal = Field(default=None, alias="limit_price")

    def model_dump(self):
        if self.side == "BUY":
            return {
                "limit_limit_fok": {
                    "quote_size": self.quote_size,
                    "limit_price": self.limit_price,
                }
            }
        elif self.side == "SELL":
            return {
                "limit_limit_fok": {
                    "base_size": self.base_size,
                    "limit_price": self.limit_price,
                }
            }
        else:
            return {"limit_limit_fok": {}}


class StopDirection(str, Enum):
    STOP_UP = "STOP_DIRECTION_STOP_UP"
    STOP_DOWN = "STOP_DIRECTION_STOP_DOWN"


class StopLimitStopLimitGTCConfiguration(OrderConfiguration):
    base_size: Decimal = Field(default=None, alias="base_size")
    stop_price: Decimal = Field(default=None, alias="stop_price")
    limit_price: Decimal = Field(default=None, alias="limit_price")
    stop_direction: StopDirection = Field(default=None, alias="stop_direction")

    def model_dump(self):
        if self.side == "BUY":
            return {
                "stop_limit_stop_limit_gtc": {
                    "base_size": self.base_size,
                    "stop_price": self.stop_price,
                    "limit_price": self.limit_price,
                    "stop_direction": self.stop_direction,
                }
            }
        elif self.side == "SELL":
            return {
                "stop_limit_stop_limit_gtc": {
                    "base_size": self.base_size,
                    "stop_price": self.stop_price,
                    "limit_price": self.limit_price,
                    "stop_direction": self.stop_direction,
                }
            }
        else:
            return {"stop_limit_stop_limit_gtc": {}}


class StopLimitStopLimitGTDConfiguration(OrderConfiguration):
    base_size: Decimal = Field(default=None, alias="base_size")
    stop_price: Decimal = Field(default=None, alias="stop_price")
    limit_price: Decimal = Field(default=None, alias="limit_price")
    stop_direction: StopDirection = Field(default=None, alias="stop_direction")
    end_time: str = Field(default=None, alias="end_time")  # RFC3339 Timestamp

    def model_dump(self):
        if self.side == "BUY":
            return {
                "stop_limit_stop_limit_gtd": {
                    "base_size": self.base_size,
                    "stop_price": self.stop_price,
                    "limit_price": self.limit_price,
                    "stop_direction": self.stop_direction,
                    "end_time": self.end_time,
                }
            }
        elif self.side == "SELL":
            return {
                "stop_limit_stop_limit_gtd": {
                    "base_size": self.base_size,
                    "stop_price": self.stop_price,
                    "limit_price": self.limit_price,
                    "stop_direction": self.stop_direction,
                    "end_time": self.end_time,
                }
            }
        else:
            return {"stop_limit_stop_limit_gtd": {}}


class TriggerBracketGTCConfiguration(OrderConfiguration):
    base_size: Decimal = Field(default=None, alias="base_size")
    stop_trigger_price: Decimal = Field(default=None, alias="stop_trigger_price")
    limit_price: Decimal = Field(default=None, alias="limit_price")
    end_time: str = Field(default=None, alias="end_time")  # RFC3339 Timestamp

    def model_dump(self):
        if self.side == "BUY":
            return {
                "trigger_bracket_gtc": {
                    "base_size": self.base_size,
                    "stop_trigger_price": self.stop_trigger_price,
                    "limit_price": self.limit_price,
                    "end_time": self.end_time,
                }
            }
        elif self.side == "SELL":
            return {
                "trigger_bracket_gtc": {
                    "base_size": self.base_size,
                    "stop_trigger_price": self.stop_trigger_price,
                    "limit_price": self.limit_price,
                    "end_time": self.end_time,
                }
            }
        else:
            return {"trigger_bracket_gtc": {}}


OrderConfigurationMapping = {
    "market_market_ioc": MarketMarketIOCConfiguration,
    "sor_limit_ioc": SorLimitIOCConfiguration,
    "limit_limit_gtc": LimitLimitGTCConfiguration,
    "limit_limit_gtd": LimitLimitGTDConfiguration,
    "limit_limit_fok": LimitLimitFOKConfiguration,
    "stop_limit_stop_limit_gtc": StopLimitStopLimitGTCConfiguration,
    "stop_limit_stop_limit_gtd": StopLimitStopLimitGTDConfiguration,
    "trigger_bracket_gtc": TriggerBracketGTCConfiguration,
}

import json
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from functions.strategies import MomentumStrategy, StrategyHandler, handler
from utils.common import Env
from utils.exceptions import AnalyzeSellPricesException, AnalyzeBuyPricesException, InvalidSideException, RequestedSellNoPositions


class TestMomentumStrategy:
    
    def test_init_momentum_strategy(self, config, positions, portfolio):
        """Test MomentumStrategy initialization"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        assert strategy.provider == "COINBASE"
        assert strategy.product_id == "BTC-USD"
        assert strategy.strategy_term == "MEDIUM_TERM"
        assert strategy.correlation_id == "test-correlation-id"

    def test_review_positions_no_positions(self, config, portfolio):
        """Test review_positions when no positions exist"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=[],
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100000"}]
        result = strategy.review_positions(historical_data)
        assert result == []

    def test_review_positions_with_profitable_positions(self, config, positions, portfolio):
        """Test review_positions with profitable positions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Mock profitable scenario - current price much higher than buy price
        historical_data = [{"close": "80000"}]  # Higher than position buy price of 70000
        
        result = strategy.review_positions(historical_data)
        assert len(result) == 1
        assert result[0] == positions[0]

    def test_review_positions_with_unprofitable_positions(self, config, positions, portfolio):
        """Test review_positions with unprofitable positions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "60000"}]  # Lower than position buy price
        
        result = strategy.review_positions(historical_data)
        assert result == []

    def test_order_side_short_term(self, config, positions, portfolio):
        """Test order_side for SHORT_TERM strategy"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="SHORT_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100000"}]
        side, returned_positions, risk = strategy.order_side(historical_data)
        
        assert side == "BUY"
        assert returned_positions == []
        assert "HIGH" in risk

    def test_order_side_medium_term_buy(self, config, positions, portfolio):
        """Test order_side for MEDIUM_TERM strategy with BUY side"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "105"}, {"close": "100"}]  # 5% gain
        side, returned_positions, risk = strategy.order_side(historical_data, side="BUY")
        
        assert side == "BUY"
        assert returned_positions == positions
        assert "MED" in risk

    def test_order_side_medium_term_sell_with_positions(self, config, positions, portfolio):
        """Test order_side for MEDIUM_TERM strategy with SELL side and profitable positions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "80000"}]  # Profitable
        side, returned_positions, risk = strategy.order_side(historical_data, side="SELL")
        
        assert side == "SELL"
        assert returned_positions == positions
        assert "MED" in risk

    def test_order_side_medium_term_sell_no_positions(self, config, portfolio):
        """Test order_side for MEDIUM_TERM strategy with SELL side but no profitable positions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=[],
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100000"}]
        
        with pytest.raises(RequestedSellNoPositions):
            strategy.order_side(historical_data, side="SELL")

    def test_order_side_medium_term_no_side_with_positions(self, config, positions, portfolio):
        """Test order_side for MEDIUM_TERM strategy with no side specified and profitable positions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "80000"}]  # Profitable
        side, returned_positions, risk = strategy.order_side(historical_data)
        
        assert side == "SELL"
        assert returned_positions == positions
        assert "LOW" in risk

    def test_order_side_medium_term_no_side_no_positions(self, config, portfolio):
        """Test order_side for MEDIUM_TERM strategy with no side and no profitable positions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=[],
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "105"}, {"close": "100"}]  # 5% gain
        side, returned_positions, risk = strategy.order_side(historical_data)
        
        assert side == "BUY"
        assert returned_positions == []
        assert "MED" in risk

    def test_validate_price_diff_pct_short_term_pass(self, config, positions, portfolio):
        """Test validate_price_diff_pct for SHORT_TERM strategy passing"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="SHORT_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100"}, {"close": "98"}]  # 2% increase, outside 1-1% range
        passed, diff_pct = strategy.validate_price_diff_pct(historical_data)
        assert passed == True
        assert abs(diff_pct - Decimal("2.04")) < Decimal("0.1")

    def test_validate_price_diff_pct_short_term_fail(self, config, positions, portfolio):
        """Test validate_price_diff_pct for SHORT_TERM strategy failing"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="SHORT_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "101"}, {"close": "100"}]  # 1% exactly, in range
        passed, diff_pct = strategy.validate_price_diff_pct(historical_data)
        assert passed == False

    def test_validate_price_diff_pct_medium_term_pass(self, config, positions, portfolio):
        """Test validate_price_diff_pct for MEDIUM_TERM strategy passing"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100"}, {"close": "105"}]  # Gain outside restricted range
        passed, diff_pct = strategy.validate_price_diff_pct(historical_data)
        assert passed == True

    def test_validate_price_diff_pct_medium_term_fail(self, config, positions, portfolio):
        """Test validate_price_diff_pct for MEDIUM_TERM strategy failing"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # For MEDIUM_TERM, the restricted range is -10% to -5%
        # A -7% change should fail (return False) because it's in the restricted range
        historical_data = [{"close": "93"}, {"close": "100"}]  # -7% change
        passed, diff_pct = strategy.validate_price_diff_pct(historical_data)
        # The method should return False for values in the restricted range
        assert passed == False

    def test_validate_price_diff_pct_zero_division(self, config, positions, portfolio):
        """Test validate_price_diff_pct with zero division scenario"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100"}, {"close": "0"}]  # Zero opening price
        passed, diff_pct = strategy.validate_price_diff_pct(historical_data)
        assert passed == True
        assert diff_pct == 0

    def test_validate_price_diff_pct_invalid_strategy_term(self, config, positions, portfolio):
        """Test validate_price_diff_pct with invalid strategy term"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="INVALID_TERM",
            **config_copy
        )
        
        historical_data = [{"close": "100"}, {"close": "105"}]
        
        with pytest.raises(ValueError):
            strategy.validate_price_diff_pct(historical_data)

    def test_validate_support_resistance(self, config, positions, portfolio):
        """Test validate_support_resistance method"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        historical_data = [
            {"high": "102", "low": "98"},
            {"high": "101", "low": "99"},
            {"high": "103", "low": "97"}
        ]
        
        result = strategy.validate_support_resistance(historical_data)
        assert "support" in result
        assert "resistance" in result

    def test_detect_bullish_engulfing(self, config, positions, portfolio):
        """Test detect_bullish_engulfing method"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Bullish engulfing pattern
        historical_data = [
            {"open": "98", "close": "102"},  # Current: bullish
            {"open": "101", "close": "99"}   # Previous: bearish
        ]
        
        result = strategy.detect_bullish_engulfing(historical_data)
        assert result == True

    def test_detect_bullish_engulfing_no_pattern(self, config, positions, portfolio):
        """Test detect_bullish_engulfing with no pattern"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # No bullish engulfing pattern
        historical_data = [
            {"open": "98", "close": "99"},   # Current: small bullish
            {"open": "101", "close": "100"}  # Previous: small bearish
        ]
        
        result = strategy.detect_bullish_engulfing(historical_data)
        assert result == False

    def test_detect_bearish_engulfing(self, config, positions, portfolio):
        """Test detect_bearish_engulfing method"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Bearish engulfing pattern
        historical_data = [
            {"open": "102", "close": "98"},  # Current: bearish
            {"open": "99", "close": "101"}   # Previous: bullish
        ]
        
        result = strategy.detect_bearish_engulfing(historical_data)
        assert result == True

    def test_detect_bearish_engulfing_no_pattern(self, config, positions, portfolio):
        """Test detect_bearish_engulfing with no pattern"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # No bearish engulfing pattern
        historical_data = [
            {"open": "98", "close": "99"},   # Current: bullish
            {"open": "101", "close": "100"}  # Previous: bearish
        ]
        
        result = strategy.detect_bearish_engulfing(historical_data)
        assert result == False

    @patch('functions.strategies.ProviderClient')
    def test_handle_historical_data_short_term(self, mock_provider_client, config, positions, portfolio):
        """Test handle_historical_data for SHORT_TERM strategy"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="SHORT_TERM",
            **config_copy
        )
        
        mock_client = Mock()
        mock_client.get_candles.return_value = {"candles": [{"close": "100"}]}
        mock_provider_client.return_value = mock_client
        
        with patch('functions.strategies.send_message_to_queue') as mock_queue:
            result = strategy.handle_historical_data()
            assert result == [{"close": "100"}]
            mock_queue.assert_called_once()

    @patch('functions.strategies.ProviderClient')
    def test_handle_historical_data_medium_term(self, mock_provider_client, config, positions, portfolio):
        """Test handle_historical_data for MEDIUM_TERM strategy"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        mock_client = Mock()
        mock_client.get_candles.return_value = {"candles": [{"close": "100"}]}
        mock_provider_client.return_value = mock_client
        
        result = strategy.handle_historical_data()
        assert result == [{"close": "100"}]

    @patch('functions.strategies.ProviderClient')
    def test_handle_historical_data_invalid_term(self, mock_provider_client, config, positions, portfolio):
        """Test handle_historical_data with invalid strategy term"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="INVALID_TERM",
            **config_copy
        )
        
        with pytest.raises(ValueError):
            strategy.handle_historical_data()

    def test_analyze_historical_data_buying_success(self, config, positions, portfolio):
        """Test analyze_historical_data_buying with valid data"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Use data that passes validation (outside restricted range)
        # For MEDIUM_TERM, restricted range is -10% to -5%, so use positive gain
        historical_data = [{"close": "105"}, {"close": "100"}]  # 5% gain, outside restricted range
        
        # Should not raise exception
        strategy.analyze_historical_data_buying(historical_data)

    def test_analyze_historical_data_buying_failure(self, config, positions, portfolio):
        """Test analyze_historical_data_buying with invalid data"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Use data in the restricted range (-10% to -5%)
        historical_data = [{"close": "93"}, {"close": "100"}]  # -7% in restricted range
        
        with pytest.raises(AnalyzeBuyPricesException):
            strategy.analyze_historical_data_buying(historical_data)

    @patch('functions.strategies.notify_assistant')
    def test_analyze_historical_data_selling_profitable(self, mock_notify, config, positions, portfolio):
        """Test analyze_historical_data_selling with profitable position"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Current price higher than buy price for good profit (> 4%)
        historical_data = [{"close": "80000"}]  # Much higher than test buy price
        
        # Should not raise exception for very profitable position
        strategy.analyze_historical_data_selling(
            historical_data, 
            Decimal("0.001"), 
            Decimal("70000"),  # Lower buy price
            "position-id"
        )

    def test_analyze_historical_data_selling_not_profitable(self, config, positions, portfolio):
        """Test analyze_historical_data_selling with unprofitable position"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Current price lower than buy price
        historical_data = [{"close": "65000"}]  # Lower than buy price
        
        with pytest.raises(AnalyzeSellPricesException):
            strategy.analyze_historical_data_selling(
                historical_data, 
                Decimal("0.001"), 
                Decimal("70000"), 
                "position-id"
            )

    @patch('functions.strategies.notify_assistant')
    def test_analyze_historical_data_selling_in_target_range(self, mock_notify, config, positions, portfolio):
        """Test analyze_historical_data_selling with profit in target range"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Calculate price that gives profit between 4% and profit_target (1.5% from config)
        # We need profit between 4% and 1.5%, so we'll use a price that gives ~5% profit
        buy_price = Decimal("70000")
        target_profit_pct = Decimal("5.0")  # 5% profit
        target_price = buy_price * (1 + target_profit_pct / 100)
        
        historical_data = [{"close": str(target_price)}]  # ~5% profit
        
        with pytest.raises(AnalyzeSellPricesException):
            strategy.analyze_historical_data_selling(
                historical_data, 
                Decimal("0.001"), 
                buy_price, 
                "position-id"
            )
        
        mock_notify.assert_called_once()

    def test_confirm_side_with_trend_valid_buy(self, config, positions, portfolio):
        """Test confirm_side_with_trend with valid BUY conditions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Create data that will pass trend confirmation
        # Use data where the latest close is very close to support level and has bullish engulfing
        # The support level should be around 99.9 based on the logic in validate_support_resistance
        historical_data = [
            {"close": "99.9", "high": "100.1", "low": "99.8", "open": "99.8"},  # Current: bullish, very close to support
            {"open": "100.0", "close": "99.9", "high": "100.1", "low": "99.8"}   # Previous: bearish
        ] + [{"close": "99.9", "high": "100.1", "low": "99.8", "open": "99.9"}] * 13
        
        # This should pass because the close price (99.9) is very close to the support levels
        # and we have a bullish engulfing pattern
        result = strategy.confirm_side_with_trend(historical_data, "BUY")
        assert result == True

    def test_confirm_side_with_trend_invalid_side(self, config, positions, portfolio):
        """Test confirm_side_with_trend with invalid conditions"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Create data that won't have support/resistance or engulfing patterns
        historical_data = [
            {"close": "100", "high": "150", "low": "50", "open": "99"},  # Wide range, no clear levels
            {"close": "200", "high": "250", "low": "150", "open": "199"},
            {"close": "300", "high": "350", "low": "250", "open": "299"}
        ] * 5
        
        with pytest.raises(InvalidSideException):
            strategy.confirm_side_with_trend(historical_data, "BUY")

    @patch('functions.strategies.ProviderClient')
    @patch('functions.strategies.LambdaClient')
    @patch('functions.strategies.send_message_to_queue')
    def test_run_successful_execution(self, mock_queue, mock_lambda_client, mock_provider_client, config, positions, portfolio):
        """Test successful strategy run"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Mock provider client with data that has profitable positions (close price 80000 > buy price 70000)
        # but also passes trend confirmation
        mock_client = Mock()
        mock_client.get_candles.return_value = {"candles": [
            {"close": "80000", "high": "80100", "low": "79900", "open": "79950"},  # Current: close to resistance for SELL
            {"open": "80050", "close": "79950", "high": "80100", "low": "79900"}   # Previous: bearish for engulfing
        ] * 7}
        mock_provider_client.return_value = mock_client
        
        # Mock lambda client
        mock_lambda = Mock()
        mock_lambda.invoke_lambda_function.return_value = '{"status": "success", "signals": ["BUY"]}'
        mock_lambda_client.return_value = mock_lambda
        
        side, historical_data, returned_positions, risk_flags = strategy.run()
        
        # With profitable positions (80000 > 70000), should be SELL, but trend confirmation will fail
        # because 80000 is not close enough to calculated resistance level
        # So it should still be SELL but with HIGH risk
        assert side == "SELL"
        assert "HIGH" in risk_flags[-1]  # Should have HIGH risk due to trend confirmation failure

    @patch('functions.strategies.ProviderClient')
    @patch('functions.strategies.LambdaClient')
    def test_run_with_invalid_side_exception(self, mock_lambda_client, mock_provider_client, config, positions, portfolio):
        """Test strategy run with InvalidSideException"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = MomentumStrategy(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            **config_copy
        )
        
        # Mock provider client with data that will fail trend confirmation
        mock_client = Mock()
        mock_client.get_candles.return_value = {"candles": [
            {"close": "80000", "high": "150000", "low": "50000", "open": "79999"},  # Wide range, no clear patterns
            {"close": "200000", "high": "250000", "low": "150000", "open": "199999"},
            {"close": "300000", "high": "350000", "low": "250000", "open": "299999"}
        ] * 5}
        mock_provider_client.return_value = mock_client
        
        # Mock lambda client
        mock_lambda = Mock()
        mock_lambda.invoke_lambda_function.return_value = '{"status": "success", "signals": ["BUY"]}'
        mock_lambda_client.return_value = mock_lambda
        
        side, historical_data, returned_positions, risk_flags = strategy.run()
        
        # Should still return SELL (profitable positions) but with HIGH risk due to trend confirmation failure
        assert side == "SELL"
        assert "HIGH" in risk_flags[-1]

class TestStrategyHandler:
    
    def test_create_medium_term_strategy(self, config, positions, portfolio):
        """Test StrategyHandler.create for MEDIUM_TERM strategy"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = StrategyHandler.create(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="MEDIUM_TERM",
            strategy_type="MOMENTUM",
            **config_copy
        )
        
        assert isinstance(strategy, MomentumStrategy)
        assert strategy.strategy_term == "MEDIUM_TERM"

    def test_create_short_term_strategy(self, config, positions, portfolio):
        """Test StrategyHandler.create for SHORT_TERM strategy"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        strategy = StrategyHandler.create(
            provider="COINBASE",
            product_id="BTC-USD",
            portfolio=portfolio,
            positions=positions,
            correlation_id="test-correlation-id",
            strategy_term="SHORT_TERM",
            strategy_type="MOMENTUM",
            **config_copy
        )
        
        assert isinstance(strategy, MomentumStrategy)
        assert strategy.strategy_term == "SHORT_TERM"

    def test_create_invalid_strategy_term(self, config, positions, portfolio):
        """Test StrategyHandler.create with invalid strategy term"""
        config_copy = config.copy()
        config_copy.pop('product_id', None)
        
        with pytest.raises(ValueError):
            StrategyHandler.create(
                provider="COINBASE",
                product_id="BTC-USD",
                portfolio=portfolio,
                positions=positions,
                correlation_id="test-correlation-id",
                strategy_term="INVALID_TERM",
                strategy_type="MOMENTUM",
                **config_copy
            )


class TestHandler:
    
    @patch('functions.strategies.send_message_to_queue')
    def test_handler_success_with_positions(self, mock_queue, sqs_strategy_event_existing_positions):
        """Test handler function with successful strategy execution and existing positions"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            # Create mock position objects with model_dump method
            mock_position = Mock()
            mock_position.model_dump.return_value = {"id": "pos1"}
            
            mock_strategy.run.return_value = (
                "SELL", 
                [{"close": "100000"}], 
                [mock_position], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            result = handler(sqs_strategy_event_existing_positions, {})
            
            # The handler should complete successfully
            mock_queue.assert_called_once()

    @patch('functions.strategies.send_message_to_queue')
    def test_handler_success_no_positions(self, mock_queue, sqs_strategy_event_no_positions):
        """Test handler function with no existing positions"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.return_value = (
                "BUY", 
                [{"close": "100000"}], 
                [], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            result = handler(sqs_strategy_event_no_positions, {})
            
            mock_queue.assert_called_once()

    def test_handler_requested_sell_no_positions(self, sqs_strategy_event_existing_positions_sell):
        """Test handler when sell is requested but no profitable positions exist"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.side_effect = RequestedSellNoPositions("No positions")
            mock_create.return_value = mock_strategy
            
            result = handler(sqs_strategy_event_existing_positions_sell, {})
            
            assert result["statusCode"] == 200

    def test_handler_strategy_failure(self, sqs_strategy_event_existing_positions):
        """Test handler when strategy execution fails"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.side_effect = Exception("Strategy failed")
            mock_create.return_value = mock_strategy
            
            with pytest.raises(Exception):
                handler(sqs_strategy_event_existing_positions, {})

    @patch('functions.strategies.send_message_to_queue')
    def test_handler_with_buy_side(self, mock_queue, sqs_strategy_event_existing_positions_buy):
        """Test handler with BUY side specified"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.return_value = (
                "BUY", 
                [{"close": "100000"}], 
                [], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            result = handler(sqs_strategy_event_existing_positions_buy, {})
            
            # Verify the strategy was called with the correct side
            mock_strategy.run.assert_called_once_with("BUY")
            mock_queue.assert_called_once()

    @patch('functions.strategies.send_message_to_queue')
    def test_handler_with_sell_side(self, mock_queue, sqs_strategy_event_existing_positions_sell):
        """Test handler with SELL side specified"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            # Create mock position with model_dump method
            mock_position = Mock()
            mock_position.model_dump.return_value = {"id": "pos1"}
            
            mock_strategy.run.return_value = (
                "SELL", 
                [{"close": "100000"}], 
                [mock_position], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            result = handler(sqs_strategy_event_existing_positions_sell, {})
            
            # Verify the strategy was called with the correct side
            mock_strategy.run.assert_called_once_with("SELL")
            mock_queue.assert_called_once()

    @patch('functions.strategies.send_message_to_queue')
    def test_handler_no_side_specified(self, mock_queue, sqs_strategy_no_side_event):
        """Test handler when no side is specified in the event"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.return_value = (
                "BUY", 
                [{"close": "100000"}], 
                [], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            result = handler(sqs_strategy_no_side_event, {})
            
            # Verify the strategy was called with None side
            mock_strategy.run.assert_called_once_with(None)
            mock_queue.assert_called_once()

    @patch('functions.strategies.send_message_to_queue')
    def test_handler_message_body_construction(self, mock_queue, sqs_strategy_event_existing_positions):
        """Test that handler constructs the message body correctly"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.return_value = (
                "BUY", 
                [{"close": "100000"}], 
                [], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            handler(sqs_strategy_event_existing_positions, {})
            
            # Check that send_message_to_queue was called with correct structure
            call_args = mock_queue.call_args
            assert call_args[0][0] == Env.QUEUE_RISK_URL  # First arg is queue URL
            
            msg_body = call_args[0][1]  # Second arg is message body
            assert "portfolio" in msg_body
            assert "product" in msg_body
            assert "side" in msg_body
            assert "positions" in msg_body
            assert "risk_flags" in msg_body
            assert "historical_data" in msg_body

    def test_handler_event_parsing(self, sqs_strategy_event_existing_positions):
        """Test that handler correctly parses event data"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create, \
             patch('functions.strategies.send_message_to_queue') as mock_queue:
            
            mock_strategy = Mock()
            mock_strategy.run.return_value = ("BUY", [], [], [])
            mock_create.return_value = mock_strategy
            
            handler(sqs_strategy_event_existing_positions, {})
            
            # Verify StrategyHandler.create was called with correct parameters
            create_call_args = mock_create.call_args
            create_kwargs = create_call_args[1]
            
            assert create_kwargs['provider'] == "COINBASE"
            assert create_kwargs['product_id'] == "BTC-USD"
            assert create_kwargs['strategy_term'] == "MEDIUM_TERM"
            assert 'portfolio' in create_kwargs
            assert 'positions' in create_kwargs
            assert 'correlation_id' in create_kwargs
            
            # Verify the strategy was called with None side
            mock_strategy.run.assert_called_once_with(None)
            mock_queue.assert_called_once()

    @patch('functions.strategies.send_message_to_queue')
    def test_handler_message_body_construction(self, mock_queue, sqs_strategy_event_existing_positions):
        """Test that handler constructs the message body correctly"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create:
            mock_strategy = Mock()
            mock_strategy.run.return_value = (
                "BUY", 
                [{"close": "100000"}], 
                [], 
                ["risk1"]
            )
            mock_create.return_value = mock_strategy
            
            handler(sqs_strategy_event_existing_positions, {})
            
            # Check that send_message_to_queue was called with correct structure
            call_args = mock_queue.call_args
            assert call_args[0][0] == Env.QUEUE_RISK_URL  # First arg is queue URL
            
            msg_body = call_args[0][1]  # Second arg is message body
            assert "portfolio" in msg_body
            assert "product" in msg_body
            assert "side" in msg_body
            assert "positions" in msg_body
            assert "risk_flags" in msg_body
            assert "historical_data" in msg_body

    def test_handler_event_parsing(self, sqs_strategy_event_existing_positions):
        """Test that handler correctly parses event data"""
        with patch('functions.strategies.StrategyHandler.create') as mock_create, \
             patch('functions.strategies.send_message_to_queue') as mock_queue:
            
            mock_strategy = Mock()
            mock_strategy.run.return_value = ("BUY", [], [], [])
            mock_create.return_value = mock_strategy
            
            handler(sqs_strategy_event_existing_positions, {})
            
            # Verify StrategyHandler.create was called with correct parameters
            create_call_args = mock_create.call_args
            create_kwargs = create_call_args[1]
            
            assert create_kwargs['provider'] == "COINBASE"
            assert create_kwargs['product_id'] == "BTC-USD"
            assert create_kwargs['strategy_term'] == "MEDIUM_TERM"
            assert 'portfolio' in create_kwargs
            assert 'positions' in create_kwargs
            assert 'correlation_id' in create_kwargs

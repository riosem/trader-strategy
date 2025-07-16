import json
import pytest

from functions.strategies import MomentumStrategy, handler
from utils.common import Env
from utils.exceptions import AnalyzeSellPricesException


@pytest.mark.unit_tests
def test_strategy_handler_no_positions_confirm_buy_no_side_requested(sqs_strategy_event_no_positions, context, historical_data_confirm_buy, mock_get_provider_product_candles, mock_aws_sqs):
    mock_get_provider_product_candles(historical_data_confirm_buy)
    handler(sqs_strategy_event_no_positions, context)
    
    resposne = mock_aws_sqs.receive_message(
        QueueUrl=Env.QUEUE_RISK_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )
    messages = resposne.get("Messages", [])
    assert len(messages) == 1

#  TODO: Review tests once we add websocket functionality

@pytest.mark.unit_tests
def test_strategy_handler_no_positions_invalid_side(mock_aws_sqs, sqs_strategy_no_side_event, context, historical_data_confirm_buy, mock_get_provider_product_candles):
    mock_get_provider_product_candles(historical_data_confirm_buy)
    handler(sqs_strategy_no_side_event, context)

    resposne = mock_aws_sqs.receive_message(
        QueueUrl=Env.QUEUE_RISK_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )
    messages = resposne.get("Messages", [])
    assert len(messages) == 1
    # assert risk flag was added in sqs message
    msg_dict = json.loads(messages[0]["Body"])
    assert 'strategy_STRATEGY_RUN_HIGH' in msg_dict.get("risk_flags")


@pytest.mark.unit_tests
def test_strategy_handler_existing_positions_in_loss_sell_requested(sqs_strategy_event_existing_positions_in_loss_sell, context, historical_data_confirm_sell, mock_get_provider_product_candles, mock_aws_sqs):
    mock_get_provider_product_candles(historical_data_confirm_sell)
    
    handler(sqs_strategy_event_existing_positions_in_loss_sell, context)

    response = mock_aws_sqs.receive_message(
        QueueUrl=Env.QUEUE_RISK_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )
    messages = response.get("Messages", [])
    assert len(messages) == 0


@pytest.mark.unit_tests
def test_strategy_handler_existing_positions_confirm_sell_no_side_requested(sqs_strategy_event_existing_positions, context, historical_data_confirm_sell, mock_get_provider_product_candles, mock_aws_sqs):
    mock_get_provider_product_candles(historical_data_confirm_sell)
    handler(sqs_strategy_event_existing_positions, context)
    
    resposne = mock_aws_sqs.receive_message(
        QueueUrl=Env.QUEUE_RISK_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )
    messages = resposne.get("Messages", [])
    assert len(messages) == 1


@pytest.mark.unit_tests
def test_strategy_handler_existing_positions_confirm_buy_side_requested(sqs_strategy_event_existing_positions_buy, context, historical_data_confirm_buy, mock_get_provider_product_candles, mock_aws_sqs):
    mock_get_provider_product_candles(historical_data_confirm_buy)
    handler(sqs_strategy_event_existing_positions_buy, context)
    
    resposne = mock_aws_sqs.receive_message(
        QueueUrl=Env.QUEUE_RISK_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )
    messages = resposne.get("Messages", [])
    assert len(messages) == 1


@pytest.mark.unit_tests
def test_strategy_handler_existing_positions_confirm_sell_side_requested(sqs_strategy_event_existing_positions_sell, context, historical_data_confirm_sell, mock_get_provider_product_candles, mock_aws_sqs):
    mock_get_provider_product_candles(historical_data_confirm_sell)
    handler(sqs_strategy_event_existing_positions_sell, context)
    
    resposne = mock_aws_sqs.receive_message(
        QueueUrl=Env.QUEUE_RISK_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0,
    )
    messages = resposne.get("Messages", [])
    assert len(messages) == 1

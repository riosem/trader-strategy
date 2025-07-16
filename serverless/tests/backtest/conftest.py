import boto3
import pytest
import os

from utils.common import Env


@pytest.fixture()
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_REGION"] = Env.REGION
    os.environ["AWS_DEFAULT_REGION"] = Env.REGION


@pytest.fixture(autouse=True)
def mock_aws_sqs(aws_credentials):
    from moto import mock_aws

    with mock_aws():
        conn = boto3.client("sqs", Env.REGION)
        conn.create_queue(QueueName="analyze.fifo", Attributes={"FifoQueue": "true"})
        conn.create_queue(QueueName="assets.fifo", Attributes={"FifoQueue": "true"})
        conn.create_queue(QueueName="profits.fifo", Attributes={"FifoQueue": "true"})
        conn.create_queue(QueueName="orders.fifo", Attributes={"FifoQueue": "true"})
        conn.create_queue(
            QueueName="post-product.fifo", Attributes={"FifoQueue": "true"}
        )
        conn.create_queue(QueueName="post-order.fifo", Attributes={"FifoQueue": "true"})
        conn.create_queue(QueueName="market.fifo", Attributes={"FifoQueue": "true"})
        conn.create_queue(QueueName="data-collection-queue")

        yield conn


@pytest.fixture(autouse=True)
def mock_aws_dynamo(aws_credentials):
    from moto import mock_aws

    with mock_aws():
        conn = boto3.resource("dynamodb", Env.REGION)
        conn.create_table(
            TableName="cache",
            KeySchema=[
                {"AttributeName": "cache_key", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "cache_key", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        yield conn


@pytest.fixture(autouse=True)
def mock_aws_scheduler(aws_credentials):
    from moto import mock_aws

    with mock_aws():
        conn = boto3.client("scheduler", Env.REGION)
        yield conn


@pytest.fixture
def product_id():
    return "BTC-USD"


@pytest.fixture
def source_portfolio_uuid():
    return Env.SOURCE_PORTFOLIO_ID


@pytest.fixture
def target_portfolio_uuid():
    return Env.TARGET_PORTFOLIO_ID


@pytest.fixture
def provider_url():
    return Env.PROVIDER_URL


@pytest.fixture
def simulator_url():
    return Env.SIMULATOR_URL


@pytest.fixture
def portfolio_balance():
    return "1000.00"


@pytest.fixture
def portfolio_asset():
    return "USD"


@pytest.fixture
def product(product_id):
    return {
        "product_id": product_id,
        "price": "58382.78",
        "price_percentage_change_24h": "-4.23785541063979",
        "volume_24h": "12900.84201012",
        "volume_percentage_change_24h": "15.2934477676346",
        "base_increment": "0.00000001",
        "quote_increment": "0.01",
        "quote_min_size": "1",
        "quote_max_size": "150000000",
        "base_min_size": "0.00000001",
        "base_max_size": "3400",
        "base_name": "Bitcoin",
        "quote_name": "USDC",
        "watched": False,
        "is_disabled": False,
        "new": False,
        "status": "online",
        "cancel_only": False,
        "limit_only": False,
        "post_only": False,
        "trading_disabled": False,
        "auction_mode": False,
        "product_type": "SPOT",
        "quote_currency_id": "USDC",
        "base_currency_id": "BTC",
        "fcm_trading_session_details": None,
        "mid_market_price": "",
        "alias": "BTC-USD",
        "alias_to": [],
        "base_display_symbol": "BTC",
        "quote_display_symbol": "USD",
        "view_only": False,
        "price_increment": "0.01",
        "display_name": "BTC-USDC",
        "product_venue": "CBE",
        "approximate_quote_24h_volume": "753187020.89",
    }


@pytest.fixture
def config_response(status, product_id, is_disabled, order_configuration):
    return {
        "config": {
            "product_id": product_id,
            "price": "58382.78",
            "price_percentage_change_24h": "-4.23785541063979",
            "volume_24h": "12900.84201012",
            "volume_percentage_change_24h": "15.2934477676346",
            "base_increment": "0.00000001",
            "quote_increment": "0.01",
            "quote_min_size": "1",
            "quote_max_size": "150000000",
            "base_min_size": "0.00000001",
            "base_max_size": "3400",
            "base_name": "Bitcoin",
            "quote_name": "USDC",
            "watched": False,
            "is_disabled": is_disabled,
            "new": False,
            "status": status,
            "cancel_only": False,
            "limit_only": False,
            "post_only": False,
            "trading_disabled": False,
            "auction_mode": False,
            "product_type": "SPOT",
            "quote_currency_id": "USDC",
            "base_currency_id": "BTC",
            "fcm_trading_session_details": None,
            "mid_market_price": "",
            "alias": "BTC-USD",
            "alias_to": [],
            "base_display_symbol": "BTC",
            "quote_display_symbol": "USD",
            "view_only": False,
            "price_increment": "0.01",
            "display_name": "BTC-USDC",
            "product_venue": "CBE",
            "approximate_quote_24h_volume": "753187020.89",
            "config_quote_min_size": "1.00",
            "config_quote_max_size": "1.00",
            "maxmin_pct_threshold": "1.5",
            "profit_target": "1.5",
            "toggle": True,
        }
    }


@pytest.fixture
def config(config_response):
    return config_response["config"]


@pytest.fixture
def is_disabled():
    return False


@pytest.fixture
def status():
    return "online"


@pytest.fixture
def state():
    return "ENABLED"


@pytest.fixture
def provider():
    return "COINBASE"


@pytest.fixture()
def context():
    return {}


@pytest.fixture
def correlation_id():
    return "correlation-id"


@pytest.fixture
def portfolio_balance():
    return "1000.00"


@pytest.fixture
def provider_order_id():
    return "provider-order-id"


@pytest.fixture
def epoch_order_id():
    return "epoch-order-id"


@pytest.fixture
def service_id(epoch_order_id):
    return f"ORDERS:{epoch_order_id}"


@pytest.fixture
def total_value_after_fees():
    return 2


@pytest.fixture
def at_price():
    return "1.00"


@pytest.fixture
def base_size():
    return "1.00"


@pytest.fixture
def quote_size():
    return "1.00"


@pytest.fixture
def last_order_status():
    return "FILLED"


@pytest.fixture
def last_order_at_price():
    return "0.90"


@pytest.fixture
def last_order_total_value_after_fees():
    return "0.90"


@pytest.fixture
def last_order_size():
    return "1.00"


@pytest.fixture
def last_order_filled_size():
    return "1.00"


@pytest.fixture
def last_order_price():
    return "1.00"


@pytest.fixture
def last_order_id():
    return "30dlK03l-930c-415a-9d6e-ijk83msse"


@pytest.fixture
def last_order_user_id():
    return "user-id"


@pytest.fixture
def last_order_side():
    return "BUY"


@pytest.fixture
def last_order_client_order_id():
    return "client-order-id"


@pytest.fixture
def last_order_service_id(last_epoch_order_id):
    return f"ORDERS:{last_epoch_order_id}"


@pytest.fixture
def last_epoch_order_id():
    return "last-epoch-order-id"


@pytest.fixture
def last_order_created_time():
    return "2024-08-15T02:54:47.931547+00:00"


@pytest.fixture
def created_time():
    return "2024-08-15T02:59:47.931547+00:00"


@pytest.fixture
def last_order(
    last_order_total_value_after_fees,
    last_order_price,
    last_order_at_price,
    last_order_size,
    last_order_filled_size,
    last_order_status,
    last_order_service_id,
    last_order_side,
    last_order_created_time,
):
    return {
        "id": "order_id",
        "status": last_order_status,
        "price": last_order_price,
        "size": last_order_size,
        "service_id": last_order_service_id,
        "total_value_after_fees": last_order_total_value_after_fees,
        "side": last_order_side,
        "average_filled_price": last_order_at_price,
        "filled_size": last_order_filled_size,
        "created_time": last_order_created_time,
    }


@pytest.fixture
def order_configuration(quote_size, base_size):
    return {
        "market_market_ioc": {
            "quote_size": quote_size,
            "base_size": base_size,
        }
    }


@pytest.fixture
def order(
    service_id,
    # average_filled_price,
    # filled_size,
    # order_id,
    order_configuration,
    status,
    total_value_after_fees,
    created_time,
):
    return {
        # "order_id": order_id,
        "status": status,
        "service_id": service_id,
        "side": "BUY",
        # "average_filled_price": average_filled_price,
        # "filled_size": filled_size,
        "order_configuration": order_configuration,
        "total_value_after_fees": total_value_after_fees,
        "created_time": created_time,
    }


@pytest.fixture
def get_ticker_response():
    return {
        "trades": [
            {
                "trade_id": 20153558,
                "price": "100000.00",
                "size": "0.01000000",
                "time": "2015-02-06T20:50:02.000000Z",
                "bid": "100000.00",
                "ask": "100000.00",
                "volume": "0.01000000",
            }
        ]
    }


@pytest.fixture()
def get_product_response(is_disabled, status, product_id):
    return {
        "id": "f8c9efa6-748d-4f02-9a9d-b108149d0bb5",
        "created": "2024-04-10T16:04:23.158274Z",
        "updated": "2024-04-10T16:04:23.158283Z",
        "enabled": False,
        "product_id": product_id,
        "price": "1.625",
        "price_percentage_change_24h": "-7.354618",
        "volume_24h": "47513.2",
        "volume_percentage_change_24h": "81.89481",
        "base_increment": "0.01",
        "quote_increment": "0.001",
        "quote_min_size": "1",
        "quote_max_size": "10000000",
        "base_min_size": "0.4",
        "base_max_size": "4000000",
        "base_name": "Echelon",
        "quote_name": "USD Coin",
        "watched": False,
        "is_disabled": is_disabled,
        "new": False,
        "status": status,
        "cancel_only": False,
        "limit_only": False,
        "post_only": False,
        "trading_disabled": False,
        "auction_mode": False,
        "product_type": "SPOT",
        "quote_currency_id": "USDC",
        "base_currency_id": "PRIME",
        "fcm_trading_session_details": None,
        "mid_market_price": "1.625",
        "alias": "PRIME-USD",
        "alias_to": "test",
        "base_display_symbol": "PRIME",
        "quote_display_symbol": "USD",
        "view_only": False,
        "price_increment": "0.001",
    }


@pytest.fixture
def order_type():
    return "market_market_ioc"


@pytest.fixture
def mock_assistant_notifications(requests_mock):
    return requests_mock.post(
        "https://assistant-url.com/notifications",
        json="Success",
        status_code=200,
    )


@pytest.fixture
def mock_assistant_notifications_500_error(requests_mock):
    return requests_mock.post(
        "https://assistant-url.com/notifications",
        json={"message": "Internal Server Error"},
        status_code=500,
    )


@pytest.fixture
def mock_assistant_notifications_timeout_error(requests_mock):
    from requests.exceptions import Timeout

    return requests_mock.post(
        "https://assistant-url.com/notifications",
        exc=Timeout("Timeout error"),
    )


@pytest.fixture
def mock_provider_get_order(requests_mock, provider_order_id, order):
    return requests_mock.get(
        f"{Env.PROVIDER_URL}/api/v3/brokerage/orders/historical/{provider_order_id}",
        status_code=200,
        json={"order": order},
    )


@pytest.fixture()
def mock_provider_get_order_404_error(requests_mock, provider_order_id):
    return requests_mock.get(
        f"{Env.PROVIDER_URL}/api/v3/brokerage/orders/historical/{provider_order_id}",
        status_code=404,
        json={"message": "Order not found"},
    )


@pytest.fixture
def mock_provider_get_order_timeout_error(requests_mock, provider_order_id):
    return requests_mock.get(
        f"{Env.PROVIDER_URL}/api/v3/brokerage/orders/historical/{provider_order_id}",
        exc=TimeoutError,
    )


@pytest.fixture(autouse=True)
def mock_post_oauth_token_success(requests_mock):
    url = Env.AUTH0_OAUTH_URL
    return requests_mock.post(
        url,
        json={"access_token": "test_access_token"},
        status_code=200,
    )


@pytest.fixture
def mock_post_oauth_token_400_error(requests_mock):
    url = Env.AUTH0_OAUTH_URL
    return requests_mock.post(
        url,
        json={"message": "Bad Request"},
        status_code=400,
    )


@pytest.fixture
def mock_post_oauth_token_timeout_error(requests_mock):
    url = Env.AUTH0_OAUTH_URL
    return requests_mock.post(
        url,
        exc=TimeoutError,
    )

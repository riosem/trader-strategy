import os
import boto3
import decimal
import json
import time

from ulid import ULID
from enum import Enum


class Env:
    QUEUE_MARKET_URL = os.environ.get("QUEUE_MARKET_URL")
    QUEUE_ORDER_URL = os.environ.get("QUEUE_ORDER_URL")
    PROVIDER_URL = os.environ.get("PROVIDER_URL")
    PROVIDER_API_KEY = os.environ.get("PROVIDER_API_KEY")
    AUTH0_PROVIDERS_CLIENT_ID = os.environ.get("AUTH0_PROVIDERS_CLIENT_ID")
    AUTH0_PROVIDERS_CLIENT_SECRET = os.environ.get("AUTH0_PROVIDERS_CLIENT_SECRET")
    AUTH0_PROVIDERS_AUDIENCE = os.environ.get("AUTH0_PROVIDERS_AUDIENCE")
    CACHE_TABLE_NAME = os.environ.get("CACHE_TABLE_NAME")
    REGION = os.environ.get("REGION")
    SIMULATOR_URL = os.environ.get("SIMULATOR_URL")
    SIMULATOR_LAMBDA = os.environ.get("SIMULATOR_LAMBDA_NAME")
    TA_INDICATORS_LAMBDA = os.environ.get("TA_INDICATORS_LAMBDA_NAME")
    QUEUE_DATA_COLLECTION_URL = os.environ.get("QUEUE_DATA_COLLECTION_URL")
    AUTH0_OAUTH_URL = os.environ.get("AUTH0_OAUTH_URL")
    QUEUE_RISK_URL = os.environ.get("QUEUE_RISK_URL")
    AUTH0_ASSISTANT_AUDIENCE = os.environ.get(
        "AUTH0_ASSISTANT_AUDIENCE"
    )
    AUTH0_ASSISTANT_CLIENT_ID = os.environ.get(
        "AUTH0_ASSISTANT_CLIENT_ID"
    )
    AUTH0_ASSISTANT_CLIENT_SECRET = os.environ.get(
        "AUTH0_ASSISTANT_CLIENT_SECRET"
    )
    ASSISTANT_API_KEY = os.environ.get(
        "ASSISTANT_API_KEY"
    )


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def send_message_to_queue(
    queue_url: str, message_body: dict, msg_group_id=str(ULID()), msg_attrs={}
):
    sqs = boto3.client("sqs", Env.REGION)

    options = {
        "QueueUrl": queue_url,
        "MessageBody": json.dumps(message_body, cls=DecimalEncoder),
        # "MessageGroupId": msg_group_id,
        # "MessageDeduplicationId": str(ULID()),
        "MessageAttributes": msg_attrs,
    }

    if queue_url.endswith("fifo"):
        options["MessageGroupId"] = msg_group_id
        options["MessageDeduplicationId"] = str(ULID())

    sqs.send_message(**options)


class CoinbaseApiResponseMessages:
    # 500 responses from Coinbase API
    SOMETHING_WENT_WRONG = "Something went wrong"
    ORDERBOOK_LIMIT_ONLY = (
        "Orderbook is in limit only mode - please use limit order type"
    )

    # Error messages from 200 responses
    INVALID_SIZE_PRECISION = "INVALID_SIZE_PRECISION"


ASSISTANT_NOTIFICATION_MESSAGE = (
"""```***NEAR_PROFIT_TARGET_ALERT***
Provider: {provider}
Product: {product_id}
Strategy: {strategy_term}
Profit %: {profit_pct}
Size: {size}
CurrentPrice: {current_price}
BoughtPrice: {at_price}
Profit%: {profit_pct}
Profit($): {profit_amt_dlrs}
CurrentValue: {current_amt}
BoughtValue: {bought_amt}
PositionID: {position_id}
```"""
)

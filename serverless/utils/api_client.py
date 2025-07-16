import requests

from utils.common import Env
from utils.logger import logger

from utils.exceptions import (
    GetProviderCandlesException,
)
from requests.exceptions import RequestException
from utils.oauth import generate_oauth_token


class ProviderClient:
    domain = Env.PROVIDER_URL

    def __init__(self, **kwargs):
        self.correlation_id = kwargs.get("correlation_id")
        self.product_id = kwargs.get("product_id")
        self.operation = kwargs.get("operation")
        self.headers = self._generate_headers()

    def _generate_headers(self):
        oauth_token = generate_oauth_token(
            Env.AUTH0_PROVIDERS_CLIENT_ID,
            Env.AUTH0_PROVIDERS_CLIENT_SECRET,
            Env.PROVIDER_URL,
        )
        return {
            "Content-Type": "application/json",
            "x-correlation-id": self.correlation_id,
            "x-api-key": Env.PROVIDER_API_KEY,
            "Authorization": f"Bearer {oauth_token}",
        }

    def get_candles(self, product_id: str, granularity: int, start: int, end: int):
        endpoint = f"api/v3/brokerage/products/{product_id}/candles"
        params = {
            "granularity": granularity,
            "start": start,
            "end": end,
        }
        try:
            resp = requests.get(
                f"{self.domain}/{endpoint}", headers=self.headers, params=params
            )
        except RequestException as e:
            logger.error(str(e))
            raise GetProviderCandlesException(str(e))

        if resp.status_code > 200:
            logger.error(
                "BAD_RESPONSE_GET_CANDLES",
                response=resp.text,
                status_code=resp.status_code,
                request_url=f"{self.domain}/{endpoint}",
                correlation_id=self.correlation_id,
                operation=self.operation,
            )
            raise GetProviderCandlesException("Error getting candles")

        return resp.json()



class AssistantSendMessageException(Exception):
    def __init__(self, message="Unexcpected error sending message to assistant"):
        self.message = message
        self.code = 500

class AssistantClient:
    domain = Env.AUTH0_ASSISTANT_AUDIENCE

    def __init__(self, **kwargs):
        self.correlation_id = kwargs.get("correlation_id")
        self.headers = self._generate_headers()

    def _generate_headers(self):
        oauth_token = generate_oauth_token(
            Env.AUTH0_ASSISTANT_CLIENT_ID,
            Env.AUTH0_ASSISTANT_CLIENT_SECRET,
            Env.AUTH0_ASSISTANT_AUDIENCE,
        )
        return {
            "Content-Type": "application/json",
            "x-correlation-id": self.correlation_id,
            "x-api-key": Env.ASSISTANT_API_KEY,
            "Authorization": f"Bearer {oauth_token}",
        }

    def send_message(self, message: str, channel: str):
        endpoint = "/notifications"
        payload = {
            "message": message,
            "webhook_channel": channel,
        }

        try:
            resp = requests.post(
                f"{self.domain}{endpoint}",
                headers=self.headers,
                json=payload,
            )
        except RequestException as e:
            raise AssistantSendMessageException(str(e))

        return resp.json()


def notify_assistant(correlation_id, message):
    assistant_client = AssistantClient(correlation_id=correlation_id)

    try:
        assistant_client.send_message(message=message, channel="general")
    except AssistantSendMessageException as e:
        logger.error(
            "SEND_ASSISTANT_MESSAGE_EXCEPTION",
            message="Could not send message to assistant",
            error=str(e),
        )
        raise e
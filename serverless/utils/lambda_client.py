import boto3

from utils.common import Env
from utils.logger import logger


class LambdaClient:
    def __init__(self, correlation_id=None):
        self.correlation_id = correlation_id
        self.region = Env.REGION
        self.client = self.get_lambda_client()

    def get_lambda_client(self):
        """
        Returns a boto3 Lambda client with the default configuration.
        """
        self.function_name = Env.SIMULATOR_LAMBDA if "SIMLAMBDA" in self.correlation_id else Env.TA_INDICATORS_LAMBDA
        return boto3.client('lambda', region_name=self.region)  # Adjust region as necessary


    def invoke_lambda_function(self, payload):
        """
        Invokes a Lambda function with the given payload.

        :param function_name: Name of the Lambda function to invoke.
        :param payload: The payload to send to the Lambda function.
        :return: The response from the Lambda function.
        """
        try:
            response = self.client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=payload
            )
        except Exception as e:
            raise e
        
        return response['Payload'].read().decode('utf-8')

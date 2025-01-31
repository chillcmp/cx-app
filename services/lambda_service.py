import json

import boto3

from config import AppConfig


class LambdaService:

    def __init__(self):
        self.lambda_client = boto3.client("lambda", AppConfig.REGION)
        self.lambda_name = AppConfig.LAMBDA_ARN

    def invoke(self):
        response = self.lambda_client.invoke(
            FunctionName=self.lambda_name,
            InvocationType="RequestResponse",
            Payload = json.dumps({"detail-type": "Web Application Request"})
        )
        decoded_response = response["Payload"].read().decode("utf-8")
        parsed_response = json.loads(decoded_response)
        body = json.loads(parsed_response['body'])
        return body

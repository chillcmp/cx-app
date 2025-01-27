import json

import boto3

from config import AppConfig
from models.image_metadata import ImageMetadata


class QueueService:

    def __init__(self):
        self.sqs = boto3.resource('sqs', AppConfig.REGION)
        self.queue_url = AppConfig.QUEUE_URL

    def send_image_uploaded_message(self, metadata: ImageMetadata):
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(metadata.to_dict())
        )

    def get_all_messages(self):
        queue = self.sqs.Queue(self.queue_url)
        return queue.receive_messages(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

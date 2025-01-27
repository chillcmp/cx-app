import json

import boto3

from config import AppConfig
from models.image_metadata import ImageMetadata


class QueueService:

    def __init__(self):
        self.queue_url = AppConfig.QUEUE_URL
        self.queue = boto3.resource('sqs', AppConfig.REGION).Queue(self.queue_url)

    def send_image_uploaded_message(self, metadata: ImageMetadata):
        self.queue.send_message(MessageBody=json.dumps(metadata.to_dict()))

    def get_all_messages(self):
        return self.queue.receive_messages(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

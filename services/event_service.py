import json

import boto3

from config import AppConfig
from models.image_metadata import ImageMetadata


class EventService:

    def __init__(self):
        self.sqs = boto3.client('sqs', AppConfig.REGION)
        self.queue_url = AppConfig.QUEUE_URL

    def send_image_uploaded_message(self, metadata: ImageMetadata):
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(metadata.to_dict())
        )

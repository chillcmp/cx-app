import os
from datetime import datetime, timedelta

import boto3

from config import AppConfig


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AppConfig.ALLOWED_EXTENSIONS


class ImageService:

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.presigned_url_lifetime_s = AppConfig.PRESIGNED_URL_LIFETIME_S
        self.urls_cache = {}

    def upload_image(self, image):
        self.s3_client.upload_fileobj(image, self.bucket_name, image.filename)

    def delete_image(self, image_name):
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=image_name)

    def get_presigned_url_for_image(self, image_name):
        if image_name not in self.urls_cache or self.urls_cache[image_name]['expiration'] <= datetime.now():
            presigned_url = self._create_and_store_presigned_url(image_name)
        else:
            presigned_url = self.urls_cache[image_name]['url']
        return presigned_url

    def get_images(self):
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)

        images = []
        for obj in response.get('Contents', []):
            object_name = obj['Key']
            if not allowed_file(object_name):
                continue
            presigned_url = self.get_presigned_url_for_image(object_name)
            images.append((object_name, presigned_url))

        return images

    def _create_and_store_presigned_url(self, object_name):
        expiration_time = datetime.now() + timedelta(seconds=self.presigned_url_lifetime_s)
        presigned_url = self.s3_client.generate_presigned_url('get_object',
                                                              Params={'Bucket': self.bucket_name, 'Key': object_name},
                                                              ExpiresIn=self.presigned_url_lifetime_s)
        self.urls_cache[object_name] = {'url': presigned_url, 'expiration': expiration_time}
        return presigned_url


def get_metadata_str(file_path):
    modified_timestamp = os.path.getmtime(file_path)
    modified_datetime = datetime.fromtimestamp(modified_timestamp)

    metadata = {'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'modified_time': modified_datetime.strftime('%Y-%m-%d'),
                'extension': os.path.splitext(file_path)[1]}
    metadata_str = '\n'.join(f'{key}: {value}' for key, value in metadata.items())
    return metadata_str

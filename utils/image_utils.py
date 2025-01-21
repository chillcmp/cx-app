import os
from datetime import datetime

from config import AppConfig


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AppConfig.ALLOWED_EXTENSIONS


def get_uploaded_images():
    images = os.listdir(AppConfig.UPLOAD_FOLDER)
    return [file for file in images if allowed_file(file)]


def get_metadata_str(file_path):
    modified_timestamp = os.path.getmtime(file_path)
    modified_datetime = datetime.fromtimestamp(modified_timestamp)

    metadata = {'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'modified_time': modified_datetime.strftime('%Y-%m-%d'),
                'extension': os.path.splitext(file_path)[1]}
    metadata_str = '\n'.join(f'{key}: {value}' for key, value in metadata.items())
    return metadata_str

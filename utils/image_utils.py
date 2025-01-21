import os

from config import AppConfig


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AppConfig.ALLOWED_EXTENSIONS


def get_uploaded_images():
    images = os.listdir(AppConfig.UPLOAD_FOLDER)
    return [file for file in images if allowed_file(file)]

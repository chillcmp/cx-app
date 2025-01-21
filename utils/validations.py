import os

from flask import request
from functools import wraps

from config import AppConfig
from utils.image_utils import allowed_file


def check_file_in_post_request(view_func):
    @wraps(view_func)
    def wrapped_view(**kwargs):
        file = request.files.get('file')
        filename = file.filename if file else request.form.get('filename', '')
        if filename == '':
            kwargs["error"] = 'No selected file'

        return view_func(**kwargs)

    return wrapped_view


def check_file_in_get_request(view_func):
    @wraps(view_func)
    def wrapped_view(**kwargs):
        file = request.args.get('filename')
        images = os.listdir(AppConfig.UPLOAD_FOLDER)
        images = [file for file in images if allowed_file(file)]

        if file == '':
            kwargs["error"] = 'No selected file'
        elif file not in images:
            kwargs["error"] = 'Unknown file'

        return view_func(**kwargs)

    return wrapped_view

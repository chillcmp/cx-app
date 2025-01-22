import os
import random
from io import BytesIO

import requests
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, send_file

from config import AppConfig
from utils.az_utils import get_region_and_az
from utils.image_utils import ImageService, get_metadata_str
from utils.validations import check_file_in_post_request, check_file_in_get_request

app = Flask(__name__)
app.config.from_object(AppConfig)
image_service = ImageService()


@app.route('/')
def index():
    images = image_service.get_images()
    region_and_az = get_region_and_az()
    return render_template('index.html', images=images, region_and_az=region_and_az)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)


@app.route('/upload', methods=['POST'])
@check_file_in_post_request
def upload_file(error: str = None):
    if error:
        return redirect(url_for('index', upload_error=error))

    image = request.files['file']
    image_service.upload_image(image)
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
@check_file_in_post_request
def delete_file(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    image_name = request.form['filename']
    image_service.delete_image(image_name)
    return redirect(url_for('index'))


@app.route('/download', methods=['GET'])
@check_file_in_get_request
def download_file(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    image_name = request.args.get('filename')
    image_url = image_service.get_presigned_url_for_image(image_name)
    response = requests.get(image_url)

    file_stream = BytesIO(response.content)
    file_stream.seek(0)

    return send_file(file_stream, as_attachment=True, download_name=image_name)


@app.route('/metadata', methods=['GET'])
@check_file_in_get_request
def show_metadata(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    filename = request.args.get('filename')
    file_path = os.path.join(AppConfig.UPLOAD_FOLDER, filename)
    metadata_str = get_metadata_str(file_path)
    return redirect(url_for('index', metadata=metadata_str))


@app.route('/random-metadata', methods=['GET'])
def random_metadata(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    images = image_service.get_images()
    random_image = random.choice(images)
    file_path = os.path.join(AppConfig.UPLOAD_FOLDER, random_image)
    metadata_str = get_metadata_str(file_path)
    return redirect(url_for('index', metadata=metadata_str))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

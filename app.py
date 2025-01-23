from io import BytesIO

import pymysql
import requests
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, send_file

from config import AppConfig
from extensions.database import db
from services.image_service import ImageService
from services.metadata_service import MetadataService
from utils.az_utils import get_region_and_az
from utils.validations import check_file_in_post_request

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(AppConfig)
db.init_app(app)

image_service = ImageService()
metadata_service = MetadataService()


with app.app_context():
    db.create_all()


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
    metadata_service.write_metadata(image)
    image_service.upload_image(image)
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_file(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    image_name = request.form['filename']
    metadata_service.delete_metadata(image_name)
    image_service.delete_image(image_name)
    return redirect(url_for('index'))


@app.route('/download', methods=['GET'])
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
def show_metadata():
    image_name = request.args.get('filename')
    metadata = metadata_service.get_metadata(image_name)
    if metadata:
        return redirect(url_for('index', metadata=metadata.to_str()))
    else:
        return redirect(url_for('index', action_error='Unknown file'))


@app.route('/random-metadata', methods=['GET'])
def random_metadata():
    metadata = metadata_service.get_random_metadata()
    if metadata:
        return redirect(url_for('index', metadata=metadata.to_str()))
    else:
        return redirect(url_for('index', action_error='No pets in gallery :('))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

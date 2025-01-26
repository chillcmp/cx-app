from io import BytesIO

import pymysql
import requests
from botocore.exceptions import ClientError
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, send_file

from config import AppConfig
from extensions.database import db
from services.image_service import ImageService
from services.metadata_service import MetadataService
from services.subscription_service import SubscriptionService
from utils.az_utils import get_region_and_az

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(AppConfig)
db.init_app(app)

image_service = ImageService()
metadata_service = MetadataService()
subscription_service = SubscriptionService()

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
def upload_file():
    image = request.files['file']
    if not image:
        return redirect(url_for('index', upload_error='No selected file'))

    metadata_service.write_metadata(image)
    image_service.upload_image(image)
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_file():
    image_name = request.form['filename']
    if image_name == '':
        return redirect(url_for('index', action_error='No selected file'))

    metadata_service.delete_metadata(image_name)
    image_service.delete_image(image_name)
    return redirect(url_for('index'))


@app.route('/download', methods=['GET'])
def download_file():
    image_name = request.args.get('filename')
    if image_name == '':
        return redirect(url_for('index', action_error='No selected file'))

    try:
        image_url = image_service.get_presigned_url_for_image(image_name)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            error = f'File {image_name} does not exist'
        else:
            error = f'Error receiving the object: {e}'
        return redirect(url_for('index', action_error=error))

    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        error = "Timeout expired"
    except requests.exceptions.ConnectionError:
        error = "Server connection error"
    except requests.exceptions.HTTPError as http_err:
        error = f"HTTP error: {http_err.response.status_code}"
    except requests.exceptions.RequestException as err:
        error = f"Request execution error: {err}"
    except Exception as e:
        error = f"Unknown error: {e}"
    else:
        file_stream = BytesIO(response.content)
        file_stream.seek(0)
        return send_file(file_stream, as_attachment=True, download_name=image_name)

    return redirect(url_for('index', action_error=error))


@app.route('/metadata', methods=['GET'])
def show_metadata():
    image_name = request.args.get('filename')
    if image_name == '':
        return redirect(url_for('index', action_error='No selected file'))

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


@app.route('/subscribe', methods=['POST'])
def subscribe_email():
    email = request.form.get('email')
    if not email:
        redirect(url_for('index', subscription_error='Non valid e-mail'))

    message = subscription_service.subscribe_email(email)
    return redirect(url_for('index', subscription_message=message))


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe_email():
    email = request.form.get('email')
    if not email:
        redirect(url_for('index', subscription_error='Non valid e-mail'))

    message = subscription_service.unsubscribe_email(email)
    return redirect(url_for('index', subscription_message=message))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

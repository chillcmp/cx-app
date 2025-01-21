import os

from flask import Flask, render_template, send_from_directory, request, redirect, url_for

from config import AppConfig
from utils import get_uploaded_images, check_file_in_post_request, check_file_in_get_request

app = Flask(__name__)
app.config.from_object(AppConfig)


@app.route('/')
def index():
    images = get_uploaded_images()
    return render_template('index.html', images=images)


@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)


@app.route('/upload', methods=['POST'])
@check_file_in_post_request
def upload_file(error: str = None):
    if error:
        return redirect(url_for('index', upload_error=error))

    file = request.files['file']
    file_path = os.path.join(AppConfig.UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
@check_file_in_post_request
def delete_file(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    filename = request.form['filename']
    file_path = os.path.join(AppConfig.UPLOAD_FOLDER, filename)
    os.remove(file_path)
    return redirect(url_for('index'))


@app.route('/download', methods=['GET'])
@check_file_in_get_request
def download_file(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))

    filename = request.args.get('filename')
    return send_from_directory(AppConfig.UPLOAD_FOLDER, filename, as_attachment=True)


@app.route('/metadata', methods=['GET'])
@check_file_in_get_request
def show_metadata(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))
    return redirect(url_for('index'))


@app.route('/random-metadata', methods=['GET'])
@check_file_in_get_request
def random_metadata(error: str = None):
    if error:
        return redirect(url_for('index', action_error=error))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

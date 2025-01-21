import os

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    images = [file for file in images if allowed_file(file)]
    return render_template('index.html', images=images)


@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    pass


@app.route('/delete', methods=['POST'])
def delete_file():
    pass


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    pass


@app.route('/metadata/<filename>', methods=['GET'])
def show_metadata(filename):
    pass


@app.route('/metadata/random', methods=['GET'])
def random_metadata():
    pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

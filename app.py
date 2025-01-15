from flask import Flask, render_template, send_from_directory
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)


@app.route('/')
def home():
    region_and_az = get_region_and_az()
    return render_template('index.html', region_and_az=region_and_az)


@app.route('/image')
def display_image():
    image_folder = './'
    image_name = 'lula.jpg'
    return send_from_directory(image_folder, image_name)


def get_region_and_az():
    try:
        session = boto3.session.Session()
        current_region = session.region_name

        ec2_metadata = boto3.client('ec2', region_name=current_region)
        response = ec2_metadata.describe_availability_zones()
        current_az = response['AvailabilityZones'][0]['ZoneName']

        return f'Region: {current_region}, Availability Zone: {current_az}'
    except NoCredentialsError:
        return "Credentials not available"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

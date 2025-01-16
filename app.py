import requests
from flask import Flask, render_template, send_from_directory
import boto3

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


def get_region_from_metadata():
    metadata_url = "http://169.254.169.254/latest/meta-data/placement/availability-zone"
    response = requests.get(metadata_url)
    response.raise_for_status()
    availability_zone = response.text
    return availability_zone[:-1]


def get_region_and_az():
    try:
        region = get_region_from_metadata()
        ec2 = boto3.client('ec2', region_name=region)

        instance_id = requests.get("http://169.254.169.254/latest/meta-data/instance-id").text

        response = ec2.describe_instances(InstanceIds=[instance_id])
        availability_zone = response["Reservations"][0]["Instances"][0]["Placement"]["AvailabilityZone"]

        return f'Region: {region}, Availability Zone: {availability_zone}'

    except Exception as e:
        return f"Cannot fetch region and AZ: {e}"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

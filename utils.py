import os

import boto3
import requests

from flask import request, redirect, url_for
from functools import wraps

from config import AppConfig


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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AppConfig.ALLOWED_EXTENSIONS


def get_uploaded_images():
    images = os.listdir(AppConfig.UPLOAD_FOLDER)
    return [file for file in images if allowed_file(file)]

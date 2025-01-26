import os


class AppConfig:
    REGION = os.getenv("REGION")

    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    PRESIGNED_URL_LIFETIME_S = 3600

    SQLALCHEMY_DATABASE_URI = ("mysql+pymysql://" + os.getenv('DB_USER') + ":"
                               + os.getenv('DB_PASSWORD') + "@"
                               + os.getenv('DB_HOST')
                               + ":3306/" + os.getenv('DB_NAME'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

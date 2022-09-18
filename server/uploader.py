import boto3 
import os

def upload_to_s3(filepath, filename):
    """Uploads image to s3 bucket"""

    s3 = boto3.client(
        service_name='s3',
        endpoint_url=os.environ.get('S3_ENDPOINT_URL'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    )

    bucket = f"{os.environ.get('S3_BUCKET')}"
    image_root_url = f"{os.environ.get('IMAGE_ROOT_URL')}"

    s3.upload_file(
        Filename=filepath,
        Bucket=bucket,
        Key=filename,
        ExtraArgs={
            'ContentType': 'image/png',
        }
    )

    return f"{image_root_url}{filename}"

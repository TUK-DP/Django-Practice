import os

import boto3
from django.core.files.uploadedfile import InMemoryUploadedFile
from dotenv import load_dotenv

load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)

s3 = session.resource('s3')

# get all objects in bucket
bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
bucket = s3.Bucket(bucket_name)


def upload_file_to_s3(file: InMemoryUploadedFile, filename: str):
    """
    :param file: InMemoryUploadedFile 파일
    :param filename: 파일 이름
    """

    filename = "image/" + filename

    # Upload the image file to S3
    bucket.upload_fileobj(file, filename, ExtraArgs={"ContentType": "image/jpeg"})

    return f"https://{bucket_name}.s3.amazonaws.com/{filename}"


def delete_file_from_s3(filename):
    """
    :param filename: 파일 이름
    """
    obj = s3.Object(bucket_name, filename)
    obj.delete()


def get_all_files_from_s3():
    """
    :return: 모든 파일 이름 리스트
    """
    return [obj.key for obj in bucket.objects.all()]

if __name__ == '__main__':
    s_ = get_all_files_from_s3()
    print(s_)
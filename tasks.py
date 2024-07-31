import time
import random

from celery import Celery

app = Celery('image', broker='redis://redis:6379', backed='redis://redis:6379')

@app.task
def working(id=1):
    print("hello") 
    time.sleep(random.randint(1, 10))

    return f"Task {id} Done!"

@app.task
def working2(id=1):
    print("hello") 
    time.sleep(random.randint(1, 10))

    return f"Task {id} Done!"

@app.task
def working3(id=1):
    print("hello") 
    time.sleep(random.randint(1, 10))

    return f"Task {id} Done!"

#image.gpt.GenerateImage.py
import os
import requests
import deepl
from dotenv import load_dotenv
from googletrans import Translator

#image.gpt.ImageConverter.py
from io import BytesIO
import requests
from PIL import Image
from django.core.files import File

#image.s3_modules.s3_handler.py
import os
import uuid
import boto3
from django.core.files import File
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSLATOR_API_KEY = os.getenv("TRANSLATOR_AUTH_KEY")

@app.task
def generate_image(prompt, n=1):
    #image.gpt.ImageConverter.py
    def url_to_image(url) -> Image:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        return image


    def bytes_to_image(byte) -> Image:
        image = Image.open(BytesIO(byte))
        return image


    def image_to_file(image: Image) -> File:
        byte = image_to_bytes(image)
        return File(byte, "")


    def image_to_bytes(image: Image) -> BytesIO:
        byte = BytesIO()
        image.save(byte, format=image.format)
        byte.seek(0)
        return byte


    def url_to_file(url) -> File:
        image = url_to_image(url)
        return image_to_file(image)

    #image.s3_modules.s3_handler.py
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


    def make_random_filename():
        # uuid 생성
        return str(uuid.uuid4())


    def upload_file_random_name_to_s3(image: File):
        return upload_file_to_s3(image, make_random_filename())


    def upload_file_to_s3(file: File, filename: str):
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

    #image.gpt.GenerateImage.py
    def translate_korean_to_english(korean: str) -> str: 
        translator = deepl.Translator(TRANSLATOR_API_KEY) 

        return translator.translate_text(korean, target_lang="EN-US").text


    def gpt_generate_image_urls(english_prompt: str, model="dall-e-2", n=1, size="256x256") -> list:
        request_url = "https://api.openai.com/v1/images/generations"

        data = {
            "model": model,
            "prompt": english_prompt,
            "n": n,
            "size": size
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Organization": "org-wA8q4aQ2GGmCmuGTMOpmjGpN",
            "OpenAI-Project": PROJECT_ID
        }

        response = requests.post(request_url, json=data, headers=headers)

        return [i['url'] for i in response.json()['data']]
    
    urls = []

    # english_prompt = 배경제거 + 그림일기 + english prompt
    english_prompt = "With the background removed, Enter the drawing diary, " + translate_korean_to_english(prompt)
    print("english_prompt : " + english_prompt)

    for url in gpt_generate_image_urls(english_prompt=english_prompt, n=n):
        file = url_to_file(url)
        uploaded_image_url = upload_file_random_name_to_s3(file)
        urls.append(uploaded_image_url)

    return urls


@app.task
def test_generate_image(prompt, n=1):
    def translate_korean_to_english(korean: str) -> str: 
        translator = deepl.Translator("bce42c5a-8ca0-4ff2-8013-f475a39ac846:fx") 

        return translator.translate_text(korean, target_lang="EN-US").text

    # english_prompt = 배경제거 + 그림일기 + english prompt
    english_prompt = "With the background removed, Enter the drawing diary, " + translate_korean_to_english(prompt)
    print("english_prompt : " + english_prompt)
    
    return ["https://tukorea-dp.s3.amazonaws.com/image/test.png" for _ in range(n)]
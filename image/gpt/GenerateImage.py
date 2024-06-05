import os

import requests
from dotenv import load_dotenv
from googletrans import Translator

from image.gpt.ImageConverter import url_to_file
from image.s3_modules.s3_handler import upload_random_name_file_to_s3

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_upload_image(prompt, n=1):
    urls = []
    # english_prompt = 배경제거 + 그림일기 + english prompt
    english_prompt = "With the background removed, Enter the drawing diary, " + translate_korean_to_english(prompt)
    print("english_prompt : " + english_prompt)

    for url in gpt_generate_image_urls(english_prompt=english_prompt, n=n):
        file = url_to_file(url)
        uploaded_image_url = upload_random_name_file_to_s3(file)
        urls.append(uploaded_image_url)

    return urls


def translate_korean_to_english(korean: str) -> str:
    translator = Translator(service_urls=['translate.google.co.kr'])
    return translator.translate(korean, src='ko', dest="en").text


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


def test_generate_image_urls(prompt: str, n=1) -> list:
    return ["https://tukorea-dp.s3.amazonaws.com/image/test.png" for _ in range(n)]

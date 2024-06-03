import os

import requests
from PIL import Image
from dotenv import load_dotenv

from image.gpt import ImageConverter

load_dotenv()

REMOVE_BACKGROUND_KEY = os.getenv("REMOVE_BACKGROUND_KEY")
REMOVE_BACKGROUND_API_URL = os.getenv("REMOVE_BACKGROUND_API_URL")


def remove_background(url) -> Image:
    request_image_bytes = apicall(url)
    return ImageConverter.bytes_to_image(request_image_bytes)


def apicall(url) -> bytes:
    response = requests.post(
        REMOVE_BACKGROUND_API_URL,
        data={
            'image_url': url,
            'size': 'auto'
        },
        headers={'X-Api-Key': REMOVE_BACKGROUND_KEY},
    )
    return response.content

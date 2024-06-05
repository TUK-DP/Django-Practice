from io import BytesIO

import requests
from PIL import Image
from django.core.files import File


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

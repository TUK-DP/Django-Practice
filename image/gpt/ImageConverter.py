import requests
from PIL import Image
from io import BytesIO

from django.core.files import File


def url_to_image(url) -> Image:
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image


def bytes_to_image(byte) -> Image:
    image = Image.open(BytesIO(byte))
    return image


def image_to_file(image: Image, filename) -> File:
    byte = image_to_bytes(image)
    return File(byte, filename)


def image_to_bytes(image: Image) -> BytesIO:
    byte = BytesIO()
    image.save(byte, format=image.format)
    byte.seek(0)
    return byte

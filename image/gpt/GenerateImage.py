from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
import os
from image.gpt.ImageConverter import url_to_image

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    project=PROJECT_ID,
    api_key=OPENAI_API_KEY
)


def generate_test_image(prompt: str) -> Image:
    return url_to_image("https://tukorea-dp.s3.amazonaws.com/image/test.png")


def generate_image(prompt: str, model="dall-e-2", n=1, size="256x256") -> Image:
    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=n,
        size=size
    )
    return url_to_image(response.data[0].url)

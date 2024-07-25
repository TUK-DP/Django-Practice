import time
import random

from celery import Celery

from image.gpt.GenerateImage import gpt_generate_image_urls, test_generate_image_urls

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

# @app.task
# def generate_image(prompt, n=1):
#     urls = gpt_generate_image_urls(prompt, n)
#     return urls


# @app.task
# def test_generate_image(prompt, n=1):
#     urls = test_generate_image_urls(prompt, n)
#     return urls
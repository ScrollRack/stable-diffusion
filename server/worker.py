import os, sys
import redis
import time
import json
# from txt2img import generate as generate_image
from upscaler import upscale
from dotenv import load_dotenv
from os.path import join, dirname
from dotenv import load_dotenv
import requests

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

r = redis.Redis(
    # host= os.environ.get('REDIS_HOST', 'redis://localhost'),
    # port= os.environ.get('REDIS_PORT', '6379'),
    # password= os.environ.get('REDIS_PASSWORD'),
    # ssl=False
)

def create_image(prompt, args):
    """Create image and upload to S3"""
    webhook = args.get('webhook_url')

    if not webhook:
        return
        
    try:
        # images, time = generate_image(
        #     prompt = prompt,
        #     seed = args.get('seed', 0),
        #     width = args.get('width', 512),
        #     height = args.get('height', 512),
        #     steps = args.get('steps', 40),
        #     iterations = args.get('iterations', 1),
        #     scale = args.get('scale', 7.5),
        # )

        # requests.post(webhook, json={ 'images': images, 'time': time, 'job_id': args.get('job_id') })
        pass
    except Exception as e:
        print(e)


while True:
    image_creation = r.lpop('generate_images')
    upscale_image = r.lpop('upscale_images')

    if image_creation:
        data = json.loads(image_creation)
        create_image(data['prompt'], data)

    if upscale_image:
        data = json.loads(upscale_image)
        upscale(data['image_url'], data['scale'])
    
    time.sleep(0.25)

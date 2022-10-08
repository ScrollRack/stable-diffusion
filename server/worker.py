import os, sys
import redis
import time
import json
from txt2img import generate as generate_image
from upscaler import upscale
from dotenv import load_dotenv
from os.path import join, dirname
from dotenv import load_dotenv
import requests

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

r = redis.Redis(
    host= os.environ.get('REDIS_HOST', 'localhost'),
    port= os.environ.get('REDIS_PORT', '6379'),
    password= os.environ.get('REDIS_PASSWORD'),
    ssl=False
)

def create_image(prompt, args):
    """Create image and upload to S3"""
    webhook = args.get('webhook_url')

    if not webhook:
        return
        
    try:
        images, time, nsfw = generate_image(
            prompt = prompt,
            seed = args.get('seed', 0),
            width = args.get('width', 512),
            height = args.get('height', 512),
            steps = args.get('steps', 40),
            iterations = args.get('iterations', 1),
            scale = args.get('scale', 7.5),
        )

        requests.post(webhook, json={
            "images": images, "nsfw": nsfw, "time": time, "job_id": args.get('job_id')
        })

        pass
    except Exception as e:
        print(e)

def upscale_image(args):
    """Upscales image and upload to S3"""
    webhook = args.get('webhook_url')
    image_url = args.get('image_url')
    scale = args.get('scale', 4)

    if not webhook:
        return

    try:
        file_url = upscale(image_url, factor=scale)

        if (file_url):
            requests.post(webhook, json={ 'file_url': file_url, 'job_id': args.get('job_id') })
        else:
            requests.post(webhook, json={ 'error': 'unable to upscale image', 'job_id': args.get('job_id') })

    except Exception as e:
        print(e)


while True:
    t2i_payload = r.lpop('generate_images')
    upscale_payload = r.lpop('upscale_images')

    if t2i_payload:
        data = json.loads(t2i_payload)
        create_image(data['prompt'], data)

    if upscale_payload:
        data = json.loads(upscale_payload)
        upscale_image(data)
    
    time.sleep(0.25)

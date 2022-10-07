import cv2
import glob
import sys, os
import requests
import numpy as np
import upsample
from os.path import join, dirname
from dotenv import load_dotenv
from uploader import upload_to_s3

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

def upscale(
    image_url,
    factor = 4,
):
    data = requests.get(image_url)

    if data.status_code != 200:
        # TODO: Send error
        print("Error: Image not found")
        return None

    output_path = 'outputs/upscaled'
    os.makedirs(output_path, exist_ok=True)

    img = cv2.imdecode(np.frombuffer(data.content, np.uint8), cv2.IMREAD_UNCHANGED)
    img_mode = None
    img_name = 'upscaled_' + image_url.split('/')[-1]
    save_path = os.path.join(output_path, f'{img_name}')
    file_url = None

    try:
        output = upsample.upscale(img, factor=factor)
    except RuntimeError as error:
        print('Error', error)
    else:
        cv2.imwrite(save_path, output)
        print("finished")
    
    try:
        file_url = upload_to_s3(save_path, img_name)
        print(f"Uploaded to {file_url}")
    except Exception as error:
        print('Error', error)

    return file_url

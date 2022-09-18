import cv2
import glob
import sys, os
import requests
import time
import numpy as np
from os.path import join, dirname
from dotenv import load_dotenv
from basicsr.archs.rrdbnet_arch import RRDBNet
from uploader import upload_to_s3

sys.path.append('src/realesrgan')

from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
model_path = os.path.join('./' + os.environ.get('MODEL_PATH'))

def upscale(
    image_url,
    outscale = 4,
):
    tile = 0
    tile_pad = 10
    pre_pad = 0
    fp32 = True
    gpu_id = None 
    netscale = 4
    input = image_url

    print(f"Upscaling {input} by {outscale}x")
    data = requests.get(input)

    if data.status_code != 200:
        # TODO: Send error
        print("Error: Image not found")
        return None

    # restorer
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        model=model,
        tile=tile,
        tile_pad=tile_pad,
        pre_pad=pre_pad,
        half=not fp32,
        gpu_id=gpu_id)

    output_path = 'outputs/upscaled'
    os.makedirs(output_path, exist_ok=True)

    img = cv2.imdecode(np.frombuffer(data.content, np.uint8), cv2.IMREAD_UNCHANGED)
    img_mode = None
    img_name = input.split('/')[-1]
    save_path = os.path.join(output_path, f'{img_name}')
    file_url = None

    try:
        output, _ = upsampler.enhance(img, outscale=outscale)
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

from PIL import Image
import requests


def load_image_from_file(image_path):
    return Image.open(image_path).convert("RGB")

def load_image_from_url(image_url):
    response = requests.get(image_url, stream=True)
    response.raw.decode_content = True
    return Image.open(response.raw)

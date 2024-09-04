from bs4 import BeautifulSoup
from io import BytesIO
from pathlib import Path
from PIL import Image
from urllib.parse import urlparse, urljoin
import requests

def is_url(url:str) -> object:
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return result
    except Exception as err:
        pass
    return None

def get_soup(url:str) -> object:
    try:
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except:
        return None

def get_elements(soup:object, elements:list, first:bool=False) -> list:
    found_elements = []
    for element in elements:
        try:
            if element['key']:
                for value in soup.select(element['selector']):
                    found_elements.append(value.get(element['key']).strip())
                    if first: break
            else:
                for value in soup.select(element['selector']):
                    found_elements.append(value.text.strip())
                    if first: break
        except:
            pass
    return found_elements


def get_full_url(host:str, url:str):
    if is_url(url) is None:
        return urljoin(host, url)
    return url

def save_image(url:str, target:Path, fileType:str=None):
    parent_path = Path(__file__).resolve().parent.parent
    target = parent_path / target
    if fileType == 'icon':
        image_size = (96, 96)
    else:
        image_size = (600, 600)
    if url and url.startswith('http'):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
    else:
        return None
    image = image.convert('RGBA', dither=Image.NONE, palette=Image.ADAPTIVE)
    image.thumbnail(image_size)
    buffered = BytesIO()
    image.save(buffered, format="PNG", dpi=(128, 128), quality=95)
    image_binary = buffered.getvalue()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target.resolve(), 'wb') as file:
        file.write(image_binary)

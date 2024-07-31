
import base64 # type: ignore
import hashlib # type: ignore
import re # type: ignore
from flask.helpers import url_for
import requests
from bs4 import BeautifulSoup
from io import BytesIO # type: ignore
from pathlib import Path # type: ignore
from PIL import Image
from urllib.parse import urlparse # type: ignore
from modules.logger import logger, method_path

class Item():
    url = None
    id = None
    description = None
    hash = None
    host = None
    icon = None
    poster = None
    schema = None
    tags = None
    actors = None
    collections = None
    title = None

    def __init__(self) -> None:
        self.__initialize_resources()

    def start(self, url):
        self.clear()
        self.url = url
        self.hash = self._hash_string(url)
        self.parse_url(url)
        self._get_soup(url)
        self.get_title()
        self.get_description()
        self.get_tags()
        self.get_actors()
        self.get_collections()
        self.get_poster()
        self.get_icon()

    def clear(self):
        for k in self.__dict__.keys():
            setattr(self, k, None)

    @classmethod
    def __initialize_resources(cls):
        cls._url_head = None
        cls._url_body = None

    @classmethod
    def _to_string(cls, value):
        conv = lambda i : i or ''
        return conv(value).replace('"',"'")
    
    @classmethod
    def _select_first(cls, location, element, target):
        try: value = location.select_one(element).get(target)
        except: value = None
        return value
    
    @classmethod
    def _get_soup(cls, url):
        try:
            logger.info(f"{method_path(cls.__name__)}: start")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 500:
                print(response.content)
            with open('fetched.html', 'wb+') as f:
                f.write(response.content)
            soup = BeautifulSoup(response.content, 'html.parser')
            # soup = BeautifulSoup(response.text, 'html.parser')
            cls._url_head = soup.find('head')
            cls._url_body = soup.find('body')
            logger.info(f"{method_path(cls.__name__)}: complete")
        except Exception as err:
            logger.warning(f"{method_path(cls.__name__)}: {err}")

    @classmethod
    def _url_check(cls, url):
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                logger.info(f"{method_path(cls.__name__)}: complete")
                return url
            else:
                logger.warning(f"{method_path(cls.__name__)}: not an url")
                return None
        except Exception as err:
            logger.warning(f"{method_path(cls.__name__)}: {err}")
            return None
        
    @classmethod
    def _hash_string(cls, value):
        try:
            hash = hashlib.md5()
            hash.update(value.encode('utf-8'))
            hash = hash.hexdigest()
            logger.info(f"{method_path(cls.__name__)}: {hash}")
            return hash
        except Exception as err:
            logger.warning(f"{method_path(cls.__name__)}: {err}")
            return None
        
    def parse_url(self, url):
        parsed_url = urlparse(url)
        self.schema = parsed_url.scheme
        self.host = parsed_url.netloc
        if self.host.startswith("www."):
            self.host = self.host[len("www."):]

    def get_title(self):
        try:
            self.title = self._select_first(self._url_head, 'meta[property*="title"]', 'content')
            self.title = self.title if self.title else self._select_first(self._url_head, 'meta[name*="title"]', 'content')
            self.title = self.title if self.title else self._url_head.title.string
            logger.info(f"{method_path(self.__class__.__name__)}: {self.title[:50]}...")
            self.title = self._to_string(self.title)
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")

    def get_description(self):
        try:
            self.description = self._select_first(self._url_head, 'meta[property*="description"]', 'content')
            self.description = self.description if self.description else self._select_first(self._url_head, 'meta[name*="description"]', 'content')
            logger.info(f"{method_path(self.__class__.__name__)}: {self.description[:50]}...")
            self.description = self._to_string(self.description)
        except Exception as err:
           logger.warning(f"{method_path(self.__class__.__name__)}: {err}")

    def get_tags(self):
        try:
            tags = []
            for tag in self._url_body.select('[class="tags-list"] a'):
                tags.append( tag.text.strip().lower() )
            for tag in self._url_body.select('a[href*="tag"]'):
                tags.append( tag.text.strip().lower() )
            for tag in self._url_body.select('[id="tag-box"] li'):
                tags.append( tag.text.strip().lower() )
            for tag in self._url_body.select('[id="video-info-tags"] li[class="vit-category"]'):
                tags.append( tag.text.strip().lower() )
            for tag in self._url_body.select('a[class*="badge-video"]'):
                tags.append( tag.text.strip().lower() )
            tags = sorted(set([ x for x in tags if len(x) > 1 and bool(re.search('edit|tag|model|suggest', x)) == False ]))
            self.tags = ', '.join(tags)
            logger.info(f"{method_path(self.__class__.__name__)}: {self.tags[:50]}...")
            self.tags = self._to_string(self.tags)
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")

    def get_actors(self):
        try:
            actors = []
            for actor in self._url_body.select('a[href*="/actor"]'):
                actors.append( actor.text.strip().lower() )
            for actor in self._url_body.select('[class*="pornstarsWrapper"] a[href*="/pornstar"]'):
                actors.append( actor.text.strip().lower() )
            for actor in self._url_body.select('[id="video-actors"] a'):
                actors.append( actor.text.strip().lower() )
            for actor in self._url_body.select('[id="videotags"] a[class="studiolink1"]'):
                actors.append( actor.text.strip().lower() )
            for actor in self._url_body.select('[id="video-info-tags"] li[class="vit-pornstar starw"]'):
                actors.append( actor.text.strip().lower() )
            for actor in self._url_body.select('a[href*="/stars"][rel="tag"]'):
                actors.append( actor.text.strip().lower() )
            for actor in self._url_body.select('[id="tab_video_info"] [class="item"] a[href*="/models"]'):
                actors.append( actor.text.strip().lower() )
            if actors == []:
                for actor in self._url_body.select('[id="shareToStream"] [class*="usernameWrap"] [class="usernameBadgesWrapper"] a'):
                    actors.append( actor.text.strip().lower() )
            actors = sorted(set([ x for x in actors if len(x) > 1 and bool(re.search('actor|actors|model|suggest', x)) == False ]))
            self.actors = ', '.join(actors)
            logger.info(f"{method_path(self.__class__.__name__)}: {self.actors[:50]}...")
            self.actors = self._to_string(self.actors)
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")

    def get_collections(self):
        try:
            collections = []
            for collection in self._url_body.select('[id="shareToStream"] [class*="usernameWrap"] [class="usernameBadgesWrapper"] a'):
                collections.append( collection.text.strip().lower() )
            for collection in self._url_body.select('[class="categoriesWrapper"] a'):
                collections.append( collection.text.strip().lower() )
            for collection in self._url_body.select('[id="videotags"] a[class="studiolink2"]'):
                collections.append( collection.text.strip().lower() )
            for collection in self._url_body.select('a[href*="/genero"]'):
                collections.append( collection.text.strip().lower() )
            for collection in self._url_body.select('[id="tab_video_info"] [class="item"] a[href*="/categories"]'):
                collections.append( collection.text.strip().lower() )
            collections = sorted(set([ x for x in collections if len(x) > 1 and bool(re.search('collection|collections|suggest|all|verified', x)) == False ]))
            self.collections = ', '.join(collections)
            logger.info(f"{method_path(self.__class__.__name__)}: {self.collections[:50]}...")
            self.collections = self._to_string(self.collections)
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")


    def get_poster(self):
        try:
            poster_url = self._select_first(self._url_head, 'meta[property*="image"]', 'content')
            poster_url = poster_url if poster_url else self._select_first(self._url_head, 'meta[name*="image"]', 'content')
            parsed_url = urlparse(poster_url)
            if not parsed_url.scheme:
                poster_url = f'{self.schema}://{poster_url.lstrip("/")}'
            if self._url_check(poster_url) is None:
                poster_url = f'{self.schema}://{self.host}/{poster_url.lstrip("/")}'
            response = requests.get(poster_url, stream=True)
            response.raise_for_status()
            self.poster = poster_url
            if self._url_check(poster_url) is None:
                poster_url = self.schema + '://' + self.host + '/' + poster_url.strip('/')
            logger.info(f"{method_path(self.__class__.__name__)}: {self.poster[:50]}...")
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")
            self.poster = 'static/img/img_404.jpg'
        return self.poster


    def get_icon(self):
        try:
            icon_url = self._select_first(self._url_head, '[rel*="icon"]', 'href')
            icon_parse = urlparse(icon_url)
            if not icon_parse.scheme:
                icon_url = f'{self.schema}://{icon_url.lstrip("/")}'
            if self._url_check(icon_url) is None:
                icon_url = f'{self.schema}://{self.host}/{icon_url.lstrip("/")}'
            icon_url = icon_url.replace('\n', '').replace('\r', '')
            response = requests.get(icon_url, stream=True)
            response.raise_for_status()
            self.icon = icon_url
            logger.info(f"{method_path(self.__class__.__name__)}: {self.icon}")
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")
            self.icon = 'static/img/icon_404.png'
        return self.icon

    def save_poster(self, user_id):
        try:
            parent_path = Path(__file__).resolve().parent.parent
            if self.poster.startswith('http'):
                response = requests.get(self.poster, stream=True)
                response.raise_for_status()
                poster = Image.open(BytesIO(response.content))
            else:
                poster_path = Path(self.poster)
                poster = Image.open(poster_path)
            poster = poster.convert('RGB', dither=Image.NONE, palette=Image.ADAPTIVE)
            poster.thumbnail((600, 600))
            buffered = BytesIO()
            poster.save(buffered, format="JPEG", dpi=(128, 128), quality=95)
            poster_name = self._hash_string(self.poster)
            poster_binary = buffered.getvalue()
            poster_target = f'user/{user_id}/thumbs/{poster_name}.jpg'
            poster_path = parent_path / f'static/{poster_target}'
            poster_path.parent.mkdir(parents=True, exist_ok=True)
            with open(poster_path, 'wb') as file:
                file.write(poster_binary)
            if poster_path.exists():
                logger.info(f"{method_path(self.__class__.__name__)}: {poster_path.exists()}")
                return str(poster_target)
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")
        return 'img/img_404.jpg'

        
    def save_icon(self, user_id):
        try:
            parent_path = Path(__file__).resolve().parent.parent
            if self.icon.startswith('http'):
                response = requests.get(self.icon, stream=True)
                response.raise_for_status()
                icon = Image.open(BytesIO(response.content))
            else:
                icon_path = Path(self.icon)
                icon = Image.open(icon_path)
            icon = icon.convert('RGBA', dither=Image.NONE, palette=Image.ADAPTIVE)
            icon.thumbnail((96, 96))
            buffered = BytesIO()
            icon.save(buffered, format="PNG", dpi=(128, 128), quality=95)
            icon_name = self._hash_string(self.icon)
            icon_binary = buffered.getvalue()  # Get binary data from the buffer
            icon_target = f'user/{user_id}/hosts/{icon_name}.png'
            icon_path = parent_path / f'static/{icon_target}'
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            with open(icon_path, 'wb') as file:
                file.write(icon_binary)
            if icon_path.exists():
                logger.info(f"{method_path(self.__class__.__name__)}: {icon_path.exists()}")
                return str(icon_target)
        except Exception as err:
            logger.warning(f"{method_path(self.__class__.__name__)}: {err}")
        return 'img/icon_404.png'
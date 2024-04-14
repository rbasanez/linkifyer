import hashlib
import re
import requests
import base64
import inspect
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
from pathlib import Path
from bs4 import BeautifulSoup
from models.logger import logger
from models.database import db

class Item:
    def __init__(self):
        """
        Initializes an Item instance.

        Parameters:
        - db: Database instance
        - logger: Logger object for logging
        """
        self.__initialize_resources(db, logger)
        self.item_id = None
        self.item_hash = None
        self.user_id = None
        self.title = None
        self.url = None
        self.tags = None
        self.poster = None
        self.icon = None
        self.description = None

    @classmethod
    def __initialize_resources(cls, db, logger):
        """
        Initializes class-level resources.

        Parameters:
        - db: Database instance
        - logger: Logger object for logging
        """
        cls._static_folder = Path(__file__).resolve().parent.parent / 'static'
        cls._db = db
        cls._logger = logger
        cls._url_head = None
        cls._url_body = None
        cls._url_schema = None
        cls._url_host = None

    def db_start(self):
        """
        Initializes the database table for Items.
        """
        success, result = self._db.execute('''
            CREATE TABLE IF NOT EXISTS "Items" (
                "item_id"       INTEGER NOT NULL,
                "item_hash"     TEXT NOT NULL,
                "user_id"       INT NOT NULL,
                "url"           TEXT NOT NULL,
                "title"         TEXT,
                "tags"          TEXT,
                "description"   TEXT,
                "poster"        TEXT,
                "icon"          TEXT,
                "favorite"      INT DEFAULT 0,
                "created_at"    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY("item_id" AUTOINCREMENT),
                FOREIGN KEY("user_id") REFERENCES users ("user_id"),
                UNIQUE(user_id, item_hash)
            );
        ''')
        if success:
            self._logger.info(f"{self._method_path()}: {success}")
        else:
            self._logger.error(f"{self._method_path()}: {result}")
            exit()

    @classmethod
    def _method_path(cls):
        """
        Returns the path of the calling method.
        """
        return "{0}.{1}".format(cls.__name__, inspect.stack()[1][3])
    
    @classmethod
    def _request_soup(cls, url):
        """
        Sends a request to the provided URL and parses the response as a BeautifulSoup object.

        Parameters:
        - url: URL to request

        Returns:
        - soup: BeautifulSoup object representing the parsed response
        """
        try:
            cls._logger.info(f"{cls._method_path()}: start")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            cls._url_head = soup.find('head')
            cls._url_body = soup.find('body')
            cls._logger.info(f"{cls._method_path()}: complete")
            parsed_url = urlparse(url)
            cls._url_schema = parsed_url.scheme
            cls._url_host = parsed_url.netloc
            return soup
        except Exception as e:
            cls._logger.warning(f"{cls._method_path()}: {e}")

    @classmethod
    def _select_first(cls, location, element, target):
        """
        Selects the first occurrence of the specified element within the location and retrieves the value of the target attribute.

        Parameters:
        - location: Location to search for the element (e.g., BeautifulSoup tag)
        - element: HTML element to search for
        - target: Attribute of the element to retrieve the value from

        Returns:
        - value: Value of the target attribute or None if not found
        """
        try: 
            value = location.select_one(element).get(target)
        except: 
            value = None
        return value
    
    @classmethod
    def _url_check(cls, url):
        """
        Checks if the provided string is a valid URL.

        Parameters:
        - url: String to check as URL

        Returns:
        - url: Valid URL if the provided string is a URL, otherwise None
        """
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                cls._logger.info(f"{cls._method_path()}: complete")
                return url
            else:
                cls._logger.warning(f"{cls._method_path()}: not an url")
                return None
        except Exception as e:
            cls._logger.warning(f"{cls._method_path()}: {e}")
            return None
        
    @classmethod
    def _to_string(cls, value):
        conv = lambda i : i or ''
        return conv(value)
    
    @classmethod
    def _hash_string(cls, value):
        """
        Hashes the provided string using MD5 algorithm.

        Parameters:
        - value: String to hash

        Returns:
        - hash: Hashed string
        """
        try:
            hash = hashlib.md5()
            hash.update(value.encode('utf-8'))
            hash = hash.hexdigest()
            cls._logger.info(f"{cls._method_path()}: {bool(hash)}")
            return hash
        except Exception as e:
            cls._logger.warning(f"{cls._method_path()}: {e}")
            return None
        
    def clear(self):
        """
        Clears the attributes of the Item instance.
        """
        for k in self.__dict__.keys():
            setattr(self, k, None)
        self._logger.info(f"{self._method_path()}: complete")
        
    def request_url(self, url):
        """
        Sends a request to the provided URL and parses the response.

        Parameters:
        - url: URL to request
        """
        self.url = url
        self._request_soup(url)

    def delete_item(self, item_id):
        """
        Deletes an item from the database.

        Parameters:
        - item_id: Item ID associated with the item
        """
        try:
            success, result = self._db.execute("DELETE FROM Items WHERE item_id=?", (item_id,))
            if success: 
                self._logger.info(f"{self._method_path()}: {success}")
            else: 
                self._logger.error(f"{self._method_path()}: {result}")
            return result.rowcount
        except Exception as e:
            self._logger.error(f"{self._method_path()}: {e}")

    def toggle_favorite(self, item_id):
        """
        Toggle the favorite status of an item for a specific user.
        """
        try:
            success, result = self._db.execute('''UPDATE Items SET favorite = CASE WHEN favorite = 1 THEN 0 ELSE 1 END WHERE item_id=?''', (item_id,) )
            if success: 
                self._logger.info(f"{self._method_path()}: {result.rowcount}")
            else: 
                self._logger.error(f"{self._method_path()}: {result}")
            return success, result.rowcount
        except Exception as e:
            self._logger.error(f"{self._method_path()}: {e}")

    def count_all_items(self):
        try:
            success, result = self._db.execute("SELECT COUNT(*) count FROM Items WHERE user_id=?", (self.user_id,))
            if success: 
                self._logger.info(f"{self._method_path()}: {success}")
            else: 
                self._logger.error(f"{self._method_path()}: {result}")
            return success, result.fetchone()
        except Exception as e:
            self._logger.error(f"{self._method_path()}: {e}")

    def get_all_items(self):
        """
        Retrieves all Items associated with the user from the database.

        Returns:
        - success: Boolean indicating whether the query was successful
        - result: List of Items retrieved from the database
        """
        try:
            success, result = self._db.execute("""
                SELECT
                     item_id
                    ,item_hash
                    ,title
                    ,url
                    ,poster
                    ,favorite
                    ,LOWER(COALESCE(tags, '') || ' ' || COALESCE(title, '') || ' ' || COALESCE(description, '')) AS keys
                    ,created_at
                FROM Items WHERE user_id=?
                ORDER BY favorite DESC, created_at DESC
            """, (self.user_id,))
            if success: 
                self._logger.info(f"{self._method_path()}: {success}")
            else: 
                self._logger.error(f"{self._method_path()}: {result}")
            return success, result.fetchall()
        except Exception as e:
            self._logger.error(f"{self._method_path()}: {e}")


    def get_items_per_page(self, limit, offset):
        try:
            success, result = self._db.execute("SELECT * FROM Items WHERE user_id=? ORDER BY favorite DESC, created_at DESC LIMIT ? OFFSET ?", (self.user_id, limit, offset))
            if success: 
                self._logger.info(f"{self._method_path()}: {success}")
            else: 
                self._logger.error(f"{self._method_path()}: {result}")
            return success, result.fetchall()
        except Exception as e:
            self._logger.error(f"{self._method_path()}: {e}")

    def get_hash(self):
        """
        Computes the hash of the item URL.
        """
        try:
            self.item_hash = self._hash_string(self.url)
            self._logger.info(f"{self._method_path()}: {bool(self.item_hash)}")
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def get_title(self):
        """
        Retrieves the title of the web page from its meta tag.
        """
        try:
            self.title = self._select_first(self._url_head, 'meta[property*="title"]', 'content')
            self.title = self.title if self.title else self._select_first(self._url_head, 'meta[name*="title"]', 'content')
            self.title = self.title if self.title else self._url_head.title.string
            self._logger.info(f"{self._method_path()}: {bool(self.title)}")
            self.title = self._to_string(self.title)
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def get_poster(self):
        """
        Retrieves and processes the poster image of the web page.
        """
        try:
            poster_url = self._select_first(self._url_head, 'meta[property*="image"]', 'content')
            poster_url = poster_url if poster_url else self._select_first(self._url_head, 'meta[name*="image"]', 'content')
            parsed_url = urlparse(poster_url)
            poster_url = self._url_schema + '://' + poster_url.strip('/') if parsed_url.scheme == '' else poster_url
            if self._url_check(poster_url) is None:
                poster_url = self._url_schema + '://' + self._url_host + '/' + poster_url.strip('/')
            poster = Image.open(requests.get(poster_url, stream=True).raw)
            poster = poster.convert('RGB', dither=Image.NONE, palette=Image.ADAPTIVE)
            poster.thumbnail((600, 600))
            buffered = BytesIO()
            poster.save(buffered, format="JPEG", dpi=(75,75), quality=95)
            self.poster = base64.b64encode(buffered.getvalue()).decode("utf-8")
            self._logger.info(f"{self._method_path()}: {bool(self.poster)}")
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def get_icon(self):
        """
        Retrieves and processes the icon of the web page.
        """
        try:
            icon_url = self._select_first(self._url_head, '[rel*="icon"]', 'href')
            parsed_url = urlparse(icon_url)
            icon_url = self._url_schema + '://' + icon_url.strip('/') if parsed_url.scheme == '' else icon_url
            if self._url_check(icon_url) is None:
                icon_url = self._url_schema + '://' + self._url_host + '/' + icon_url.strip('/')
            icon = Image.open(requests.get(icon_url, stream=True).raw)
            icon = icon.convert('RGBA', dither=Image.NONE, palette=Image.ADAPTIVE)
            icon.thumbnail((96, 96))
            buffered = BytesIO()
            icon.save(buffered, format="PNG", dpi=(75,75), quality=95)
            self.icon = base64.b64encode(buffered.getvalue()).decode("utf-8")
            self._logger.info(f"{self._method_path()}: {bool(self.icon)}")
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def get_tags(self):
        """
        Retrieves tags from the web page content.
        """
        try:
            tags = []
            for tag in self._url_body.select('a[href*="tags/"]'):
                tags.append( tag.text.strip().lower() )
            for tag in self._url_body.select('[class*="tags"] a'):
                tags.append( tag.text.strip().lower() )
            tags = sorted(set([ x for x in tags if len(x) > 1 and bool(re.search('edit|tag|model', x)) == False ]))
            self.tags = ' '.join(tags)
            self._logger.info(f"{self._method_path()}: {bool(self.tags)}")
            self.tags = self._to_string(self.tags)
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def get_description(self):
        """
        Retrieves the description of the web page from its meta tag.
        """
        try:
            self.description = self._select_first(self._url_head, 'meta[property*="description"]', 'content')
            self.description = self.description if self.description else self._select_first(self._url_head, 'meta[name*="description"]', 'content')
            self._logger.info(f"{self._method_path()}: {bool(self.description)}")
            self.description = self._to_string(self.description)
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    # def generate_tags(self):
    #     text = ' '.join([self.title, self.description, self.tags])
    #     text = re.sub(r"[^\w\-' ]", " ", text.lower())
    #     words = word_tokenize(text)
    #     tagged_words = nltk.pos_tag(words)
    #     allowed_tags = ['NN', 'NNS', 'VB', 'VBD', 'VBG', 'VBN', 'VBZ', 'JJ', 'JJR', 'JJS', 'NNP', 'NNPS', 'RB', 'SYM']
    #     filtered_words = [word for word, tag in tagged_words if tag in allowed_tags]
    #     filtered_words = [word for word, tag in tagged_words if word]
    #     print(filtered_words)
    #     word_freq = Counter(filtered_words)
    #     tags = [tag for tag, _ in word_freq.most_common()]
    #     self.tags = ' '.join(tags)
    #     self._logger.info(f"{self._method_path()}: {bool(self.tags)}")
    #     self.tags = self._to_string(self.tags)
        
    def save_poster(self):
        """
        Saves the poster image to the file system.
        """
        try:
            poster_binary = base64.b64decode(self.poster)
            poster_target = f'user/{self.user_id}/thumbs/{self.item_hash}.jpg'
            poster_path = self._static_folder / poster_target
            poster_path.parent.mkdir(parents=True, exist_ok=True)
            with open(poster_path, 'wb') as file:
                file.write(poster_binary)
            if poster_path.exists():
                self.poster = poster_target
            self._logger.info(f"{self._method_path()}: {poster_path.exists()}")
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def save_icon(self):
        """
        Saves the icon image to the file system.
        """
        try:
            icon_name = self._hash_string(self.icon)
            icon_binary = base64.b64decode(self.icon)
            icon_target = f'user/{self.user_id}/hosts/{icon_name}.png'
            icon_path = self._static_folder / icon_target
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            with open(icon_path, 'wb') as file:
                file.write(icon_binary)
            if icon_path.exists():
                self.icon = icon_target
            self._logger.info(f"{self._method_path()}: {icon_path.exists()}")
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def save_data(self):
        """
        Saves item data to the database.
        """
        try:
            columns = []
            values  = []
            params  = []
            for k, v in self.__dict__.items():
                if v and k != 'item_id':
                    columns.append(k)
                    values.append('?')
                    params.append(v)
            success, result = self._db.execute(f'INSERT OR REPLACE INTO Items ({','.join(columns)}) VALUES ({','.join(values)})', params)
            if success: 
                self._logger.info(f"{self._method_path()}: {success}")
            else: 
                self._logger.error(f"{self._method_path()}: {result}")
            return success
        except Exception as e:
            self._logger.error(f"{self._method_path()}: {e}")

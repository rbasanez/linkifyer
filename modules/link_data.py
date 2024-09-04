import re
from modules.site_actions import *
from modules.item_actions import *
from modules.logger import logger, method_path

class LinkData:
    
    id:int          = None
    hash:str        = None
    user_id:int     = None
    host:str        = None
    url:str         = None
    title:str       = None
    description:str = None
    models:str      = None
    tags:str        = None
    collections:str = None
    poster_url:str  = None
    poster_path:str = None
    icon_url:str    = None
    icon_path:str   = None
    favorite:int    = None
    soup:object     = None
    
    def start(self, url, user_id):
        url_parsed = is_url(url)
        if url_parsed is None:
            logger.warning(f"{method_path(self.__class__.__name__)}: not a valid url: <{url}>")
            return None
        self.user_id = user_id
        self.soup = get_soup(url)
        self.hash  = get_hash_string(url)
        self.url   = url
        self.host  = '{0}://{1}'.format(url_parsed.scheme, url_parsed.hostname)

    def get_title(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        title_elements = [
            { 'selector' : 'meta[property*="title"]',  'key' : 'content'},
            { 'selector' : 'meta[name*="title"]',  'key' : 'content'}
        ]
        found_titles = get_elements(self.soup, title_elements, first=True)
        for title in found_titles:
            self.title = title
            break
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.title}>")
        
    def get_description(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        description_elements = [
            { 'selector' : 'meta[property*="description"]',  'key' : 'content'},
            { 'selector' : 'meta[name*="description"]',  'key' : 'content'}
        ]
        found_descriptions = get_elements(self.soup, description_elements, first=True)
        for description in found_descriptions:
            self.description = description
            break
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.description}>")
        
    def get_models(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        model_elements = [
            { 'selector' : 'a[href*="/actor"]', 'key' : None},
            { 'selector' : '[class*="pornstarsWrapper"] a[href*="/pornstar"]', 'key' : None},
            { 'selector' : '[id="video-model"] a', 'key' : None},
            { 'selector' : '[id="videotags"] a[class="studiolink1"]', 'key' : None},
            { 'selector' : '[id="video-info-tags"] li[class="vit-pornstar starw"]', 'key' : None},
            { 'selector' : 'a[href*="/stars"][rel="tag"]', 'key' : None},
            { 'selector' : '[id="tab_video_info"] [class="item"] a[href*="/models"]', 'key' : None},
            { 'selector' : '[class="video-detail-list"] [class="video-pornstar-title"]', 'key' : None},
        ]
        found_models = get_elements(self.soup, model_elements)
        if found_models == []:
            model_elements = [
                { 'selector' : '[id="shareToStream"] [class*="usernameWrap"] [class="usernameBadgesWrapper"] a', 'key' : None},
            ]
            found_models = get_elements(self.soup, model_elements)
        found_models = sorted(set([ x.lower() for x in found_models if len(x) > 1 and bool(re.search('actor|model|model|suggest', x)) == False ]))
        self.models = ', '.join(found_models)
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.models}>")
        
    def get_tags(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        tag_elements = [
            { 'selector' : '[class="tags-list"] a', 'key' : None},
            { 'selector' : 'a[href*="tag"]', 'key' : None},
            { 'selector' : '[id="tag-box"] li', 'key' : None},
            { 'selector' : '[id="video-info-tags"] li[class="vit-category"]', 'key' : None},
            { 'selector' : 'a[class*="badge-video"]', 'key' : None},
        ]
        found_tags = get_elements(self.soup, tag_elements)
        found_tags = sorted(set([ x.lower() for x in found_tags if len(x) > 1 and bool(re.search('edit|tag|model|suggest', x)) == False ]))
        self.tags = ', '.join(found_tags)
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.tags}>")
        
    def get_collections(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        collection_elements = [
            { 'selector' : '[id="shareToStream"] [class*="usernameWrap"] [class="usernameBadgesWrapper"] a', 'key' : None},
            { 'selector' : '[class="categoriesWrapper"] a', 'key' : None},
            { 'selector' : '[id="videotags"] a[class="studiolink2"]', 'key' : None},
            { 'selector' : 'a[href*="/genero"]', 'key' : None},
            { 'selector' : '[id="tab_video_info"] [class="item"] a[href*="/categories"]', 'key' : None},
        ]
        found_collections = get_elements(self.soup, collection_elements)
        found_collections = sorted(set([ x.lower() for x in found_collections if len(x) > 1 and bool(re.search('collection|collections|suggest|all|verified', x)) == False ]))
        self.collections = ', '.join(found_collections)
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.collections}>")

    def get_icon(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        icon_elements = [
            { 'selector' : '[rel*="icon"]',  'key' : 'href'}
        ]
        found_icons = get_elements(self.soup, icon_elements, first=True)
        for icon in found_icons:
            host_hashed = get_hash_string(self.host)
            self.icon_url  = get_full_url(self.host, icon)
            self.icon_path = 'static/user/{0}/icons/{1}.png'.format(self.user_id, host_hashed)
            break
        self.icon_path = self.icon_path if self.icon_path else 'static/img/icon_404.png'
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.icon_path}>")

    def get_poster(self):
        logger.info(f"{method_path(self.__class__.__name__)}: start")
        poster_elements = [
            { 'selector' : 'meta[property*="image"]',  'key' : 'content'}
        ]
        found_posters = get_elements(self.soup, poster_elements, first=True)
        for poster in found_posters:
            host_hashed = get_hash_string(self.host)
            self.poster_url  = get_full_url(self.host, poster)
            self.poster_path = 'static/user/{0}/posters/{1}.png'.format(self.user_id, host_hashed)
            break
        self.poster_path = self.poster_path if self.poster_path else 'static/img/img_404.png'
        logger.info(f"{method_path(self.__class__.__name__)}: <{self.poster_path}>")
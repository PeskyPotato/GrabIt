import re
import json
import os
import logging

from .common import Common
from resources.parser import Parser


class Imgur(Common):
    # Tested link formats
    # https://imgur.com/r/humanporn/tHNQLyz
    # https://imgur.com/gallery/YhYQ36h
    # https://imgur.com/a/hWjM8
    # https://i.imgur.com/aI3Avr9.jpg
    # https://imgur.com/a/sdHPt (disturbing content, NSFW)

    valid_url = r'https?://(?:i\.|m\.)?imgur\.com/(?P<col>(a|(gallery)|(r/[a-z0-9]+))/)?(/)?(?P<id>[a-zA-Z0-9]+)(?P<ext>\.[^/]+)*'

    def __init__(self, link, name, direct):
        super().__init__(link, name, direct)
        self.data = {}

    def save(self):
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        self.data = self.get_data()
        if type(self.data) is dict:
            if self.data.get('is_album'):
                self.save_album()
            else:
                self.save_single()
        return False

    def sanitize_url(self):
        match = re.match(self.valid_url, self.link)
        if match.group('col'):
            self.link = 'https://imgur.com/{}/{}'.format(match.group('col')[:-1], match.group('id'))
        else:
            self.link = 'https://imgur.com/{}'.format(match.group('id'))
        self.logger.debug('Sanitized link {}'.format(self.link))

    def get_data(self):
        '''Returns the JSON file with data on images.'''
        imgur_cookie = Parser().config.get("imgur")
        if not imgur_cookie:
            imgur_cookie = {}
        else:
            imgur_cookie = {"Cookie": "authautologin={};".format(imgur_cookie.get("authautologin"))}

        page_html = self.get_html(imgur_cookie)
        if page_html:
            page_html_text = page_html.text
            data_string = re.search('image( ){15}: (?P<data>(.)+)', page_html_text)
            if data_string:
                data = data_string.group('data')[:-1]
                data = json.loads(data)
                return data
        self.logger.warning("Imgur album page returning None")
        return None

    def write_description(self, txt_file, description):
        if description:
            with open(txt_file, "w+") as f:
                f.write(description)

    def save_single(self):
        self.link = "https://imgur.com/{}{}".format(self.data["hash"], self.data["ext"])
        direct_description = self.direct
        title = self.name
        if self.data.get("title"):
            title = self.data.get("title")
        title = self.format_name(title)
        self.direct = os.path.join(self.direct, "{}-{}{}".format(title, self.data["hash"], self.data["ext"]))
        self.logger.debug("Saved single image {}".format(self.link))

        if not self.save_image():
            return False
        self.write_description(os.path.join(direct_description, "{}-{}.txt".format(title, self.data["hash"])), self.data["description"])
        return True

    def save_album(self):
        album_id = self.link.rsplit('/', 1)[-1]
        if '#' in album_id:
            album_id = album_id.rsplit('#', 1)[-2]

        self.logger.debug("Saving album {} - album_id {}".format(self.link, album_id))
        if self.data["title"]:
            folder_name = self.format_name(self.data["title"])
        else:
            folder_name = self.format_name(self.format_name(self.name) + " - " + album_id)
        try:
            images = self.data["album_images"]["images"]
        except KeyError:
            if not self.save_single():
                return False
            return True
        folder = os.path.join(self.direct, folder_name)
        if not os.path.exists(folder):
            os.makedirs(folder)

        counter = 1
        for image in images:
            self.link = "https://imgur.com/{}{}".format(image["hash"], image["ext"])
            self.direct = os.path.join(folder, "{}-{}{}".format(counter, image["hash"], image["ext"]))

            if not self.save_image():
                return False
            self.write_description(os.path.join(folder, "{}-{}.txt").format(counter, image["hash"]), image["description"])
            counter += 1
        logging.debug("Album complete {}".format(self.link))
        return True

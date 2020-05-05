import re
import os
import time
import urllib.request
from urllib.request import urlopen, Request, urlretrieve
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
from bs4 import BeautifulSoup as soup
import logging

from resources.parser import Parser
from resources.save import Save


class Common:
    valid_url = r'((.)+\.(?P<ext>jpg|png|gif|jpeg|bmp|tiff|webp|mp4|mov|mpeg|3gp|mp3|flac|ogg))|(https?://i.reddituploads.com/(.)+)'

    def __init__(self, link, name, template_data):
        self.logger = logging.getLogger(__name__)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')]
        urllib.request.install_opener(opener)
        self.link = link
        self.name = name
        self.template_data = template_data
        self.load_config()
        self.saveDir = Save()
        self.direct = ""

    def load_config(self):
        parser = Parser()
        data = parser.config

        try:
            int(data["media_download"]["retries"])
            int(data["media_download"]["wait_time"])
            self.retries = data["media_download"]["retries"]
            self.wait_time = data["media_download"]["wait_time"]

        except TypeError:
            self.logger.warning("TypeError: Media download retries or wait time is not an integer.")
            self.retries = 5
            self.wait_time = 60

    def save(self):
        if '.gifv' in self.link:
            ext = '.mp4'
            self.link = self.link.replace('gifv', 'mp4')
        elif 'i.reddituploads.com' in self.link:
            ext = '.jpeg'
        else:
            ext = '.' + re.search(self.valid_url, self.link).group('ext')
        self.template_data["ext"] = ext
        self.direct = self.saveDir.get_dir(self.template_data)
        self.logger.debug("Saving {} with extension {}".format(self.link, ext))

        if not self.save_image():
            return False
        return True

    def save_image(self, current_retry=1):
        try:
            urlretrieve(self.link, self.direct)
        except (URLError, RemoteDisconnected, ConnectionResetError) as e:
            if self.retries > current_retry:
                self.logger.warning("{}, retrying {}".format(str(e), self.link))
                time.sleep(self.wait_time)
                current_retry += 1
                self.save_image(current_retry)
            else:
                self.logger.error("{}, failed {}".format(str(e), self.link))
                return False
        except Exception as e:
            if self.retries > current_retry:
                self.logger.error("{}, retrying {}".format(str(e), self.link))
                time.sleep(self.wait_time)
                current_retry += 1
                self.save_image(current_retry)
            else:
                self.logger.error("{}, failed {}".format(str(e), self.link))
                return False
        return True

    def get_html(self, headers_param={}):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
        }
        headers.update(headers_param)
        req = Request(
            self.link,
            data=None,
            headers=headers,
        )
        try:
            page_html = urlopen(req).read()
            page_html = soup(page_html, "lxml")
        except (HTTPError, URLError) as e:
            page_html = None
            self.logger.error('{} - Link {}'.format(str(e), self.link))
        return page_html

    def format_name(self, title):
        title = re.sub('[?/|\\\}{:<>*"]', '', title)
        if len(title) > 190:
            title = title[:120]
        return title

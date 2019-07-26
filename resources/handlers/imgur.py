import re
import json
import os
import logging

from .common import Common

class Imgur(Common):
    valid_url = r'https?://(?:i\.|m\.)?imgur\.com/((?:a|(gallery))/)?(?P<id>[a-zA-Z0-9]+)(?P<ext>[^/])*'
    
    def __init__(self, link, name, direct):
        super().__init__(link, name, direct)
        self.data = {}

    def save(self):
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        self.data = self.get_data()
        if self.data:
            if self.data.get('is_album'):
                self.save_album()
            else:
                self.save_single()

    def sanitize_url(self):
        self.link = self.link.replace("m.imgur", "imgur")
        self.link = re.sub('#(.*)', '', self.link)
        ext = re.match(self.valid_url, self.link).group('ext')
        if ext:
            self.link = self.link.replace(ext, "")
        self.logger.debug('Sanitized link {}'.format(self.link))

    def get_data(self):
        '''Returns the JSON file with data on images.'''
        page_html = self.get_html()
        if page_html:
            page_html = page_html.text
            data_string = re.search('image( ){15}: (?P<data>(.)+)', page_html)
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
        self.logger.debug("Saving single image {}".format(self.link))

        self.save_image()
        self.write_description(os.path.join(direct_description,"{}-{}.txt".format(title, self.data["hash"])), self.data["description"])
    
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
            self.save_single()
            return
        folder = os.path.join(self.direct, folder_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        counter = 1
        for image in images:
            self.link = "https://imgur.com/{}{}".format(image["hash"], image["ext"])
            self.direct = os.path.join(folder, "{}-{}{}".format(counter, image["hash"], image["ext"]))

            self.save_image()
            self.write_description(os.path.join(folder,"{}-{}.txt").format(counter,image["hash"]), image["description"])
            
            counter += 1
        logging.debug("Album complete {}".format(self.link))
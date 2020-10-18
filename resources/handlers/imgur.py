import re
import logging
import requests

from .common import Common
from resources.parser import Parser


class Imgur(Common):
    # Tested link formats
    # https://imgur.com/gallery/YhYQ36h
    # https://imgur.com/a/hWjM8
    # https://i.imgur.com/aI3Avr9.jpg
    # https://imgur.com/a/sdHPt (disturbing content, NSFW)
    # https://www.reddit.com/r/pics/comments/j3dbt6/trump_impersonator_crashes_mike_pence_speech_in/

    valid_url = r'https?://(?:i\.|m\.)?imgur\.com/(?P<col>(a|(gallery)|(r/[a-z0-9]+))/)?(/)?(?P<id>[a-zA-Z0-9]+)(?P<ext>\.[^/]+)*'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)
        self.data = {}

    def save(self):
        ret = False
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        self.data = self.get_data()
        if type(self.data) is dict:
            if self.data.get('is_album'):
                ret = self.save_album()
            else:
                ret = self.save_single()
        return ret

    def sanitize_url(self):
        match = re.match(self.valid_url, self.link)
        if match.group('col'):
            self.link = 'https://imgur.com/{}/{}'.format(match.group('col')[:-1], match.group('id'))
        else:
            self.link = 'https://imgur.com/{}'.format(match.group('id'))
        self.logger.debug('Sanitized link {}'.format(self.link))

    def get_data(self):
        '''Returns the JSON file with data on images.'''
        client_id = Parser().config.get("imgur")
        if not client_id.get("client_id"):
            headers = {
                "Authorization": "Client-ID 53bdf7a3b30690b"
            }
        else:
            headers = {
                "Authorization": "Client-ID {}".format(
                    client_id.get("client_id")
                )
            }

        params = {
            "include": "media,tags,account"
        }
        match = re.match(self.valid_url, self.link)
        imgur_id = match.group('id')
        if not match.group("col"):
            url = "https://api.imgur.com/post/v1/media/{}".format(imgur_id)
        else:
            url = "https://api.imgur.com/post/v1/albums/{}".format(imgur_id)

        r = requests.get(url, headers=headers, params=params)
        if r.status_code == requests.codes.ok:
            return r.json()

        self.logger.warning("Imgur API returns a bad status code: {}".format(r.status_code))
        return None

    def write_description(self, txt_file, description):
        if description:
            with open(txt_file, "w+") as f:
                f.write(description)

    def save_single(self):
        self.link = self.data["media"][0]["url"]
        title = self.name
        if self.data.get("title"):
            title = self.data.get("title")
        title = self.format_name(title)
        temporary_template = self.template_data
        temporary_template["ext"] = "txt"
        temporary_template["id"] = self.data["id"]
        direct_description = self.saveDir.get_dir(temporary_template)
        temporary_template["ext"] = self.data["media"][0]["ext"].replace(".", "")
        self.direct = self.saveDir.get_dir(temporary_template)

        self.logger.debug("Saved single image {}".format(self.link))

        if not self.save_image():
            return False
        self.write_description(direct_description, self.data["description"])
        return True

    def save_album(self):
        album_id = self.link.rsplit('/', 1)[-1]
        if '#' in album_id:
            album_id = album_id.rsplit('#', 1)[-2]

        self.logger.debug(
            "Saving album {} - album_id {}".format(self.link, album_id)
        )
        if self.data["title"]:
            folder_name = self.format_name(self.data["title"])
        else:
            folder_name = self.format_name(self.format_name(self.name) + " - " + album_id)
        try:
            images = self.data["media"]
        except KeyError:
            if not self.save_single():
                return False
            return True

        counter = 1
        for image in images:
            self.link = image["url"]
            temporary_template = self.template_data
            temporary_template["ext"] = image["ext"].replace(".", "")
            temporary_template["id"] = image["id"]
            temporary_template["title"] = counter
            self.direct = self.saveDir.get_dir(temporary_template, prepend_path=folder_name, prepend_name=str(counter) + "-")
            if not self.save_image():
                return False
            try:
                temporary_template["ext"] = "txt"
                temporary_template["id"] = self.data["id"]
                temporary_template["title"] = counter
                direct_description = self.saveDir.get_dir(temporary_template, prepend_path=folder_name)
                self.write_description(direct_description, image["metadata"]["description"])
            except OSError as e:
                self.logger.error("OS Error: writing desctipion {}".format(str(e)))
                return False
            counter += 1
        logging.debug("Album complete {}".format(self.link))
        return True

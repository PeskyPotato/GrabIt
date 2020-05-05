import re
import os
import logging

from .common import Common


class Giphy(Common):
    valid_url = r'https?://giphy\.com/gifs/((?P<name>[\w-]+)-)*(?P<id>(\w)+$)'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        gif_id = self.sanitize_url()
        temporary_data = self.template_data
        temporary_data["ext"] = "gif"
        temporary_data["id"] = gif_id
        self.direct = self.saveDir.get_dir(self.template_data)
        self.logger.debug("Saving {}".format(self.link))
        if not self.save_image():
            return False
        return True

    def sanitize_url(self):
        gif_id = re.match(self.valid_url, self.link).group('id')
        self.link = 'https://media.giphy.com/media/{}/giphy.gif'.format(gif_id)
        return gif_id

import re
import json
import os
import logging

from .common import Common

class Giphy(Common):
    valid_url = r'https?://giphy\.com/gifs/((?P<name>[\w-]+)-)*(?P<id>(\w)+$)'
    
    def __init__(self, link, name, direct):
        self.logger = logging.getLogger(__name__)

        super().__init__(link, name, direct)

    def save(self):
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        super().save()

    def sanitize_url(self):
        gif_id = re.match(self.valid_url, self.link).group('id')
        self.link = 'https://media.giphy.com/media/{}/giphy.gif'.format(gif_id)



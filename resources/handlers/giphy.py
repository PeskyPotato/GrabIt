import re
import os
import logging

from .common import Common


class Giphy(Common):
    valid_url = r'https?://giphy\.com/gifs/((?P<name>[\w-]+)-)*(?P<id>(\w)+$)'

    def __init__(self, link, name, direct):
        self.logger = logging.getLogger(__name__)
        super().__init__(link, name, direct)

    def save(self):
        gif_id = self.sanitize_url()
        self.direct = os.path.join(self.direct, '{}-{}.gif'.format(gif_id, self.format_name(self.name)))
        self.logger.debug("Saving {}".format(self.link))
        if not self.save_image():
            return False
        return True

    def sanitize_url(self):
        gif_id = re.match(self.valid_url, self.link).group('id')
        self.link = 'https://media.giphy.com/media/{}/giphy.gif'.format(gif_id)
        return gif_id

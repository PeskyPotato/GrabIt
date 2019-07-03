import re
import json
import os
import logging

from .common import Common

class Giphy(Common):
    
    def __init__(self, link, name, direct):
        self.logger = logging.getLogger(__name__)

        super().__init__(link, name, direct)

    def save(self):
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        super().save()

    def sanitize_url(self):
        self.link = 'https://media.giphy.com/media/' + self.link.split('-', 2)[-1] + '/giphy.gif'

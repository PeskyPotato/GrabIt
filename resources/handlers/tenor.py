import re
import json
import os
import logging

from .common import Common

class Tenor(Common):
    
    def __init__(self, link, name, direct):
        self.logger = logging.getLogger(__name__)

        super().__init__(link, name, direct)

    def save(self):
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        self.link = self.get_data()
        if self.link:
            super().save()
        else:
            return None

    def sanitize_url(self):
        self.link = self.link.replace("http:", "https")
    
    def get_data(self):
        page_html = self.get_html()
        if page_html:
            mp4_link = page_html.find("meta", {"property":"og:video"})
            return mp4_link["content"]
        return None

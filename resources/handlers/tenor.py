import os
import logging

from .common import Common


class Tenor(Common):
    valid_url = r'https?://tenor\.com/view/(?P<name>[\w-]+)-(?P<id>(\w)+$)'

    def __init__(self, link, name, direct):
        self.logger = logging.getLogger(__name__)

        super().__init__(link, name, direct)

    def save(self):
        self.sanitize_url()
        self.logger.debug("Saving {}".format(self.link))
        self.link = self.get_data()
        if self.link:
            self.direct = os.path.join(self.direct, self.format_name(self.name) + '.mp4')

            self.logger.debug("Saving {} with extension {}".format(self.link, '.mp4'))

            if not self.save_image():
                return False
            return True
        else:
            return False

    def sanitize_url(self):
        self.link = self.link.replace("http:", "https:")

    def get_data(self):
        page_html = self.get_html()
        if page_html:
            mp4_link = page_html.find("meta", {"property":"og:video"})
            return mp4_link["content"]
        return None

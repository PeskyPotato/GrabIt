import json

from .common import Common
from .youtube import YouTube


class Redgifs(Common):
    valid_url = r'https?://(?:www\.)redgifs\.com/watch/((?P<name>[\w-]+))'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        page = self.get_html()
        if not page:
            return False
        self.logger.debug("Fetching redgifs json data")
        data = json.loads(page.find("script",
                                    {"type": "application/ld+json"}).text)
        self.link = data["video"]["contentUrl"]
        self.valid_url = super().valid_url
        return YouTube(self.link, self.name, self.template_data).save()

    def sanitize_url(self):
        pass

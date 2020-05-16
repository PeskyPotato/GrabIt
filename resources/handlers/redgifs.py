import json

from .common import Common


class Redgifs(Common):
    valid_url = r'https?://redgifs\.com/watch/((?P<name>[\w-]+))'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        page = self.get_html()
        self.logger.debug("Fetching redgifs json data")
        data = json.loads(page.find("script",
                                    {"type": "application/ld+json"}).text)
        self.link = data["video"]["contentUrl"]
        self.valid_url = super().valid_url
        return super().save()

    def sanitize_url(self):
        pass

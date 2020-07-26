import requests

from .common import Common
from .youtube import YouTube


class Gfycat(Common):
    valid_url = r'https?://(?:(?:www|giant|thumbs)\.)?gfycat\.com/(?:fr/|ru/|ifr/|gifs/detail/)?(?P<id>[^-/?#\.]+)'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        page = self.get_html()
        url = page.find("meta", {"property": "og:video"}).get("content", "")
        self.link = url
        self.valid_url = super().valid_url
        return super().save()

    def sanitize_url(self):
        pass

from .common import Common


class Gfycat(Common):
    valid_url = r'https?://(?:(?:www|giant|thumbs)\.)?gfycat\.com/(?:fr/|ru/|ifr/|gifs/detail/)?(?P<id>[^-/?#\.]+)'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        page = self.get_html()
        if not page:
            return False
        url = page.find("meta", {"property": "og:video"})
        if not url:
            return False
        url = url.get("content", "")
        self.link = url
        self.valid_url = super().valid_url
        return super().save()

    def sanitize_url(self):
        pass

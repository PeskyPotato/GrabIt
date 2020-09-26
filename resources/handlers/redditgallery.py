import re

from .common import Common


class RedditGallery(Common):
    valid_url = r'https?://(www\.)?reddit\.com/gallery/(?P<id>[^-/?#\.]+)'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        page = self.get_html()
        if not page:
            return False
        figures = page.find_all("figure")
        counter = 0
        for figure in figures:
            img = figure.find("a")
            self.link = img.get("href", "")
            img_reg = r'(.)*redd.it/(?P<id>[^-/?#\.]+).(.)*'
            match = re.match(img_reg, self.link)
            if not match.group("id"):
                return False

            temporary_template = self.template_data
            temporary_template["ext"] = "webp"
            temporary_template["id"] = match.group("id")
            temporary_template["title"] = counter

            folder_name = self.format_name(self.name)
            self.direct = self.saveDir.get_dir(
                temporary_template, prepend_path=folder_name,
                prepend_name=str(counter) + "-"
            )

            if not self.save_image():
                return False

            counter += 1
        return True

    def sanitize_url(self):
        pass

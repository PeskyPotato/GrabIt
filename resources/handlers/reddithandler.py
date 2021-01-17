import re
from .common import Common
from resources.interfaces.reddit_instance import RedditInstance


class RedditHandler(Common):
    valid_url = r'(.)*/comments/(?P<submission_id>[a-zA-z0-9]+)/(.)*$'

    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        reddit = RedditInstance().reddit
        match = re.match(self.valid_url, self.link)
        if not match:
            return False
        self.logger.debug("Fetching submission data")
        submission = reddit.submission(id=match.group("submission_id"))
        return submission

    def sanitize_url(self):
        pass

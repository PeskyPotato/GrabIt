import logging
import requests
import re
from collections import namedtuple


class Pushshift():
    subreddit_regex = r'\/?r\/(?P<subreddit>.+)'

    def __init__(self, subR, parser):
        self.logger = logging.getLogger(__name__)

        self.subR = subR
        self.parser = parser

    def queue(self, before, size):
        if re.match(self.subreddit_regex, self.subR):
            self.subR = re.match(self.subreddit_regex, self.subR).group('subreddit')
        url = 'https://api.pushshift.io/reddit/search/submission/?subreddit={}&before={}&size={}'.format(self.subR, int(float(before)), size)
        r = requests.get(url)
        submissions = r.json()

        submissions_queue = []
        if submissions:
            count = 0
            for submission in submissions["data"]:
                submissions_queue.append(namedtuple('Submission', submission.keys())(*submission.values()))
                count += 1
            self.logger.debug("Pushshift API submission: {}".format(count))
        return submissions_queue

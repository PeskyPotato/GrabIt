import logging
import requests
import re
from collections import namedtuple


class Pushshift():
    user_regex = r'\/?u\/(?P<user>.+)'
    subreddit_regex = r'\/?r\/(?P<subreddit>.+)'
    submissions_queue = []

    def __init__(self, subR, parser):
        self.logger = logging.getLogger(__name__)

        self.subR = subR
        self.parser = parser

    def get_submissions(self, url):
        '''
        Takes url with Pushshift parameters and gets JSON data. Formats the
        JSON data to submission objects and appends to self.submission_queue.
        '''
        r = requests.get(url)
        submissions = r.json()

        if submissions:
            count = 0
            for submission in submissions["data"]:
                self.submissions_queue.append(namedtuple('Submission', submission.keys())(*submission.values()))
                count += 1
            self.logger.debug("Pushshift API submission count: {}".format(count))

    def generate_submissions(self, size, before=''):
        '''
        Recursively gets _size_ number of submissions using the 'before' param
        if _size_ is greater than 500.
        '''
        params = '&over_18=false'
        if self.parser.allow_nsfw:
            params = ''  # both nsfw and sfw by default

        if before:
            params += "&before=" + before

        if size > 500:
            cur_size = 500
            size -= 500
        else:
            cur_size = size
            size = 0

        url = 'https://api.pushshift.io/reddit/search/submission/'\
              '?subreddit={}&q={}&size={}{}'.format(self.subR, self.parser.search, cur_size, params)
        self.get_submissions(url)

        if size != 0:
            if len(self.submissions_queue) > 0:
                before = str(self.submissions_queue[-1].created_utc)
            self.generate_submissions(size, before)

    def queue(self):
        posts = self.parser.posts
        search = self.parser.search

        if search:
            self.logger.debug('Search term: {}'.format(search))
            if re.match(self.user_regex, self.subR):
                self.logger.warning('Cannot search redditors: {}'.format(self.subR))
            else:
                posts = min(posts, 2000)  # prevents overloading api
                self.generate_submissions(posts)
        else:
            self.logger.warning("--pushshift currently only supports search")

        return self.submissions_queue

    def queue_append(self, before, size):
        '''
        Called when Reddit API used and greater than 1000 submissions are
        needed frpm a subreddit when sorting by new.
        '''
        if re.match(self.subreddit_regex, self.subR):
            self.subR = re.match(self.subreddit_regex, self.subR).group('subreddit')
        url = 'https://api.pushshift.io/reddit/search/submission/'\
              '?subreddit={}&before={}&size={}'.format(self.subR, int(float(before)), size)
        self.get_submissions(url)
        return self.submissions_queue

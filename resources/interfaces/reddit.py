import praw
import logging
import sys
import traceback
from prawcore import exceptions


class Reddit():
    def __init__(self, subR, parser):
        self.logger = logging.getLogger(__name__)

        self.subR = subR
        self.parser = parser

    def queue(self):
        posts = self.parser.posts
        sort = self.parser.sort
        search = self.parser.search
        config = self.parser.config

        try:
            reddit = praw.Reddit(
                client_id=config["reddit"]["creds"]["client_id"],
                client_secret=config["reddit"]["creds"]["client_secret"],
                user_agent=config["reddit"]["creds"]["user_agent"]
            )

            submissions = []

            # search term given
            if search:
                self.logger.debug('Search term: {}'.format(search))
                if 'u/' in self.subR or '/u/' in self.subR:
                    self.logger.warning('Cannot search redditors: {}'.format(self.subR))
                else:
                    include_over_18 = 'off'
                    if self.parser.allow_nsfw:
                        include_over_18 = 'on'
                    submissions = reddit.subreddit(self.subR).search(search, sort=sort.lower(),
                        limit=int(posts), time_filter=self.parser.time_filter, params={'include_over_18': include_over_18})

            # user or subreddit given
            elif 'reddit.com' not in self.subR:
                if 'u/' in self.subR or '/u/' in self.subR:
                    if '/u/' in self.subR:
                        self.subR = self.subR[3:]
                    elif 'u/'in self.subR:
                        self.subR = self.subR[2:]
                    if sort == 'hot':
                        submissions = reddit.redditor(self.subR).submissions.hot(limit=int(posts))
                    elif sort == 'new':
                        submissions = reddit.redditor(self.subR).submissions.new(limit=int(posts))
                    elif sort == 'top':
                        submissions = reddit.redditor(self.subR).submissions.top(limit=int(posts), time_filter=self.parser.time_filter)
                    elif sort == 'controversial':
                        submissions = reddit.redditor(self.subR).submissions.controversial(limit=int(posts), time_filter=self.parser.time_filter)

                else:
                    if sort == 'hot':
                        submissions = reddit.subreddit(self.subR).hot(limit=int(posts))
                    elif sort == 'new':
                        submissions = reddit.subreddit(self.subR).new(limit=int(posts))
                    elif sort == 'top':
                        submissions = reddit.subreddit(self.subR).top(limit=int(posts), time_filter=self.parser.time_filter)
                    elif sort == 'controversial':
                        submissions = reddit.subreddit(self.subR).controversial(limit=int(posts), time_filter=self.parser.time_filter)

            # single submission given
            else:
                submissions = [reddit.submission(url=self.subR)]

        except exceptions.ResponseException as err:
            if "received 401 HTTP response" in str(err):
                self.logger.error("{} Check Reddit API credentials".format(err))
            elif "Redirect to /subreddits/search" in str(err):
                self.logger.error("{} Subreddit does not exist".format(err))
            else:
                self.logger.error(str(traceback.TracebackException.from_exception(err)) + " Check username, subreddit or url: " + self.subR)
        except praw.exceptions.ClientException as err:
            self.logger.error(err)
            sys.exit()

        return submissions

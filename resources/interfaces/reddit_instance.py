import sys
import logging
import praw
from prawcore import exceptions
from resources.parser import Parser


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class RedditInstance(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        parser = Parser()
        self.config = parser.config
        self.reddit = None
        self.start_reddit()

    def start_reddit(self):
        self.logger.debug("Initialising Reddit")
        try:
            self.reddit = praw.Reddit(
                client_id=self.config["reddit"]["creds"]["client_id"],
                client_secret=self.config["reddit"]["creds"]["client_secret"],
                user_agent=self.config["reddit"]["creds"]["user_agent"]
            )
        except exceptions.ResponseException as err:
            self.logger.error("{} Check Reddit API credentials".format(err))
            sys.exit(0)

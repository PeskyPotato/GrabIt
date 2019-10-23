import argparse
import json
import logging
import sys
import os

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

class Parser(metaclass=Singleton):
    def __init__(self):
        if not (os.path.isfile("./resources/config.json")):
            self.initConfig()

        with open("./resources/config.json") as config_json:
            self.config = json.load(config_json)

        parser = argparse.ArgumentParser(description="Archives submissions from Reddit")
        parser.add_argument(
            "subreddit",
            nargs="?",
            help="Enter a subreddit, user, submission url or text file to backup",
        )
        parser.add_argument("-p", "--posts", help="Number of posts to grab on each cycle")
        parser.add_argument("--search", help="Search for submissions in a subreddit")
        parser.add_argument("--sort", help='Sort submissions by "relevance", "comments", "hot", "new", "top", or "controversial"')
        parser.add_argument("--time_filter", help='Filter sorted submissions by "all", "day", "hour", "month", "week", or "year"')
        parser.add_argument("-w", "--wait", help="Wait time in seconds between each cycle")
        parser.add_argument("-c", "--cycles", help="Number to times to repeat after wait time")
        parser.add_argument("-o", "--output", help="Set base directory")
        parser.add_argument("-t", "--output_template", help="Specify output template")
        parser.add_argument("--allow_nsfw", help="Include nsfw posts", action="store_true")
        parser.add_argument("-v", "--verbose", help="Set verbose", action="store_true")
        parser.add_argument("--blacklist", help="Avoid downloading a user or subreddit")
        parser.add_argument("--reddit_id", help="Reddit client ID")
        parser.add_argument("--reddit_secret", help="Reddit client secret")
        parser.add_argument("--imgur_cookie", help="Imgur authautologin cookie")
        parser.add_argument("--db_location", help="Set location of database file")

        self.args = parser.parse_args()

        self.subreddit = self.args.subreddit
        self.allow_nsfw = self.args.allow_nsfw
        self.verbose = self.args.verbose
    
    def initConfig(self):
        text = input("Config file does not exist\nWould you like to create one? [Y/n]")
        if text == "" or text.strip()[0].lower() == 'y':
            config = {
                "general": {
                    "database_location": "./downloaded.db",
                    "logger_append": False,
                    "log_file": "./grabber.log",
                    "log_timestamp": False
                },
                "reddit": {
                    "creds": {
                        "client_id": "",
                        "client_secret": "",
                        "user_agent": "Downloads submissions by user/subreddit"
                    },
                    "blacklist": []
                },
                "media_download": {
                    "retries": 3,
                    "wait_time": 60
                }
            }
            client_id = input("Enter Reddit client ID: ")
            config["reddit"]["creds"]["client_id"] = client_id.strip()
            client_secret = input("Enter Reddit client secret: ")
            config["reddit"]["creds"]["client_secret"] = client_secret.strip()
            with open('./resources/config.json', 'w') as f:
                json.dump(config, f)
        else:
            print("Quiting")
            sys.exit(0)


    def checkArgs(self):
        # wait
        if self.args.wait and self.args.subreddit:
            try:
                self.wait = int(self.args.wait)
            except ValueError:
                self.logger.error("Please enter an integer in seconds to wait")
                sys.exit()
        else:
            self.wait = self.config["general"]["wait_time"]
        self.logger.debug("Wait time set to  {} seconds".format(self.wait))

        # cycles
        if self.args.cycles and self.args.subreddit:
            try:
                self.cycles = int(self.args.cycles)
            except ValueError:
                self.logger.error("Please enter an integer in seconds to wait")
                sys.exit()
        else:
            self.cycles = self.config["general"]["cycles"]
        self.logger.debug("Cycles set to {}.".format(self.cycles))

        # posts
        if self.args.posts and self.args.subreddit:
            try:
                self.posts = int(self.args.posts)
            except ValueError:
                self.logger.error("Please enter an inter for the number of posts")
                sys.exit()
        else:
            self.posts = self.config["general"]["posts"]
        self.logger.debug("Posts to download set to {}".format(self.posts))

        # output, sets base_dir
        if self.args.output and self.args.subreddit:
            self.base_dir = os.path.abspath(self.args.output)
            self.ifNotExistMakeDir(self.base_dir)
        else:
            self.base_dir = os.getcwd()
        self.output = self.args.output
        self.logger.debug("Base directory for download set to {}".format(self.base_dir))

        # search
        self.search = None
        if self.args.search:
            self.search = self.args.search
        self.logger.debug('Reddit search set to "{}"'.format(self.search))

        # sort
        self.sort = self.config["general"]["sort"]
        if (
            self.args.sort
            and (
                self.args.sort.lower() == "relevance"
                or self.args.sort.lower() == "new"
                or self.args.sort.lower() == "top"
                or self.args.sort.lower() == "comments"
            )
            and self.args.subreddit
            and self.args.search
        ):
            self.sort = self.args.sort.lower()
        elif (
            self.args.sort
            and (
                self.args.sort.lower() == "hot"
                or self.args.sort.lower() == "new"
                or self.args.sort.lower() == "top"
                or self.args.sort.lower() == "controversial"
            )
            and self.args.subreddit
        ):
            self.sort = self.args.sort.lower()
        elif self.args.sort and self.subreddit:
            self.logger.error("Incorrect use of sort: {}\nCheck https://github.com/LameLemon/GrabIt for help".format(self.args.sort.lower()))
            sys.exit()
        self.logger.debug("Reddit sorting set to {}".format(self.sort))

        # time_filter
        self.time_filter = self.config["general"]["time_filter"]
        if (
            self.args.time_filter
            and (
                self.args.time_filter.lower() == "all"
                or self.args.time_filter.lower() == "day"
                or self.args.time_filter.lower() == "hour"
                or self.args.time_filter.lower() == "month"
                or self.args.time_filter.lower() == "week"
                or self.args.time_filter.lower() == "year"
            )
            and self.args.subreddit
        ):
            self.time_filter = self.args.time_filter.lower()
        elif self.args.time_filter and self.subreddit:
            self.logger.error("Please enter all, day, hour, month, week, or year for time_filter")
            sys.exit()
        self.logger.debug("Reddit time_filter set to {}".format(self.time_filter))

        # blacklist
        if self.args.blacklist:
            self.config["reddit"]["blacklist"].append(self.args.blacklist)
            self.logger.info('Added "{}" to the blacklist'.format(self.args.blacklist))

        # reddit api credentials
        if self.args.reddit_id:
            self.config["reddit"]["creds"]["client_id"] = self.args.reddit_id
        if self.args.reddit_secret:
            self.config["reddit"]["creds"]["client_secret"] = self.args.reddit_secret
        
        # imgur authautologin cookie
        if self.args.imgur_cookie:
            if not self.config.get("imgur"):
                self.config["imgur"] = {
                   "authautologin": self.args.imgur_cookie
                }            
            else:
                self.config["imgur"]["authautologin"] = self.args.imgur_cookie
        
        # set database location
        if self.args.db_location:
            self.config["general"]["database_location"] = self.args.db_location
            db_path = self.args.db_location[:self.args.db_location.rfind('/')]
            self.ifNotExistMakeDir(db_path)
            self.db_location = self.args.db_location


        # writes config to json file (used by other classes)
        with open("./resources/config.json", "w") as config_json:
            json.dump(self.config, config_json)

        # output template
        if self.args.output_template:
            self.template = self.args.output_template
        else:
            self.template = os.path.join("%(subreddit)s", "%(author)s")

    def setupLogger(self):
        """ Called after logger initialised """
        self.logger = logging.getLogger(__name__)

    def ifNotExistMakeDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)


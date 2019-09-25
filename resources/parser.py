import argparse
import json
import logging
import sys
import os


class Parser:
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
        parser.add_argument("--sort", help='Sort submissions by "hot", "new", "top", or "controversial"')
        parser.add_argument("-w", "--wait", help="Wait time in seconds between each cycle")
        parser.add_argument("-c", "--cycles", help="Number to times to repeat after wait time")
        parser.add_argument("-o", "--output", help="Set base directory")
        parser.add_argument("-t", "--output_template", help="Specify output template")
        parser.add_argument("-v", "--verbose", help="Set verbose", action="store_true")
        parser.add_argument("--blacklist", help="Avoid downloading a user or subreddit")
        parser.add_argument("--reddit_id", help="Reddit client ID")
        parser.add_argument("--reddit_secret", help="Reddit client secret")

        self.args = parser.parse_args()

        self.subreddit = self.args.subreddit
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
            self.wait = 600
        self.logger.debug("Wait time set to  {} seconds".format(self.wait))

        if self.args.cycles and self.args.subreddit:
            try:
                self.cycles = int(self.args.cycles)
            except ValueError:
                self.logger.error("Please enter an integer in seconds to wait")
                sys.exit()
        else:
            self.cycles = 1
        self.logger.debug("Cycles set to {}.".format(self.cycles))

        # posts
        if self.args.posts and self.args.subreddit:
            try:
                self.posts = int(self.args.posts)
            except ValueError:
                self.logger.error("Please enter an inter for the number of posts")
                sys.exit()
        else:
            self.posts = 50
        self.logger.debug("Posts to download set to {}".format(self.posts))

        # output, sets base_dir
        if self.args.output and self.args.subreddit:
            self.base_dir = os.path.abspath(self.args.output)
            if not os.path.exists(self.base_dir):
                os.makedirs(self.base_dir)
        else:
            self.base_dir = os.getcwd()
        self.output = self.args.output
        self.logger.debug("Base directory for download set to {}".format(self.base_dir))

        # sort
        self.sort = "hot"
        if (
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
            self.logger.error("Please enter hot, new or top for sort")
            sys.exit()
        self.logger.debug("Reddit sorting set to {}".format(self.sort))

        # search
        self.search = None
        if self.args.search:
            self.search = self.args.search
        self.logger.debug('Reddit search set to "{}"'.format(self.search))

        # blacklist
        if self.args.blacklist:
            self.config["reddit"]["blacklist"].append(self.args.blacklist)
            self.logger.info('Added "{}" to the blacklist'.format(self.args.blacklist))

        if self.args.reddit_id:
            self.config["reddit"]["creds"]["client_id"] = self.args.reddit_id
        if self.args.reddit_secret:
            self.config["reddit"]["creds"]["client_secret"] = self.args.reddit_secret

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
        self.logger.debug("it's all gucci")

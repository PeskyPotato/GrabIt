import os
import json


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


class Config(metaclass=Singleton):

    default_config = {
            "general": {
                "database_location": os.path.join(os.path.dirname(__file__), "..", "downloaded.db"),
                "logger_append": False,
                "log_file": os.path.join(os.path.abspath(os.getcwd()), "grabber.log"),
                "log_timestamp": False,
                "wait_time": 600,
                "cycles": 1,
                "posts": 50,
                "sort": "hot",
                "time_filter": "all"
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
            },
            "imgur": {
                "authautologin": ""
            }
        }

    def __init__(self, path):
        self.config_path = path

        self.config = {}
        if not os.path.isfile(self.config_path):
            print("Created config")
            self.create_config()
        else:
            self.load_config()

    def create_config(self):
        self.config = self.default_config
        self.write_config()

    def write_config(self):
        with open(self.config_path, "w+") as f:
            json.dump(self.config, f)

    def load_config(self):
        with open(self.config_path, "r") as f:
            self.config = json.load(f)

        ''' only checks top level keys '''
        for k in self.default_config.keys():
            if k not in self.config:
                self.config[k] = self.default_config[k]

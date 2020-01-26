import os
import sys
import logging

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

class Save(metaclass=Singleton):
    def __init__(self, base_dir, template):
        self.logger = logging.getLogger(__name__)
        self.base_dir = base_dir
        self.template = template

    def get_dir(self, data):
        try:
            path = self.template % data
        except KeyError as e:
            self.logger.error('KeyError: Incorrect template output ' + str(e))
            sys.exit('Exiting: Incorrect template output')

        folder = os.path.join(self.base_dir, path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.logger.debug('Saving to ' + folder)
        return folder

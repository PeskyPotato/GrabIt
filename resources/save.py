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

    def get_dir(self, data, prepend_path=None, prepend_name=""):
        try:
            path = self.template % data
        except KeyError as e:
            self.logger.error('KeyError: Incorrect template output ' + str(e))
            sys.exit('Exiting: Incorrect template output')
        
        folder = os.path.join(self.base_dir, path)
        if prepend_path:
            folder_split = os.path.split(folder)
            folder = os.path.join(folder_split[0], prepend_path, prepend_name + folder_split[1]) 
        if not os.path.exists(os.path.dirname(folder)):
            os.makedirs(os.path.dirname(folder))
        self.logger.debug('Saving to ' + folder)
        return folder

import os
import sys
import logging


class Save:
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

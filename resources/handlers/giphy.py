import re
import json
import os

from .common import Common

class Giphy(Common):
    
    def __init__(self, link, name, direct):
        super().__init__(link, name, direct)

    def save(self):
        self.sanitize_url()
        super().save()

    def sanitize_url(self):
        self.link = 'https://media.giphy.com/media/' + self.link.split('-', 2)[-1] + '/giphy.gif'

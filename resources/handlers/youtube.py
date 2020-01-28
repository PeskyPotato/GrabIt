import re
import json
import os
import logging
import youtube_dl

from .common import Common
from resources.parser import Parser


class YouTube(Common):
    
    def __init__(self, link, name, direct):
        super().__init__(link, name, direct)

    def save(self):
        downloaded = True
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.direct, '%(id)s-%(title)s.%(ext)s'),
            'quiet': 'quiet'
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link])
        except youtube_dl.utils.DownloadError:
            self.logger.info("No matches: {}".format(self.link))
            downloaded = False
        except Exception as e:
            self.logger.error('Exception {} on {}'.format(e, self.link))
            downloaded = False

        return downloaded

    @staticmethod
    def yt_supported(url):
        extractors = youtube_dl.extractor.gen_extractors()
        for extractor in extractors:
            if extractor.suitable(url) and extractor.IE_NAME != 'generic':
                return True
        return False

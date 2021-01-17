import re
import json
import os
import logging
import youtube_dl

from .common import Common
from resources.parser import Parser


class YouTube(Common):
    
    def __init__(self, link, name, template_data):
        super().__init__(link, name, template_data)

    def save(self):
        downloaded = True
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'retries': 10,
            'outtmpl': os.path.join(os.path.dirname(self.saveDir.get_dir(self.template_data)), "%(id)s-%(title)s.%(ext)s"),
            'quiet': 'quiet',
            'progress_hooks': [self.progress],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link])
        except youtube_dl.utils.DownloadError as e:
            self.logger.info("No matches: {}".format(self.link))
            downloaded = False
        except Exception as e:
            self.logger.error('Exception {} on {}'.format(e, self.link))
            downloaded = False

        return downloaded

    def progress(self, d):
        if d["status"] == "downloading":
            print(d["_percent_str"], end="\r")

    @staticmethod
    def yt_supported(url):
        extractors = youtube_dl.extractor.gen_extractors()
        for extractor in extractors:
            if extractor.suitable(url) and extractor.IE_NAME != 'generic':
                return True
        return False

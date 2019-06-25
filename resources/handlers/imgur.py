import re
import json
import os

from .common import Common

class Imgur(Common):
    
    def __init__(self, link, name, direct):
        super().__init__(link, name, direct)
        self.data = {}
        self.save()

    def save(self):
        self.sanitize_url()
        self.data = self.get_data()
        if self.data:
            if 'gallery' in self.link or 'a' in self.link:
                self.save_album()
            else:
                self.save_single()

    def sanitize_url(self):
        self.link = self.link.replace("m.imgur", "imgur")

    def get_data(self):
        '''Returns the JSON file with data on images.'''
        page_html = self.get_html()
        if page_html:
            data_string = re.search('item: (.)+\n( ){12}};', page_html)
            if data_string:
                data_string = data_string.group(0)[5:-2]
                data = json.loads(data_string)
                return data
        return None
    
    def write_description(self, txt_file, description):
        if description:
            with open(txt_file, "w+") as f:
                f.write(description)

    def save_single(self):
        self.link = "https://imgur.com/{}{}".format(self.data["hash"], self.data["ext"])
        self.direct = os.path.join(self.direct, "{}-{}{}".format(self.format_name(self.data["title"]), self.data["hash"], self.data["ext"]))
        
        self.save_image()
        self.write_description(os.path.join(self.direct,"{}-{}.txt".format(self.format_name(self.data["title"]), self.data["hash"])), self.data["description"])
    
    def save_album(self):
        album_id = self.link.rsplit('/', 1)[-1]
        if '#' in album_id:
            album_id = album_id.rsplit('#', 1)[-2]

        if self.data["title"]:
            folder_name = self.format_name(self.data["title"])
        else:
            folder_name = self.format_name(self.format_name(self.name) + " - " + album_id)
        
        images = self.data["album_images"]["images"]
        
        folder = os.path.join(self.direct, folder_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        counter = 1
        for image in images:
            self.link = "https://imgur.com/{}{}".format(image["hash"], image["ext"])
            self.direct = os.path.join(folder, "{}-{}{}".format(counter, image["hash"], image["ext"]))

            self.save_image()
            self.write_description(os.path.join(folder,"{}-{}.txt").format(counter,image["hash"]), image["description"])
            
            counter += 1
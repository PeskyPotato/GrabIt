import imgurpython
from creds import *
import urllib.request
import re
import os
import time

retry_counter = 5

'''
Saves individual images into the assigned directory.
If a URLError or HTTPError occurs it retries before logging
the error.
'''
def saveImage(link, name, direct, counter = 1):
    if 'gifv' in link:
        ext = '.mp4'
        link = link.replace('gifv', 'mp4')
    else:
        ext = re.search('jpg|png|gif', link).group()
    try:
        urllib.request.urlretrieve(link, os.path.join(direct,  name + ext))
    except (urllib.error.URLError, urllib.error.HTTPError) as err:
        if retry_counter > counter:
            print(err, "retrying", counter, link)
            time.sleep(60)
            counter += 1
            saveImage(link, name, direct, counter)
        else:
            with open(os.path.join(direct, 'error.txt'), 'a+') as logFile:
                logFile.write('{}: {}\n'.format(err, link))
    except FileNotFoundError as err:
        # this means album was not found, fix pending
        with open(os.path.join(direct, 'error.txt'), 'a+') as logFile:
            logFile.write('{}: {}\n'.format(err, link))
            


'''
Saves entire imgur albums into the assigned directory.
Writes the descrption to a text file if there is one. Retries
five times if a URLError occurs before logging the error.
'''
def saveAlbum(album, sub_title, direct):
    counter = 0
    client = imgurpython.ImgurClient(Im_client_id, Im_client_secret) #Imgur client
    try:
        try:
            album_data = client.get_album(album) #Whole album images + data
        except imgurpython.helpers.error.ImgurClientError: #Album with only one image
            saveImage('https://imgur.com/' + album + '.jpg', sub_title, direct)
            return

        folderName = album_data.title #album title

        if not folderName:
            folderName = formatName(sub_title + " - " + str(album))
        else:
            folderName = formatName(folderName.replace(' ', '_'))

        images = client.get_album_images(album)

        for image in images:
            folder = os.path.join(direct, str(folderName))

            if not os.path.exists(folder):
                os.makedirs(folder)

            writeDescription(image.description, image.id, folder, counter)
            type = image.type
            type = type.replace('image/', '.')
            type = type.replace('video/', '.')

            counter_ = 0
            while (True):
                try:
                    urllib.request.urlretrieve(image.link, os.path.join(folder, "(" + str(counter) + ") " + str(image.id) + type))
                except urllib.error.URLError:
                    counter_ += 1
                    if retry_counter > counter_:
                        pass
                    else:
                        with open(os.path.join(direct, 'error.txt'), 'a+') as logFile:
                            logFile.write('urllib.error.URLERROR: ' + link + '\n')
                        break
                break
                
            counter += 1

    except imgurpython.helpers.error.ImgurClientError:
        with open(os.path.join(direct, 'error.txt'), 'a+') as logFile:
            logFile.write('ImgurClientError: ' + album + '\n')

def writeDescription(description, imageId, folder, counter):
    if description != None:
        with open(os.path.join(folder, "(" + str(counter) + ") " + imageId + '.txt'), 'w+') as f:
            f.write('%s\n' % description)

def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 190: title = title[:120]
    return title

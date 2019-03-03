from imgurpython import ImgurClient
import imgurpython
from creds import *
import urllib.request
import re
import os
import time

retry_counter = 5

'''
Saves individual images into the assigned directory.
If a URLError occurs it retries five times before logging
the error.
'''
def saveImage(link, author, sub, name, ext, direct, counter = 1):
    folder = direct + '/' + sub + '/' + author + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        urllib.request.urlretrieve(link, folder + name + ext)
    except urllib.error.URLError:
        if retry_counter > counter:
            time.sleep(60)
            counter += 1
            saveImage(link, author, sub, name, ext, direct, counter)
        else:
            with open(direct + '/error.txt', 'a') as logFile:
                logFile.write('urllib.error.URLERROR: ' + link + '\n')
                logFile.close()


'''
Saves entire imgur albums into the assigned directory.
Writes the descrption to a text file if there is one. Retries
five times if a URLError occurs before logging the error.
'''
def saveAlbum(album, author, sub, sub_title, direct):
    counter = 0
    client = ImgurClient(Im_client_id, Im_client_secret) #Imgur client
    try:
        try:
            album_data = client.get_album(album) #Whole album images + data
        except imgurpython.helpers.error.ImgurClientError: #Album with only one image
            saveImage('https://imgur.com/' + album + '.jpg', author, sub, sub_title, 'jpg', direct)
            return

        folderName = album_data.title #album title

        if not folderName:
            folderName = sub_title + " - " + str(album)
            folderName = formatName(folderName)
        else:
            folderName = folderName.replace(' ', '_')
            folderName = formatName(folderName)

        images = client.get_album_images(album)


        for image in images:
            folder = os.path.join(direct, sub, author, str(folderName))

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
                        with open(direct + '/error.txt', 'a') as logFile:
                            logFile.write('urllib.error.URLERROR: ' + link + '\n')
                            logFile.close()
                        break
                break
                
            counter += 1

    except imgurpython.helpers.error.ImgurClientError:
        with open(direct + '/error.txt', 'a') as logFile:
            logFile.write('ImgurClientError: ' + album + '\n')
            logFile.close()

def writeDescription(description, imageId, folder, counter):
    if description != None:
        name = os.path.join(folder, "(" + str(counter) + ") " + imageId + '.txt')
        file = open(name, 'w+')
        file.write('%s\n' % description)

def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 190:
        title = title[:120]
    return title

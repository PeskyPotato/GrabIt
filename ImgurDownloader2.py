from imgurpython import ImgurClient
import imgurpython
from creds import *
import urllib.request
import re
import os
import time

def saveImage(link, author, sub, name, ext, direct):
    folder = direct + '\\' + sub + '\\' + author + '\\'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        urllib.request.urlretrieve(link, folder + name + ext)
    except urllib.error.URLError:
        time.sleep(20)
        try:
            urllib.request.urlretrieve(link, folder + name + ext)
        except:
            pass
def saveAlbum(album, author, sub, sub_title, direct):
    counter = 0
    client = ImgurClient(Im_client_id, Im_client_secret) #Imgur client
    try:
        album_data = client.get_album(album) #Whole album
        folderName = album_data.title #album title

        if not folderName:
            folderName = sub_title + " - " + str(album)
            folderName = formatName(folderName)
        else:
            folderName = folderName.replace(' ', '_')
            folderName = formatName(folderName)
        print(album)
        images = client.get_album_images(album)
        print(album)

        for image in images:
            #print(str(image.link))
            #print(str(image.description))
            print(image.type)
            folder = direct + '\\' + sub + '\\' + author + '\\' + str(folderName) + '\\'
            #folder  = re.sub('[?/|\:<>*"]', '', folder)

            if not os.path.exists(folder):
                os.makedirs(folder)

            writeDescription(image.description, image.id, folder, counter)

            urllib.request.urlretrieve(image.link, folder + "(" + str(counter) + ") " + str(image.id) + str(image.type).replace('image/','.'))

            counter = counter + 1
    except imgurpython.helpers.error.ImgurClientError:
        with open(direct + '\\error.txt', 'a') as logFile:
            logFile.write('ImgurClientError: ' + album + '\n')
            logFile.close()

def writeDescription(description, imageId, folder, counter):
    name = folder + "(" + str(counter) + ") " + imageId + '.txt'
    #print(name)
    file = open(name, 'w+')
    file.write('%s\n' % description)

def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 211:
        title = title[:210]
    return title

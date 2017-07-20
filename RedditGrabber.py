import praw
from ImgurDownloader2 import saveAlbum
from ImgurDownloader2 import saveImage
import re
import sys
import os
import time
import urllib.request, json

reddit = praw.Reddit(client_id = '',
                     client_secret= '',
                     user_agent='',
                     username = '',
                     password = '')

with open('downloaded.txt') as input:
          dictionary = set(input.read().split())
def grabber(subR):
    for submission in reddit.subreddit(subR).hot(limit=100):
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        title = submission.title
        #print(title)
        print(submission.is_self)
        link = submission.url
        
        if submission.is_self:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                folder = "C:/Users/User/Documents/ImgurBackup/" + str(submission.subreddit) + "/" + str(submission.author) + "/"
                if not os.path.exists(folder):
                    os.makedirs(folder)
                file = open(folder + title + '.txt', 'a')
                #file.write(str(submission.author) + '\n')
                file.write(str(submission.selftext.encode('utf-8')))
                file.close()
                with open("downloaded.txt", "a") as file0:
                    file0.write(link+'\n')
                file.close()
            
        elif '.jpg' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.jpg')
                with open("downloaded.txt", "a") as file:
                    file.write(link + '\n')
                file.close()
                print("jpg")

        elif '.png' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.png')
                with open("downloaded.txt", "a") as file:
                    file.write(link + '\n')
                file.close()
                print("png")

        elif 'http://imgur.com/a/' in link:
            albumId = link[19:]
            if len(albumId) > 5: albumId = albumId[:5]
            if albumId not in dictionary:
                print (link)
                saveAlbum(albumId, str(submission.author), str(submission.subreddit), submission.title)
                with open("downloaded.txt", "a") as file:
                    file.write(albumId + '\n')
                file.close()
                print("album")
            
        elif 'gfycat.com/' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)            
                tag = link.rsplit('/', 1)[-1]
                requestLink = "http://gfycat.com/cajax/get/" + tag
                with urllib.request.urlopen(requestLink) as url:
                    data = json.loads(url.read().decode())
                    gifUrl = data['gfyItem']['gifUrl']
                saveImage(gifUrl, str(submission.author), str(submission.subreddit), title, '.gif')
                with open("downloaded.txt", "a") as file:
                    file.write(link + '\n')
                file.close()
                print('gfycat')
        elif 'https://www.reddit.com/' in link:
            print("reddit")

def formatName(title):
    title = re.sub('[?/|\:<>*"]', '', title)
    if len(title) > 211:
        title = title[:210]
    return title

#Subreddit to backup goes here
if __name__ == "__main__":
    while True:
        grabber('DIY')

    


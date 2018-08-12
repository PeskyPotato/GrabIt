import praw
from ImgurDownloader2 import saveAlbum
from ImgurDownloader2 import saveImage
import re
import sys
import os
import time
import urllib.request, json
from creds import *
import socket

reddit = praw.Reddit(client_id = Re_client_id,
                     client_secret= Re_client_secret,
                     user_agent= Re_user_agent,
                     username = Re_username,
                     password = Re_password)
dictionary = {}

def grabber(subR, direct):
    for submission in reddit.subreddit(subR).hot(limit=	150):
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        title = submission.title
        print('Downloading post:', title.encode('utf-8'), 'From:', str(subR), 'By', str(submission.author))
        link = submission.url

        if submission.is_self:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                #folder = "C:/Users/User/Documents/ImgurBackup/" + str(submission.subreddit) + "/" + str(submission.author) + "/"
                folder = direct + '/' + str(submission.subreddit) + '/' + str(submission.author) + '/'
                #print('folder', folder)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                file = open(folder + title + '.txt', 'a')
                #file.write(str(submission.author) + '\n')
                file.write(str(submission.selftext.encode('utf-8')))
                file.close()
                with open(direct + '/downloaded.txt', 'a') as file0:
                    file0.write(link+'\n')
                file.close()

        elif '.jpg' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.jpg', direct)
                with open(direct + '/downloaded.txt', 'a') as file:
                    file.write(link + '\n')
                file.close()
                print("jpg")

        elif '.png' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.png', direct)
                with open(direct + 'downloaded.txt', 'a') as file:
                    file.write(link + '\n')
                file.close()
                print("png")

        elif 'https://imgur.com/a/' in link:
            albumId = link[19:]
            #if len(albumId) > 5: albumId = albumId[:5]
            if albumId not in dictionary:
                #print (albumId)
                saveAlbum(albumId, str(submission.author), str(submission.subreddit), submission.title, direct)
                with open(direct + '/downloaded.txt', 'a') as file:
                    file.write(albumId + '\n')
                file.close()
                #print("album")

        elif '.gifv' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                try:
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.mp4', direct)
                except urllib.error.HTTPError:
                    time.sleep(10)
                    try:
                        saveImage(link, str(submission.author), str(submission.subreddit), title, '.mp4', direct)
                    except urllib.error.HTTPError:
                        print("Time out", link)
                with open(direct + '/downloaded.txt', 'a') as file:
                    file.write(link + '\n')
                file.close()
                print("gifv")

        elif '.gif' in link:
            if link not in dictionary:
                print(link)
                title = submission.title
                title = formatName(title)
                try:
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)
                except urllib.error.URLError:
                    time.sleep(20)
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)

                with open(direct + '/downloaded.txt', 'a') as file:
                    file.write(link + '\n')
                file.close()
                print("gif")

        elif 'gfycat.com/' in link:
            if link not in dictionary:
                title = submission.title
                title = formatName(title)
                tag = link.rsplit('/', 1)[-1]
                requestLink = "http://gfycat.com/cajax/get/" + tag
                with urllib.request.urlopen(requestLink) as url:
                    data = json.loads(url.read().decode())
                    try:
                        gifUrl = data['gfyItem']['gifUrl']
                    except KeyError:
                        with open(direct + '/error.txt', 'a') as logFile:
                            logFile.write('KeyError: '+ link + '\n')
                            logFile.close()
                try:
                    saveImage(gifUrl, str(submission.author), str(submission.subreddit), title, '.gif', direct)
                except TypeError:
                    with open(direct + '/error.txt', 'a') as logFile:
                        logFile.write('TypeError: ' + link + '\n')
                        logFile.close()
                except UnboundLocalError:
                    print("oops"    )
                with open(direct + '/downloaded.txt', 'a') as file:
                    file.write(link + '\n')
                file.close()
                print('gfycat')
        elif 'https://www.reddit.com/' in link:
            with open(direct + '/error.txt', 'a') as logFile:
                logFile.write('Link to reddit' + link + '\n')
                logFile.close()
        else:
            with open(direct + '/error.txt', 'a') as logFile:
                logFile.write('No matches' + link + '\n')
                logFile.close()

def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 211:
        title = title[:210]
    return title

if __name__ == '__main__':
    direct = os.getcwd()
    while True:
        with open(direct + '/downloaded.txt') as input:
            dictionary = set(input.read().split())
        with open("subs.txt") as f:
            for sub in f:
                print("********** ",str(sub.split())," **********")
                grabber(str(sub.strip()), direct)
                time.sleep(10)

import praw
from ImgurDownloader2 import saveAlbum
from ImgurDownloader2 import saveImage
from dbHandler import createTable
from dbHandler import dbWrite
#from urllib.request import urlopen
import requests
import re
import sys
import os
import time
import urllib.request,json
from creds import *
import argparse
import signal

'''
Initialise Reddit
'''
reddit = praw.Reddit(client_id = Re_client_id,
                     client_secret= Re_client_secret,
                     user_agent= Re_user_agent)

def grabber(subR, direct, posts):
    for submission in reddit.subreddit(subR).hot(limit = int(posts)):
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        title = submission.title
        link = submission.url

        if(dbWrite(submission.permalink, title, submission.created, submission.author, link)):
        #if(1):
            print('Downloading post:', title.encode('utf-8'), 'From:', str(subR), 'By', str(submission.author))

            if submission.is_self:
                title = submission.title
                title = formatName(title)
                folder = direct + '/' + str(submission.subreddit) + '/' + str(submission.author) + '/'
                if not os.path.exists(folder):
                    os.makedirs(folder)
                file = open(folder + title + '.txt', 'a')
                file.write(str(submission.selftext.encode('utf-8')))
                file.close()

            elif '.jpg' in link:
                title = submission.title
                title = formatName(title)
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.jpg', direct)

            elif '.png' in link:
                title = submission.title
                title = formatName(title)
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.png', direct)

            elif 'imgur.com/' in link:
                albumId = link.rsplit('/', 1)[-1]
                if '#' in albumId:
                    albumId = albumId.rsplit('#', 1)[-2]
                saveAlbum(albumId, str(submission.author), str(submission.subreddit), submission.title, direct)

            elif '.gifv' in link:
                title = submission.title
                title = formatName(title)
                link = link.replace('gifv', 'gif')
                try:
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)
                except urllib.error.HTTPError:
                    time.sleep(10)
                    try:
                        saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)
                    except urllib.error.HTTPError:
                        with open(direct + '/error.txt', 'a') as logFile:
                            logFile.write('HTTPError (timeout): '+ link + '\n')
                            logFile.close()

            elif 'giphy.com/gifs' in link:
                title = submission.title
                title = formatName(title)
                link = 'https://media.giphy.com/media/' + link.split('-', 2)[-1] + '/giphy.gif'
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)

            elif '.gif' in link:
                title = submission.title
                title = formatName(title)
                try:
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)
                except urllib.error.URLError:
                    time.sleep(20)
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)

            elif 'gfycat.com/' in link:
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
                    gifurl = data['gfyItem']['mobileUrl']
                    saveImage(str(data['gfyItem']['mobileUrl']), str(submission.author), str(submission.subreddit), title, '.mp4', direct)
                except UnboundLocalError:
                    with open(direct + '/error.txt', 'a') as logFile:
                        logFile.write('UnboundLocalError: '+ link + '\n')
                        logFile.close()

            elif 'https://www.reddit.com/' in link:
                with open(direct + '/error.txt', 'a') as logFile:
                    logFile.write('Link to reddit' + link + '\n')
                    logFile.close()
            else:
                with open(direct + '/error.txt', 'a') as logFile:
                    logFile.write('No matches: ' + link + '\n')
                    logFile.close()

'''
Removes special characters and shortens long
filenames
'''
def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 211:
        title = title[:210]
    return title

def handler(signum, frame):
    print("Exiting...")
    sys.exit()

def main(subR, posts):
    direct = os.getcwd()
    sys.stdout.write("\033[0;32m")
    print("****", subR, "****")
    grabber(subR, direct, posts)

if __name__ == '__main__':
    '''
    Parser input
    '''
    parser = argparse.ArgumentParser(description = "Downloads images, GIFS and text from YouTube")
    parser.add_argument("Subreddit", help = "Enter a subreddit to backup or text file")
    parser.add_argument("-w", "--wait", help = "Change wait time between subreddits in seconds")
    parser.add_argument("-p", "--posts", help = "Number of posts to grab on each cycle")

    args = parser.parse_args()

    subR = None
    filepath = None
    verb = False

    if '.txt' in args.Subreddit:
        filepath = args.Subreddit
    else:
        subR = args.Subreddit

    if args.wait and isinstance(args.wait, int):
        wait = args.wait
    else:
        wait = 600

    if args.posts:
        posts = args.posts
    else:
        posts = 50
    createTable()

    '''
    Feed subreddits to main
    '''
    while(True):
        if filepath is not None:
            with open(filepath) as f:
                line = f.readline()
                while line:
                    subR = "{}".format(line.strip())
                    main(subR, posts)
                    signal.signal(signal.SIGINT, handler)
                    line = f.readline()
        else:
            main(subR, posts)
        print("waiting")
        time.sleep(wait)

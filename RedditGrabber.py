import praw
from handlers.ImgurDownloader2 import saveAlbum
from handlers.ImgurDownloader2 import saveImage
from handlers.dbHandler import createTable
from handlers.dbHandler import dbWrite
import requests
import re
import sys
import os
import time
import urllib.request,json
from creds import *
import argparse
import signal
import youtube_dl

'''
Initialise Reddit
'''
reddit = praw.Reddit(client_id = Re_client_id,
                     client_secret= Re_client_secret,
                     user_agent= Re_user_agent)

def grabber(subR, direct, posts):
    for submission in reddit.subreddit(subR).hot(limit = int(posts)):
        title = submission.title
        link = submission.url
        if(dbWrite(submission.permalink, title, submission.created, submission.author, link)):
        #if(1):
            print('Downloading post:', title.encode('utf-8'), 'From:', str(subR), 'By', str(submission.author))
            title = formatName(submission.title)
            
            # Is a selftext post
            if submission.is_self:
                folder = direct + '/' + str(submission.subreddit) + '/' + str(submission.author) + '/'
                if not os.path.exists(folder):
                    os.makedirs(folder)
                file = open(folder + title + '.txt', 'a')
                file.write(str(submission.selftext.encode('utf-8')))
                file.close()
            
            # Link to a jpg, png, giv
            elif '.jpg' in link:
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.jpg', direct)
            elif '.png' in link:
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.png', direct)
            elif '.gifv' in link:
                link = link.replace('gifv', 'mp4')
                try:
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.mp4', direct)
                except urllib.error.HTTPError:
                    time.sleep(10)
                    try:
                        saveImage(link, str(submission.author), str(submission.subreddit), title, '.mp4', direct)
                    except urllib.error.HTTPError:
                        with open(direct + '/error.txt', 'a') as logFile:
                            logFile.write('HTTPError (timeout): '+ link + '\n')
                            logFile.close()
            
            # Imgur album
            elif 'imgur.com/' in link:
                albumId = link.rsplit('/', 1)[-1]
                if '#' in albumId:
                    albumId = albumId.rsplit('#', 1)[-2]

                saveAlbum(albumId, str(submission.author), str(submission.subreddit), title, direct)

            # Giphy
            elif 'giphy.com/gifs' in link:
                link = 'https://media.giphy.com/media/' + link.split('-', 2)[-1] + '/giphy.gif'

                saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)

            # Gif post
            elif '.gif' in link:
                try:
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)
                except urllib.error.URLError:
                    time.sleep(20)
                    saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', direct)

            # Link to another reddit submission
            elif 'https://www.reddit.com/' in link:
                with open(direct + '/error.txt', 'a') as logFile:
                    logFile.write('Link to reddit' + link + ' by ' + str(submission.author) + ' \n')
                    logFile.close()
            
            # All others are caught by youtube-dl, if still no match it's written to the log file
            else:
                folder = direct + '/' + str(submission.subreddit) + '/' + str(submission.author) + '/'
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': folder + '%(title)s-%(id)s.%(ext)s',
                    'quiet': 'quiet'
                }
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([link])
                except youtube_dl.utils.DownloadError:
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
    sys.stdout.write("\033[1;32m")
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

    if args.wait:
        try:
            wait = int(args.wait)
        except ValueError:
            print("Please enter an integer in seconds to wait")
            sys.exit()
    else:
        wait = 600

    if args.posts:
        try:
            posts = int(args.posts)
        except ValueError:
            print("Please enter an integer for the number of posts")
            sys.exit()
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
        print("Waiting", wait, "seconds.")
        time.sleep(wait)

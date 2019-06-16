import praw
from handlers.ImgurDownloader import saveAlbum, saveImage
from handlers.dbHandler import createTable, dbWrite
import requests
import re
import sys
import os
import time
import urllib.request,json
from creds import *
import argparse
import youtube_dl

class color:
   RED = '\033[91m'
   BOLD = '\033[1m'
   END = '\033[0m'

'''
Initialise Reddit
'''
reddit = praw.Reddit(client_id = Re_client_id,
                     client_secret= Re_client_secret,
                     user_agent= Re_user_agent)

def grabber(subR, base_dir, posts):
    for submission in reddit.subreddit(subR).hot(limit = int(posts)):
        title = submission.title
        link = submission.url
        if(dbWrite(submission.permalink, title, submission.created, submission.author, link)):
        #if(1):
            print_title = title.encode('utf-8')[:25] if len(title) > 25 else title.encode('utf-8')
            print('{}Post:{} {}... {}From:{} {} {}By:{} {}'.format(color.BOLD, color.END, print_title, color.BOLD, color.END, str(subR), color.BOLD, color.END, str(submission.author)))
            title = formatName(title)
            
            # Selftext post
            if submission.is_self:
                folder = os.path.join(base_dir, str(submission.subreddit), str(submission.author))
                if not os.path.exists(folder):
                    os.makedirs(folder)
                with open(os.path.join(folder, title + '.txt'), 'a+') as f:
                    f.write(str(submission.selftext.encode('utf-8')))

            # Link to a jpg, png, giv, gif
            elif any(ext in link for ext in ['.jpg', '.png', '.gif', 'gifv']):
                saveImage(link, str(submission.author), str(submission.subreddit), title, base_dir)

            # Imgur album
            elif 'imgur.com/' in link:
                albumId = link.rsplit('/', 1)[-1]
                if '#' in albumId:
                    albumId = albumId.rsplit('#', 1)[-2]
                saveAlbum(albumId, str(submission.author), str(submission.subreddit), title, base_dir)

            # Giphy
            elif 'giphy.com/gifs' in link:
                link = 'https://media.giphy.com/media/' + link.split('-', 2)[-1] + '/giphy.gif'
                saveImage(link, str(submission.author), str(submission.subreddit), title, '.gif', base_dir)

            # Link to another reddit submission
            elif 'reddit.com/r/' in link:
                with open(os.path.join(base_dir, 'error.txt'), 'a+') as logFile:
                    logFile.write('Link to reddit' + link + ' by ' + str(submission.author) + ' \n')
                    logFile.close()
            
            # All others are caught by youtube-dl, if still no match it's written to the log file
            else:
                folder = os.path.join(base_dir, str(submission.subreddit), str(submission.author))
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(folder, '%(title)s-%(id)s.%(ext)s'),
                    'quiet': 'quiet'
                }
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([link])
                except youtube_dl.utils.DownloadError:
                    with open(os.path.join(base_dir, 'error.txt'), 'a+') as logFile:
                        logFile.write('No matches: ' + link + '\n')

'''
Removes special characters and shortens long
filenames
'''
def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 211: title = title[:210]
    return title

def main(subR, posts, base_dir):
    print(color.BOLD, "****", subR, "****", color.END)
    grabber(subR, base_dir, posts)

if __name__ == '__main__':
    '''
    Parser input
    '''
    parser = argparse.ArgumentParser(description = "Downloads images, GIFS and text from YouTube")
    parser.add_argument("Subreddit", help = "Enter a subreddit to backup or text file")
    parser.add_argument("-w", "--wait", help = "Change wait time between subreddits in seconds")
    parser.add_argument("-p", "--posts", help = "Number of posts to grab on each cycle")
    parser.add_argument("-o", "--output", help = "Set base directory to start download")

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
    
    if args.output:
        base_dir = os.path.abspath(args.output)
        if not os.path.exists(base_dir): os.makedirs(base_dir)
    else:
        base_dir = os.getcwd()

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
                    main(subR, posts, base_dir)
                    line = f.readline()
        else:
            main(subR, posts, base_dir)
        print(color.BOLD, "Waiting", wait, "seconds.", color.END)
        time.sleep(wait)

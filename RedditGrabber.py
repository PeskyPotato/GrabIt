import praw
from prawcore import exceptions
import re
import sys
import os
import time
import argparse
import youtube_dl
import json
import traceback
import logging
from datetime import datetime
from resources.log_color import ColoredFormatter

from resources.handlers.tenor import Tenor
from resources.handlers.giphy import Giphy
from resources.handlers.imgur import Imgur
from resources.handlers.common import Common

from resources.save import Save
from resources.db_interface import DBInterface

with open('./resources/config.json') as f:
        config = json.load(f)
save = Save(os.getcwd(), False)
logger = logging.getLogger(__name__)
db = None

def grabber(subR, base_dir, posts, sort, search):
    # Initialise Reddit
    reddit = praw.Reddit(client_id = config["reddit"]["creds"]["client_id"],
                        client_secret= config["reddit"]["creds"]["client_secret"],
                        user_agent= config["reddit"]["creds"]["user_agent"])
    submissions = []
    if search:
        logger.debug('Search term: {}'.format(search) )
        if 'u/' in subR or '/u/' in subR:
            logger.warning('Cannot search redditors: {}'.format(subR))
        else:
            submissions = reddit.subreddit(subR).search(search, sort=sort.lower(), limit = int(posts))

    else:
        if 'u/' in subR or '/u/' in subR:
            if '/u/' in subR: subR = subR[3:]
            elif 'u/'in subR: subR = subR[2:]
            if sort == 'hot': submissions = reddit.redditor(subR).submissions.hot(limit = int(posts))
            elif sort == 'new': submissions = reddit.redditor(subR).submissions.new(limit = int(posts))
            elif sort =='top': submissions = reddit.redditor(subR).submissions.top(limit = int(posts))
        else:
            if sort == 'hot': submissions = reddit.subreddit(subR).hot(limit = int(posts))
            elif sort == 'new': submissions = reddit.subreddit(subR).new(limit = int(posts))
            elif sort == 'top': submissions = reddit.subreddit(subR).top(limit = int(posts))
        
    for submission in submissions:
        title = submission.title
        logger.debug("Submission url {}".format(submission.url))
        link = submission.url
        ''' django URL validation regex '''
        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not (db.checkPost(submission.permalink.split("/")[4])) and checkBlacklist(submission) and re.match(regex, link):
            downloaded = True
            print_title = title.encode('utf-8')[:25] if len(title) > 25 else title.encode('utf-8')
            logger.info("Post: {}...({}) From: {} By: {}".format(print_title, submission.id, submission.subreddit, str(submission.author)))
            title = formatName(title)

            path = {'author': str(submission.author), 'subreddit': str(submission.subreddit)}

            # Selftext post
            if submission.is_self:
                with open(os.path.join(save.get_dir(path),'{}-{}.txt'.format(str(submission.id), formatName(title))), 'a+') as f:
                    f.write(str(submission.selftext.encode('utf-8')))

            # Link to a jpg, png, gifv, gif, jpeg
            elif re.match(Common.valid_url, link):
                Common(link, '{}-{}'.format(str(submission.id),title), save.get_dir(path))

            # Imgur
            elif re.match(Imgur.valid_url, link):
                Imgur(link, title, save.get_dir(path))

            # Giphy
            elif re.match(Giphy.valid_url, link):
                Giphy(link, title, save.get_dir(path))

            # Tenor
            elif re.match(Tenor.valid_url, link):
                Tenor(link, title, save.get_dir(path))

            # Flickr
            elif 'flickr.com/' in link:
                logger.debug("No Flickr support")
                with open(os.path.join(base_dir, 'error.txt'), 'a+') as logFile:
                        logFile.write('Needs support: ' + link + '\n')

            # Reddit submission
            elif 'reddit.com/r/' in link:
                downloaded = False
                with open(os.path.join(base_dir, 'error.txt'), 'a+') as logFile:
                    logFile.write('Link to reddit ' + link + ' by ' + str(submission.author) + ' \n')
                    logFile.close()
            
            # All others are caught by youtube-dl, if still no match it's written to the log file
            else:
                folder = save.get_dir(path)
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(folder, '%(id)s-%(title)s.%(ext)s'),
                    'quiet': 'quiet'
                }
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([link])
                except youtube_dl.utils.DownloadError:
                    logger.info("No matches: {}".format(link))
                    downloaded = False
                except Exception as e:
                    logger.error('Exception {} on {}'.format(e, link))
                    downloaded = False

            if downloaded:
                db.insertPost(submission.permalink, submission.title, submission.created, str(submission.author), submission.url)

def checkBlacklist(submission):
    for item in config['reddit']['blacklist']:
        if ('u/' in item or '/u/' in item):
            if item.split('/')[-1] == submission.author:
                logger.debug('Blocked user ' + item.split('/')[-1])
                return False
        elif item == submission.subreddit:
            logger.debug('Blocked subreddit ' + item)
            return False
    return True

'''
Removes special characters and shortens long
filenames
'''
def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 211: title = title[:210]
    return title

def feeder(subR, posts, base_dir, sort, search):
    # reloads config file
    with open('./resources/config.json') as f:
        config = json.load(f)
    
    logger.info("*****  {}  *****".format(subR))
    try:
        grabber(subR, base_dir, posts, sort, search)
    except exceptions.ResponseException as err:
        if "received 401 HTTP response" in str(err):
            logger.error("{} Check Reddit API credentials".format(err))
        elif "Redirect to /subreddits/search" in str(err):
            logger.error("{} Subreddit does not exist".format(err))
        else:
            logger.error(str(traceback.TracebackException.from_exception(err)) + " Check username or subreddit: " + subR)

def main(args):

    subR = None
    filepath = None

    if args.subreddit:
        if '.txt' in args.subreddit: 
            filepath = args.subreddit
        else: 
            subR = args.subreddit

    # wait
    if args.wait and args.subreddit:
        try:
            wait = int(args.wait)
        except ValueError:
            logger.error("Please enter an integer in seconds to wait")
            sys.exit()
    else:
        wait = 600

    # posts
    if args.posts and args.subreddit:
        try:
            posts = int(args.posts)
        except ValueError:
            logger.error("Please enter an inter for the number of posts")
            sys.exit()
    else:
        posts = 50

    # output
    if args.output and args.subreddit:
        base_dir = os.path.abspath(args.output)
        if not os.path.exists(base_dir): os.makedirs(base_dir)
    else:
        base_dir = os.getcwd()

    # sort
    sort = 'hot'
    if args.sort and (args.sort.lower() == 'hot' or args.sort.lower() == 'new' or args.sort.lower() == 'top') and args.subreddit:
        sort = args.sort
    elif args.sort:
        logger.error("Please enter hot, new or top for sort")
        sys.exit()
    
    search = None
    if args.search:
        search = args.search

    # blacklist
    if args.blacklist:
        config["reddit"]["blacklist"].append(args.blacklist)

    # reddit api credentials
    if args.reddit_id:
        config["reddit"]["creds"]["client_id"] = args.reddit_id
    if args.reddit_secret:
        config["reddit"]["creds"]["client_secret"] = args.reddit_secret
    
    with open('./resources/config.json', 'w') as f:
        json.dump(config, f)

    # output template
    global save
    if args.output_template:
        template = args.output_template
    else:
        template = os.path.join('%(subreddit)s','%(author)s')
    save = Save(base_dir, template)

    # initialise database
    global db
    db_path = config['general']['database_location']
    db_path = db_path[:db_path.rfind('/')]
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    db = DBInterface(config["general"]["database_location"])

    if args.subreddit:
        # Passes subreddits to feeder
        while(True):
            if filepath is not None:
                with open(filepath) as f:
                    line = f.readline()
                    while line:
                        subR = "{}".format(line.strip())
                        feeder(subR, posts, base_dir, sort, search)
                        line = f.readline()
            else:
                feeder(subR, posts, base_dir, sort, search)
            logger.info("Waiting {} seconds".format(wait))
            time.sleep(wait)


if __name__ == '__main__':
    # Parses input
    parser = argparse.ArgumentParser(description = "Archives submissions from Reddit")
    parser.add_argument("subreddit", nargs = '?', help = "Enter a subreddit to backup or text file")
    parser.add_argument("-w", "--wait", help = "Change wait time between subreddits in seconds")
    parser.add_argument("-p", "--posts", help = "Number of posts to grab on each cycle")
    parser.add_argument("-o", "--output", help = "Set base directory to start download")
    parser.add_argument('-t', '--output_template', help = 'Specify output template for download')
    parser.add_argument("--sort", help = "Sort submissions by 'hot', 'new' or 'top'")
    parser.add_argument("-v", "--verbose", help = "Set verbose", action = "store_true")
    parser.add_argument("--blacklist", help = "Avoid downloading a user or subreddit")
    parser.add_argument('--search', help='Search for submissions in a subreddit')
    parser.add_argument('--reddit_id', help = 'Reddit client ID')
    parser.add_argument('--reddit_secret', help = 'Reddit client secret')

    args = parser.parse_args()

    # verbose / logger
    log_path = config['general']['log_file']
    log_path = log_path[:log_path.rfind('/')]
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if config["general"]["logger_append"]:
        filemode = 'a'
    else:
        filemode = 'w'
    if config['general']['log_timestamp']:
        now = datetime.now()
        log_path = config['general']['log_file']
        log_file = log_path[log_path.rfind('/')+1:]
        log_file = '%d-%d-%d_%d-%d-%d_%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, log_file)
    else:
        log_file = config['general']['log_file']
    try:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=log_file,
                            filemode=filemode)
    except IsADirectoryError as e:
        print('Log file not set correctly, check log_file in config')
        sys.exit()

    console = logging.StreamHandler()
    if args.verbose and args.subreddit:  
        console.setLevel(logging.DEBUG)
        formatter = ColoredFormatter("[%(name)s][%(levelname)s] %(message)s (%(filename)s:%(lineno)d)")
    else:
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')

    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # start program
    try:
        main(args)
    except KeyboardInterrupt:
        logger.info("\nQuitting")
        sys.exit()
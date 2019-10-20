import praw
from prawcore import exceptions
import re
import sys
import os
import time
from resources.parser import Parser
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

save = Save(os.getcwd(), False)
logger = logging.getLogger(__name__)
db = None


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


def formatName(title):
    '''Removes special characters and shortens long filenames'''
    title = re.sub('[?/|\\:<>*"]', '', title)
    if len(title) > 211:
        title = title[:210]
    return title


def bar_percent(progress_raw, total_count, toolbar_width):
    if total_count > 0:
        progress = int((progress_raw/total_count) * toolbar_width)
        if progress <= toolbar_width:
            marks = '-' * (progress) + ' ' * (toolbar_width-progress)
            print('[{}] {}%'.format(marks, int((progress/toolbar_width)*100)), '[{}/{}]'.format(progress_raw, total_count), end='\r')

def getSubmission(submission, parser):
    title = submission.title
    logger.debug("Submission url {}".format(submission.url))
    link = submission.url
    ''' django URL validation regex '''
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not (db.checkPost(submission.permalink.split("/")[4])) and checkBlacklist(submission) and re.match(regex, link) and (not(submission.over_18) or parser.allow_nsfw):
        downloaded = True
        print_title = title.encode('utf-8')[:25] if len(title) > 25 else title.encode('utf-8')
        logger.info("Post: {}...({}) From: {} By: {}".format(print_title, submission.id, submission.subreddit, str(submission.author)))
        title = formatName(title)
        path = {'author': str(submission.author), 'subreddit': str(submission.subreddit)}

        # Selftext post
        if submission.is_self:
            with open(os.path.join(save.get_dir(path), '{}-{}.txt'.format(str(submission.id), formatName(title))), 'a+') as f:
                f.write(str(submission.selftext.encode('utf-8')))

        # Link to a jpg, png, gifv, gif, jpeg
        elif re.match(Common.valid_url, link):
            if not Common(link, '{}-{}'.format(str(submission.id), title), save.get_dir(path)).save():
                downloaded = False

        # Imgur
        elif re.match(Imgur.valid_url, link):
            if not Imgur(link, title, save.get_dir(path)).save():
                downloaded = False

        # Giphy
        elif re.match(Giphy.valid_url, link):
            if not Giphy(link, title, save.get_dir(path)).save():
                downloaded = False

        # Tenor
        elif re.match(Tenor.valid_url, link):
            if not Tenor(link, title, save.get_dir(path)).save():
                downloaded = False

        # Flickr
        elif 'flickr.com/' in link:
            downloaded = False
            logger.info("No mathces: No Flickr support".format(link))

        # Reddit submission
        elif 'reddit.com/r/' in link:
            downloaded = False
            logger.info("No mathces: Reddit submission {}".format(link))

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
    else:
        logger.debug("Skipped submission url {}".format(submission.url))

def feeder(subR, parser):
    posts = parser.posts
    sort = parser.sort
    search = parser.search

    # reloads config file
    with open('./resources/config.json') as f:
        config = json.load(f)

    logger.info("*****  {}  *****".format(subR))
    try:
        reddit = praw.Reddit(
            client_id=config["reddit"]["creds"]["client_id"],
            client_secret=config["reddit"]["creds"]["client_secret"],
            user_agent=config["reddit"]["creds"]["user_agent"]
        )
        
        # gather submissions
        submissions = []
        if search:
            logger.debug('Search term: {}'.format(search))
            if 'u/' in subR or '/u/' in subR:
                logger.warning('Cannot search redditors: {}'.format(subR))
            else:
                include_over_18 = 'off'
                if parser.allow_nsfw:
                    include_over_18 = 'on'
                submissions = reddit.subreddit(subR).search(search, sort=sort.lower(), 
                    limit=int(posts), time_filter=parser.time_filter, params={'include_over_18': include_over_18})
        elif 'reddit.com' not in subR:
            if 'u/' in subR or '/u/' in subR:
                if '/u/' in subR: subR = subR[3:]
                elif 'u/'in subR: subR = subR[2:]
                if sort == 'hot':
                    submissions = reddit.redditor(subR).submissions.hot(limit=int(posts))
                elif sort == 'new':
                    submissions = reddit.redditor(subR).submissions.new(limit=int(posts))
                elif sort == 'top':
                    submissions = reddit.redditor(subR).submissions.top(limit=int(posts), time_filter=parser.time_filter)
                elif sort == 'controversial':
                    submissions = reddit.redditor(subR).submissions.controversial(limit=int(posts), time_filter=parser.time_filter)

            else:
                if sort == 'hot':
                    submissions = reddit.subreddit(subR).hot(limit=int(posts))
                elif sort == 'new':
                    submissions = reddit.subreddit(subR).new(limit=int(posts))
                elif sort == 'top':
                    submissions = reddit.subreddit(subR).top(limit=int(posts), time_filter=parser.time_filter)
                elif sort == 'controversial':
                    submissions = reddit.subreddit(subR).controversial(limit=int(posts), time_filter=parser.time_filter)
        else:
            submissions = [reddit.submission(url=subR)]

        submission_queue = []
        for submission in submissions:
            submission_queue.append(submission)
            print('Loading', len(submission_queue), 'posts', end='\r')

        counter = 0
        for submission in submission_queue:
            counter += 1
            getSubmission(submission, parser)
        bar_percent(counter, len(submission_queue), 50)
        print()

    except exceptions.ResponseException as err:
        if "received 401 HTTP response" in str(err):
            logger.error("{} Check Reddit API credentials".format(err))
        elif "Redirect to /subreddits/search" in str(err):
            logger.error("{} Subreddit does not exist".format(err))
        else:
            logger.error(str(traceback.TracebackException.from_exception(err)) + " Check username, subreddit or url: " + subR)
    except praw.exceptions.ClientException as err:
        logger.error(err)
        sys.exit()


def main(parser):
    # subreddit/user/text file
    subR = None
    filepath = None

    if parser.subreddit:
        if '.txt' in parser.subreddit:
            filepath = parser.subreddit
        else:
            subR = parser.subreddit

    # output template
    global save
    save = Save(parser.base_dir, parser.template)
    logger.debug('Output template set to {}'.format(save))

    # initialise database
    global db
    db_path = config['general']['database_location']
    db_path = db_path[:db_path.rfind('/')]
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    db = DBInterface(config["general"]["database_location"])

    if parser.subreddit:
        # Passes subreddits to feeder
        current_cycle = 0
        while(current_cycle < parser.cycles):
            if filepath is not None:
                with open(filepath) as f:
                    line = f.readline()
                    while line:
                        subR = "{}".format(line.strip())
                        feeder(subR, parser)
                        line = f.readline()
            else:
                feeder(subR, parser)
            if parser.cycles > 1:
                logger.info("Waiting {} seconds".format(parser.wait))
                time.sleep(parser.wait)
            current_cycle += 1


if __name__ == '__main__':
    parser = Parser()

    with open('./resources/config.json') as f:
        config = json.load(f)

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
    except IsADirectoryError:
        print('Log file not set correctly, check log_file in config')
        sys.exit()

    console = logging.StreamHandler()

    if parser.verbose:
        console.setLevel(logging.DEBUG)
        formatter = ColoredFormatter("[%(name)s][%(levelname)s] %(message)s (%(filename)s:%(lineno)d)")
    else:
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')

    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    parser.setupLogger()
    parser.checkArgs()

    # start program
    try:
        main(parser)
    except KeyboardInterrupt:
        logger.info("\nQuitting")
        sys.exit()

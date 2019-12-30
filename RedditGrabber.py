import re
import sys
import os
import time
import youtube_dl
import logging
from datetime import datetime
from resources.log_color import ColoredFormatter
from resources.parser import Parser

from resources.handlers.tenor import Tenor
from resources.handlers.giphy import Giphy
from resources.handlers.imgur import Imgur
from resources.handlers.common import Common

from resources.save import Save
from resources.db_interface import DBInterface
from resources.interfaces.reddit_instance import RedditInstance
from resources.interfaces.reddit import Reddit
from resources.interfaces.pushshift import Pushshift

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


def yt_supported(url):
    extractors = youtube_dl.extractor.gen_extractors()
    for extractor in extractors:
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False

def checkSubmission(submission):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    if (not (db.checkPost(submission.permalink.split("/")[4])) and 
        checkBlacklist(submission) and
        re.match(regex, submission.url) and
        (not (submission.over_18) or parser.allow_nsfw) and
        not ((db.checkDuplicate(submission.url)) and parser.ignore_duplicate)):
        return True
    return False


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

    if checkSubmission(submission):
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

        # youtube_dl supported site
        elif yt_supported(link):
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
        else:
            logger.info("No matches: {}".format(link))
            downloaded = False
        if downloaded:
            db.insertPost(submission.permalink, submission.title, submission.created_utc, str(submission.author), submission.url)
    else:
        logger.debug("Skipped submission url {}".format(submission.url))


def feeder(subR, parser):
    parser.reload_parser()
    RedditInstance()
    submission_queue = []
    pushshift = Pushshift(subR, parser)

    logger.info("*****  {}  *****".format(subR))

    if parser.pushshift:
        submission_queue = pushshift.queue()
    else:
        submission_queue = Reddit(subR, parser).queue()

        if parser.sort == 'new' and parser.posts > 1000 and not(parser.search):
            size = min(parser.posts - len(submission_queue), 4000)
            push_subs = pushshift.queue_append(submission_queue[-1].created_utc, size)
            submission_queue.extend(push_subs)

    for submission in submission_queue:
        getSubmission(submission, parser)


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
    db = DBInterface(parser.db_location)

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

    config = parser.config

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
        log_file = log_path[log_path.rfind('/') + 1:]
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

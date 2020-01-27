import youtube_dl
import logging
import os
import re

from resources.save import Save

from resources.handlers.tenor import Tenor
from resources.handlers.giphy import Giphy
from resources.handlers.imgur import Imgur
from resources.handlers.common import Common

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

def routeSubmission(submission):
    logger = logging.getLogger(__name__)
    save = Save()

    path = {'author': str(submission.author), 'subreddit': str(submission.subreddit)}
    title = formatName(submission.title)
    link = submission.url
    downloaded = True

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

    return downloaded
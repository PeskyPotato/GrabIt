import urllib.request
import re
import os
import time

retry_counter = 5

'''
Saves individual images into the assigned directory.
If a URLError or HTTPError occurs it retries before logging
the error.
'''
def saveImage(link, name, direct, counter = 1):
    if 'gifv' in link:
        ext = '.mp4'
        link = link.replace('gifv', 'mp4')
    else:
        ext = re.search('jpg|png|gif', link).group()
    try:
        urllib.request.urlretrieve(link, os.path.join(direct,  name + "." + ext))
    except (urllib.error.URLError, urllib.error.HTTPError) as err:
        if retry_counter > counter:
            print(err, "retrying", counter, link)
            time.sleep(60)
            counter += 1
            saveImage(link, name, direct, counter)
        else:
            with open(os.path.join(direct, 'error.txt'), 'a+') as logFile:
                logFile.write('{}: {}\n'.format(err, link))
    except FileNotFoundError as err:
        # this means album was not found, fix pending
        with open(os.path.join(direct, 'error.txt'), 'a+') as logFile:
            logFile.write('{}: {}\n'.format(err, link))

def formatName(title):
    title = re.sub('[?/|\\\:<>*"]', '', title)
    if len(title) > 190: title = title[:120]
    return title

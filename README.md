# RedditImageBackup

This project will help you backup subreddits. This downloads and organises images, self posts and gifs.

## Getting Started

Add your [imgur](https://imgur.com/account/settings/apps) and [reddit](https://www.reddit.com/prefs/apps/) credentials in the `creds.py` file.

Install [praw](https://praw.readthedocs.io/en/latest/), a Reddit API wrapper, and [imgurpython](https://github.com/Imgur/imgurpython), a Python client for the Imgur API.

    pip3 install praw
    pip3 install imgurpython

## Usage and Arguments
To download from a single subreddit, in this case /r/diy

    python3 RedditGrabber.py diy
You can also pass in a list of subreddits in the form of a txt file, with each subreddit on a newline.

    python3 RedditGrabber.py subs.txt

Below are some option arguments that you can use:

    -h, --help            show this help message and exit

    -w WAIT, --wait WAIT  Change wait time between subreddits in seconds
    -p POSTS, --posts POSTS
                        Number of posts to grab on each cycle

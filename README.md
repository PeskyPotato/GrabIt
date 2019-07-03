# RedditImageBackup

RedditImageBackup is a tool built to archive self-posts, images, gifs and videos from subreddit and users. This program works through the command line and uses Python 3.

## Installation

Get your [Reddit API credentials](https://www.reddit.com/prefs/apps/).

Install all the dependencies.

    pip install -r requirements.txt

Add the API client ID and secret through the terminal as so, replace the string in quotes with your credentials:

    python3 RedditGrabber.py --reddit_id "client_id_here" --reddit_secret "client_secret_here"

Or you can also enter the client id and and client secret int he config.json file in the resources folder.

## Usage and Arguments
To download from a single subreddit, in this case /r/diy

    python3 RedditGrabber.py diy

You can also pass in a list of subreddits and users in the form of a txt file, with contains each subreddit on a newline.

    python3 RedditGrabber.py subs.txt

This downloads the first 50 new submission from the user /u/spez and stores they by user then subreddit(i.e. spez/\<subreddit>/\<media>).

    python3 RedditGrabber.py /u/spez --by_author --posts 50 --sort new

Below are all the optional arguments that you can use:

    -h, --help                     show this help message and exit

    -w WAIT, --wait WAIT            Change wait time between subreddits in seconds
    -p POSTS, --posts POSTS         Number of posts to grab on each cycle
    -o OUTPUT, --output OUTPUT      Set base directory to start download
    --by_author                     Sort downloads by author, default by subreddit
    --sort SORT                     Sort submissions by 'hot', 'new' or 'top'
    -v, --verbose                   Sets verbose
    --blacklist BLACKLIST           Avoid downloading a user, without /u/
    --reddit_id REDDIT_ID           Reddit client ID
    --reddit_secret REDDIT_SECRET   Reddit client secret

# RedditImageBackup

RedditImageBackup is a tool built to archive self-posts, images, gifs and videos from subreddit and users. This program works through the command line and uses Python 3.

## Installation

Get your [Reddit API credentials](https://www.reddit.com/prefs/apps/).

Install all the dependencies.

    pip3 install -r requirements.txt

Add the Reddit API client ID and secret through the terminal as shown below, replace the string in quotes with your credentials:

    python3 RedditGrabber.py --reddit_id "client_id_here" --reddit_secret "client_secret_here"

If you do not wish to enter them through the terminal you can also enter the client id and secret in the config.json file in the resources folder.

## Usage and Arguments
Subreddits and users are positional arguments and must be entered at the start. Subreddits must be entered with any prefix whereas users must be untered with a "u/" before the username.
To download from a single subreddit, in this case /r/diy

    python3 RedditGrabber.py diy

You can also pass in a list of subreddits and users in the form of a txt file, which contains each subreddit or user on a newline.

    python3 RedditGrabber.py subs.txt

Below are all the optional arguments that you can use:

    -h, --help                     show this help message and exit

    -w WAIT, --wait WAIT            Change wait time between subreddits in seconds
    -p POSTS, --posts POSTS         Number of posts to grab on each cycle
    -o OUTPUT, --output OUTPUT      Set base directory to start download
    -t OUTPUT_TEMPLATE, --output_template OUTPUT_TEMPLATE
                                    Specify output template for download
    --sort SORT                     Sort submissions by 'hot', 'new' or 'top'
    -v, --verbose                   Sets verbose
    --blacklist BLACKLIST           Avoid downloading a user or subreddit
    --reddit_id REDDIT_ID           Reddit client ID
    --reddit_secret REDDIT_SECRET   Reddit client secret

### Output Template
By default the program saves by subreddit then user, if you would like to change this you can specify an output template.

The default can be represented by `-t '%(subreddit)s/%(author)s'`. If you would like to only save by author, you can do the following `-t '%(author)s'`. Note, this is only a way to change the layout within the download location, if you wish to change the download location itself specify that with `--output`.

Below are the available tags

* author: The author of the reddit submission
* subreddit: The subreddit the submissions was in

### Blacklist
If you wish to avoid downloading a specific user or subreddit you can blacklist them. To blacklist a user add their username like so `u/spez` or to blacklist a subreddit add it without any slashes like so `AskReddit`. Below are how they would look as a valid argument.

    python3 RedditGrabber.py --blacklist u/spez
    python3 RedditGrabber.py --blacklist AskReddit
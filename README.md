# GrabIt

GrabIt is a tool built to archive self-posts, images, gifs and videos from subreddit and users from Reddit. This program works through the command line and uses Python 3.

## Installation

Get your [Reddit API credentials](https://www.reddit.com/prefs/apps/).

Install all the dependencies.

    pip3 install -r requirements.txt

Add the Reddit API client ID and secret through the terminal as shown below, replace the string in quotes with your credentials:

    python3 RedditGrabber.py --reddit_id "client_id_here" --reddit_secret "client_secret_here"

If you do not wish to enter them through the terminal you can also enter the client id and secret in the config.json file in the resources folder.

## Usage and Arguments
Subreddits and users or a submission url are positional arguments and must be entered at the start. Subreddits must be entered without any prefix whereas users must be untered with a "u/" before the username.
To download from a single subreddit, in this case /r/diy

    python3 RedditGrabber.py diy

You can also pass in a list of subreddits and users in the form of a txt file, which contains each subreddit or user on a newline.

    python3 RedditGrabber.py subs.txt

Below are all the optional arguments that you can use:

    -h, --help                      show this help message and exit

    -p POSTS, --posts POSTS         Number of posts to grab on each cycle
    --search SEARCH                 Search for submissions in a subreddit
    --sort SORT                     Sort submissions by "hot", "new", "top", or "controversial"
    --time_filter TIME_FILTER       Filter sorted submission by "all", "day", "hour", "month", 
                                    "week", or "year"
    -w WAIT, --wait WAIT            Wait time between subreddits in seconds
    -c CYCLES, --cycles CYCLES      Number of times to repeat after wait time
    -o OUTPUT, --output OUTPUT      Set base directory to start download
    -t OUTPUT_TEMPLATE, --output_template OUTPUT_TEMPLATE
                                    Specify output template for download
    --allow_nsfw                    Include nsfw posts too
    -v, --verbose                   Sets verbose
    --pushshift                     Only use pushshift to grab submissions
    --ignore_duplicate              Ignore duplicate media submissions
    --blacklist BLACKLIST           Avoid downloading a user or subreddit
    --search SEARCH                 Search for submissions in a subreddit
    --reddit_id REDDIT_ID           Reddit client ID
    --reddit_secret REDDIT_SECRET   Reddit client secret
    --imgur_cookie IMGUR_COOKIE     Imgur authautologin cookie
    --db_location                   Set location of database file

### Output Template
By default the program saves by subreddit then user, if you would like to change this you can specify an output template.

The default can be represented by `-t '%(subreddit)s/%(author)s/%(id)s-%(title)s.%(ext)s'`. If you would like to only save by author and name the file by title, you can do the following `-t '%(author)s/%(title)s.%(ext)s'`.

Note, if you ues this parameter you must specify a template for the filename and use `%(ext)s` if you wish the files to save properly. If you only wish to change the output directory you can use the `--output` parameter.

Below are the available tags

| Tags         | Description                       |
| ------------ | --------------------------------- |
| author       | The author of the submission      |
| subreddit    | The subreddit of the submission   |
| id           | ID of the submission              |
| created_utc  | Time the submission was created   |
| title        | Title of the submission           |
| ext          | File extension                    |     

### Blacklist
If you wish to avoid downloading a specific user or subreddit you can blacklist them. To blacklist a user add their username like so `u/spez` or to blacklist a subreddit add it without any slashes like so `AskReddit`. Below are how they would look as a valid argument.

    python3 RedditGrabber.py --blacklist u/spez
    python3 RedditGrabber.py --blacklist AskReddit

### Search
You can search a subreddit using keywords along with sorting and time filters. Below are examples of a simple search on r/all for "breakfast cereal".

    python3 RedditGrabber.py all --search "breakfast cereal"

If you do not use the "--sort" flag then it will default to sorting by relevance, otherwise you can use "hot", "top", "new" or "comments". While using the search you can also get links by time using the "--time_filter" flag with "all", "day", "hour", "month", "week", or "year". Below is an example searching r/DataHoader for "sata fire" sorted by top submissions retrieving links only from the past year.

    python3 RedditGrabber.py DataHoarder --search "sata fire" --sort top --time_filter year

### Imgur Cookie
Imgur requires users to login to view NSFW content on their site, therefore if you wish to download such content that has been posted to Reddit you will need to provide the cookie used to verify an Imgur login. 

Using the flag provide the `authautologin` cookie data. You can find this cookie in your browser's storage inspector ([Chrome](https://developers.google.com/web/tools/chrome-devtools/storage/cookies), [Edge](https://docs.microsoft.com/en-us/microsoft-edge/devtools-guide/storage), [Firefox](https://developer.mozilla.org/en-US/docs/Tools/Storage_Inspector), [Safari](https://support.apple.com/en-gb/guide/safari-developer/dev43453fff5/mac)).

    python3 RedditGrabber.py --imgur_cookie "abcdefghi9876%jklmnop54321qrstu"

The cookies is then stored in the `config.json` file for future use. If you wish to update the cookie use the command above with the new value.
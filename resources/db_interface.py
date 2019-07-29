import sqlite3
import logging
import traceback
import sys


class DBInterface():

    def __init__(self, name):
        self.logger = logging.getLogger(__name__)
        self.name = name

        self.connect()
        self.createTables()

    def connect(self):
        self.logger.debug("Making database connection to {}".format(self.name))
        try:
            self.conn = sqlite3.connect(self.name)
        except sqlite3.OperationalError as e:
            self.logger.error('Check database_location in config, {}'.format(e))
            sys.exit()
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        self.logger.debug("Closing database connection to {}".format(self.name))
        self.c.close()
        self.conn.close()

    def createTables(self):
        self.logger.debug("Creating tables in database")
        self.c.execute("""CREATE TABLE IF NOT EXISTS submissions (
            submission_id text PRIMARY KEY,
            title text NOT NULL,
            u_date text NOT NULL,
            author_id integer NOT NULL,
            url text NOT NULL,
            subreddit_id integer NOT NULL,
                    FOREIGN KEY (subreddit_id) REFERENCES subreddits(subreddit_id),
                    FOREIGN KEY (author_id) REFERENCES authors(author_id)
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS subreddits (
            subreddit_id integer PRIMARY KEY,
            name text UNIQUE NOT NULL
            )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS authors (
            author_id integer PRIMARY KEY,
            name text UNIQUE NOT NULL
            )""")

        # migration
        self.c.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='posts'""")
        if (self.c.fetchone()):
            self.logger.debug("Using an old version of the database, starting migration...")
            old_c = self.conn.cursor()
            old_c.execute("SELECT * FROM posts")
            for row in old_c:
                self.insertPost(row[0], row[1], row[2], row[3], row[4])
            old_c.close()
            self.logger.debug("migration complete")
            self.c.execute("""DROP TABLE posts""")

    def insertPost(self, perma, title, u_date, author, url):
        parts = perma.split("/")
        subreddit = parts[2]
        submission_id = parts[4]

        subreddit_id = self.checkSubreddit(subreddit)
        if not subreddit_id:
            self.logger.debug("subreddit does not exist adding {}".format(subreddit))
            subreddit_id = self.insertSubreddit(subreddit)

        author_id = self.checkAuthor(author)
        if not author_id:
            self.logger.debug("author does not exist adding {}".format(author))
            author_id = self.insertAuthor(author)

        try:
            self.c.execute("""INSERT INTO submissions (
                submission_id, title, u_date, author_id, url, subreddit_id
            )
            VALUES (?, ?, ?, ?, ?, ?)""", (submission_id, title, u_date, author_id, url, subreddit_id))
            self.conn.commit()
        except sqlite3.IntegrityError as err:
            if "UNIQUE constraint failed: submissions.submission_id" in str(err):
                self.logger.debug("{} - Submission already exists, cannot add again".format(err))
            elif "FOREIGN KEY constraint failed" in str(err):
                self.logger.debug("{} - subreddit_id does not exist in subreddits".format(err))
            else:
                self.logger.debug(traceback.TracebackException.from_exception(err))

    def checkPost(self, submission_id):
        self.c.execute("""SELECT EXISTS(SELECT 1 FROM submissions WHERE submission_id=?)""",
                       (submission_id,))
        ret = self.c.fetchone()
        return ret[0]

    def insertAuthor(self, name):
        author_id = None
        try:
            self.c.execute("""INSERT INTO authors (name)
                VALUES (?)""", (name,))
            self.conn.commit()
            author_id = self.c.lastrowid
        except sqlite3.IntegrityError as err:
            if "UNIQUE constraint failed: authors.name" in str(err):
                self.logger.debug("{} - Author already exists, cannot add again".format(err))
            else:
                self.logger.debug(traceback.TracebackException.from_exception(err))
        return author_id

    def checkAuthor(self, name):
        self.c.execute("""SELECT author_id FROM authors WHERE name=?""", (name,))
        ret = self.c.fetchone()
        if ret:
            ret = ret[0]
        return ret

    def insertSubreddit(self, name):
        subreddit_id = None

        try:
            self.c.execute("""INSERT INTO subreddits (name)
                VALUES (?)""", (name,))
            self.conn.commit()
            subreddit_id = self.c.lastrowid
        except sqlite3.IntegrityError as err:
            if "UNIQUE constraint failed: subreddits.name" in str(err):
                self.logger.debug("{} - Subrteddit already exists, cannot add again".format(err))
            else:
                self.logger.debug(traceback.TracebackException.from_exception(err))
        return subreddit_id

    def checkSubreddit(self, name):
        self.c.execute("""SELECT subreddit_id FROM subreddits WHERE name=?""", (name,))
        ret = self.c.fetchone()
        if ret:
            ret = ret[0]
        return ret

    def lastRow(self):
        self.c.execute("""SELECT submission_id, title, author_id, subreddit_id from submissions
            ORDER BY rowid DESC limit 5""")
        return self.c.fetchall()

    def getAuthor(self, author_id):
        self.c.execute("""SELECT name FROM authors WHERE author_id=?""", (author_id,))
        ret = self.c.fetchone()
        if ret:
            ret = ret[0]
        return ret

    def getSubreddit(self, author_id):
        self.c.execute("""SELECT name FROM subreddits WHERE subreddit_id=?""", (author_id,))
        ret = self.c.fetchone()
        if ret:
            ret = ret[0]
        return ret

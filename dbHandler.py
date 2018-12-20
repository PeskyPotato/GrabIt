import sqlite3

'''
Creates a database file is one does not already
exist.
'''
def createTable():
    conn = sqlite3.connect('downloaded.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS posts (perma TEXT NOT NULL UNIQUE, title TEXT, udate TEXT, author TEXT, url TEXT, PRIMARY KEY (perma))')
    c.close()
    conn.close()

'''
Enter submission information into the database.
Duplicates return 0 and entry is skippped, otherwise
it is logged and a 0 is returned.
'''
def dbWrite(perma, title, udate, author, url):
    try:
        conn = sqlite3.connect('downloaded.db')
        c = conn.cursor()
        c.execute("INSERT INTO posts (perma, title, udate, author, url) VALUES (?, ?, ?, ?, ?)", (perma, title, udate, str(author), url))
        conn.commit()
    except sqlite3.IntegrityError:
        c.close()
        conn.close()
        return 0

    c.close()
    conn.close()
    return 1

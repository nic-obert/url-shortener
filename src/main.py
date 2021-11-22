import sqlite3
import os
from typing import Union
from flask import Flask, redirect, Response, request, render_template


# Create the application
app = Flask(__name__)
DATABASE_PATH = 'urls.db'


def initialize_database() -> None:
    # Check if the database file exists
    if os.path.exists(DATABASE_PATH):
        # Check if urls table exists
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls'")
            # If the urls table doesn't exist, create it
            if cursor.fetchone() is None:
                cursor.execute('CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT)')
    
    else:
        # Create the database and the urls table
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT);')


def get_url(id: int) -> Union[str, None]:
    # Connect to the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM urls WHERE id = ?', (id,))
        data = cursor.fetchone()
        # If the url exists, return it. Otherwise, return None
        if data:
            return data[0]
        return None


def store_url(url: str) -> int:
    # Connect to the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urls (url) VALUES (?)', (url,))
        # Return the id of the new url
        return cursor.lastrowid


def exists_url(url: str) -> bool:
    # Connect to the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM urls WHERE url = ?', (url,))
        # If the url exists, return True. Otherwise, return False
        return cursor.fetchone() is not None


def get_url_id(url: str) -> int:
    # Connect to the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM urls WHERE url = ?', (url,))
        # Return the id of the url
        return cursor.fetchone()[0]


def shorten_url(url: str) -> str:
    if exists_url(url):
        id = get_url_id(url)
    else:
        id = store_url(url)
    
    # Return the shortened url
    return request.base_url + '?id=' + str(id)
    

# Create the home page route
@app.route('/', methods=['GET'])
def index():
    # Check if the id parameter exists
    id = request.args.get('id')
    if id:
        # Validate the id
        if id.isdigit():
            # Get the url from the database.
            url = get_url(int(id))
            # If the url exists, redirect to it.
            if url:
                return redirect(url)
        
        # If the id is invalid, return a 404 error
        return Response('<h1>Invalid URL</h1>', status=404)

    # Check if the url parameter exists
    url = request.args.get('url')
    if url:
        # Shorten the url and return it
        shortened_url = shorten_url(url.strip())
        return render_template('index.html', url=shortened_url)
    
    # If the id and url parameters don't exist, return just the home page
    return render_template('index.html')


# Python's kind of main function
if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)


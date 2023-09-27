import string
import sqlite3
import random
import urllib.parse
from flask import Flask, request, redirect, render_template

app = Flask(__name__)

# Database
conn = sqlite3.connect('shortlinks.db')
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS url_mappings (
    shortcode TEXT PRIMARY KEY,
    long_url TEXT,
    amount_used NUMERIC
    )
    '''
)
conn.commit()
conn.close()


def generate_shortcode():
    """Generate a random shortcode."""
    characters = string.ascii_letters + string.digits
    shortcode = ''.join(random.choice(characters) for _ in range(6))
    return shortcode

def add_to_database(website_url):
    """Adds a shortcode and website to the database"""
    conn = sqlite3.connect('shortlinks.db')
    cursor = conn.cursor()

    cursor.execute('SELECT shortcode FROM url_mappings WHERE long_url = ?', (website_url,))
    result = cursor.fetchone()
    if result:
        shortcode = result[0]
    else:
        shortcode = generate_shortcode()
        cursor.execute('INSERT INTO url_mappings (shortcode, long_url, amount_used) VALUES (?, ?, ?)', (shortcode, website_url, 0))
        conn.commit()
    conn.close()

    return shortcode

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/<shortcode>', methods=['GET'])
def get_url(shortcode):
    conn = sqlite3.connect("shortlinks.db")
    cursor = conn.cursor()
    cursor.execute('SELECT long_url FROM url_mappings WHERE shortcode = ?', (shortcode,))
    result = cursor.fetchone()

    if result:
        long_url = result[0]
        # add one
        update_query = "UPDATE url_mappings SET amount_used = amount_used + 1 WHERE shortcode = ?"
        cursor.execute(update_query, (shortcode,))
        conn.commit()
        
        return redirect(long_url)
    else:
        return 'Short URL not found'
    conn.close()

@app.route('/make-short-url', methods=['POST', 'GET'])
def short_url():
    if request.method == 'POST':
        data = request.get_json()
        website = data.get('website', None)

        parsed_url = urllib.parse.urlparse(website)
        if not parsed_url.scheme in ('http', 'https'):
            return 'Make sure you are sending a vaild website'
    

        code = add_to_database(website)

        return f"/{code}"

app.run(host="0.0.0.0")


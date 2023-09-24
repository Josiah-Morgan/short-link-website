import string
import sqlite3
import random
from flask import Flask, request

app = Flask(__name__)

# Database
conn = sqlite3.connect('shortlinks.db')
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS url_mappings (
    shortcode TEXT PRIMARY KEY,
    long_url TEXT
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
    print(result)
    if result:
        shortcode = result[0]
    else:
        shortcode = generate_shortcode()
        cursor.execute('INSERT INTO url_mappings (shortcode, long_url) VALUES (?, ?)', (shortcode, website_url))
        conn.commit()
    conn.close()

    return shortcode

@app.route('/')
def index():
    return 'hijj'

@app.route('/make-short-url', methods=['POST', 'GET'])
def short_url():
    if request.method == 'POST':
        data = request.get_json()
        website = data.get('website', None)

        code = add_to_database(website)

        return f"/{code}"


app.run(host="0.0.0.0")



# send links
# return code
# add link and code to a database
# when people request code send to link (redirect)
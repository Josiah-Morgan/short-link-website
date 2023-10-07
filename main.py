import random
import sqlite3
import string
import urllib.parse

from flask import Flask, jsonify, redirect, render_template, request

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

def add_to_database(website_url, alias):
    """Adds a shortcode and website to the database"""

    conn = sqlite3.connect('shortlinks.db')
    cursor = conn.cursor()

    if alias:
        shortcode = alias
        check = check_shortcode_in_database(shortcode)
        if check:
            cursor.execute('INSERT INTO url_mappings (shortcode, long_url, amount_used) VALUES (?, ?, ?)', (shortcode, website_url, 0))
            conn.commit()
            conn.close()
            return True, shortcode
        else:
            return False, 'Alias already used'


    cursor.execute('SELECT shortcode FROM url_mappings WHERE long_url = ?', (website_url,))
    result = cursor.fetchone()
    if result:
        shortcode = result[0]
    else:            
        shortcode = generate_shortcode()
        cursor.execute('INSERT INTO url_mappings (shortcode, long_url, amount_used) VALUES (?, ?, ?)', (shortcode, website_url, 0))
        conn.commit()
    conn.close()

    return True, shortcode

def check_shortcode_in_database(shortcode):
    conn = sqlite3.connect('shortlinks.db')
    cursor = conn.cursor()

    cursor.execute('SELECT shortcode FROM url_mappings WHERE shortcode = ?', (shortcode,))
    result = cursor.fetchone()
    if result:
        return False
    else:
        return True


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

@app.route('/make-short-url', methods=['POST'])
def short_url():

    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        data = request.get_json()
        website = data.get('website', None)
    elif content_type == 'application/x-www-form-urlencoded':
        website = request.form.get('longUrl', None)
        alias = request.form.get('alias', None)
    else:
        return 'Issue'

    parsed_url = urllib.parse.urlparse(website)
    if not parsed_url.scheme in ('http', 'https'):
        return 'Make sure you are sending a vaild website'
    

    check, message = add_to_database(website, alias)
    if not check:
        return jsonify({'Erorr': message})
    
    # message = shortcode

    if content_type == 'application/json':
        return jsonify({'short_url': f'website/{message}', 'shortcode': message, 'long_url': website}) # put times used
    else:
        return render_template('made_short_link.html', shortcode=message, long_url=website)

#@app.route('/generate-qr', methods=['POST'])
#def generate_qr_code():
    #website_url = request.json.get('url')
    #data = "https://www.thepythoncode.com"
    # output file name
    #filename = "site.png"
    # generate qr code
    #img = qrcode.make(data)
    # save img to a file
    #img.save(filename)
    #return jsonify({'message': 'QR code generated successfully'})

app.run(host="0.0.0.0", debug=True)



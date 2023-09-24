from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'hijj'

@app.route('/make-short-url', methods=['POST'])
def short_url():
    data = request.get_json()
    website = data.get('website', None)
    return 'data'


app.run(host="0.0.0.0")



# send links
# return code
# add link and code to a database
# when people request code send to link (redirect)
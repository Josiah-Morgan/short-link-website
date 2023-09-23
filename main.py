from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'hijj'

app.run(host="0.0.0.0")
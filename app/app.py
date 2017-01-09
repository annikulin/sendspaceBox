import json
import requests
from flask import Flask, render_template, request, session, url_for

app = Flask(__name__)


@app.route('/')
def index():
    if 'access_token' not in session:
        return render_template('login.html', redirect_url=url_for('authorized', _external=True), client_id = app.config['DROPBOX_APP_ID'])
    return render_template('index.html')


@app.route('/authorized')
def authorized():
    code = request.args.get('code')

    params = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': app.config['DROPBOX_APP_ID'],
        'client_secret': app.config['DROPBOX_APP_SECRET'],
        'redirect_uri': url_for('authorized', _external=True)
    }
    response = requests.post('https://api.dropboxapi.com/1/oauth2/token', params=params)
    if response.status_code != 200:
        raise Exception('Something went wrong :(')
    session['access_token'] = json.loads(response.text)['access_token']

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return render_template('login.html', redirect_url=url_for('authorized', _external=True), client_id = app.config['DROPBOX_APP_ID'])


if __name__ == '__main__':
    app.config.from_pyfile('config.py')
    app.run()

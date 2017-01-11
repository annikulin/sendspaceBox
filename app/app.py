import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import requests
from flask import Flask, render_template, request, session, url_for
from client import DropboxClient, DropboxSendspaceSync, SendspaceClient

app = Flask(__name__)
sync_processes = dict()


@app.route('/')
def index():
    if 'access_token' not in session:
        return render_template('login.html', redirect_url=url_for('authorized', _external=True),
                               client_id=app.config['DROPBOX_APP_ID'])

    synced_files_before = session['access_token'] in sync_processes
    if synced_files_before:
        finished_previous_sync = sync_processes[session['access_token']].done()
        errors = sync_processes[session['access_token']].errors
        logs = sync_processes[session['access_token']].logs
    else:
        finished_previous_sync, errors, logs = False, list(), list()


    return render_template('index.html', synced_files_before=synced_files_before,
                           finished_previous_sync=finished_previous_sync, errors=errors, logs=logs)


@app.route('/authorized')
def authorized():
    code = request.args.get('code')

    params = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': app.config['DROPBOX_APP_ID'],
        'client_secret': app.config['DROPBOX_APP_SECRET'],
        'redirect_uri': url_for('authorized', _external=True, _scheme='https')
    }
    response = requests.post('https://api.dropboxapi.com/1/oauth2/token', params=params)
    if response.status_code != 200:
        http_error_msg = '%s %s Error message: %s' % (response.status_code, response.reason, response.text)
        raise Exception(http_error_msg)
    session['access_token'] = json.loads(response.text)['access_token']

    return index()


@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return render_template('login.html', redirect_url=url_for('authorized', _external=True),
                           client_id=app.config['DROPBOX_APP_ID'])


@app.route('/sync', methods=['POST'])
def sync():
    sendspace_username = request.form.get('sendspace_username')
    sendspace_password = request.form.get('sendspace_password')
    sendspace_key = request.form.get('sendspace_key')

    dropbox_client = DropboxClient(session['access_token'])
    sendspace_client = SendspaceClient(sendspace_key, sendspace_username, sendspace_password)
    sync = DropboxSendspaceSync(dropbox_client, sendspace_client)
    sync.sync_files()
    sync_processes[session['access_token']] = sync

    return index()


if __name__ == '__main__':
    if os.path.exists('config.py'):
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping({
            'SECRET_KEY': os.environ['SECRET_KEY'],
            'SESSION_TYPE': os.environ['SESSION_TYPE'],
            'DROPBOX_APP_ID': os.environ['DROPBOX_APP_ID'],
            'DROPBOX_APP_SECRET': os.environ['DROPBOX_APP_SECRET']
        })

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

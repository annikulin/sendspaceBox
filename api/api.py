import hashlib
import requests
import xml.etree.ElementTree as ET


def post_request(url, headers=None, json=None, params=None, files=None, data=None):
    r = requests.post(url, headers=headers, json=json, params=params, files=files, data=data)

    if r.status_code != 200:
        http_error_msg = '%s %s Error message: %s' % (r.status_code, r.reason, r.content)
        raise Exception(http_error_msg)

    return r


class DropboxAPI(object):
    _API_VERSION = '2'
    _DEFAULT_DOMAIN = 'dropboxapi.com'
    _HOST_API = 'api'
    _HOST_CONTENT = 'content'

    def __init__(self, oauth2_access_token):
        assert len(oauth2_access_token) > 0, 'OAuth2 access token cannot be empty.'
        self._oauth2_access_token = oauth2_access_token

    def download(self, path):
        url = self._build_url('download', is_content_url=True)
        headers = self._build_headers({'Dropbox-API-Arg': '{"path": "%s"}' % path})

        return post_request(url, headers=headers).content

    def list_folder(self, path, recursive=False):
        url = self._build_url('list_folder')
        headers = self._build_headers({'Content-Type': 'application/json'})

        # Dropbox API requires to specify the root folder as an empty string rather than as "/"
        if path == '/':
            path = ''

        data = {'path': path, 'recursive': recursive, 'include_media_info': False, 'include_deleted': False,
                'include_has_explicit_shared_members': False}
        return post_request(url, headers=headers, json=data).content

    def list_folder_continue(self, cursor):
        url = self._build_url('list_folder/continue')
        headers = self._build_headers({'Content-Type': 'application/json'})

        data = {'cursor': cursor}
        return post_request(url, headers=headers, json=data).content

    def _build_headers(self, extra_headers):
        headers = {'Authorization': 'Bearer %s' % self._oauth2_access_token}
        headers.update(extra_headers)
        return headers

    def _build_url(self, route, is_content_url=False):
        data = {'host': self._HOST_CONTENT if is_content_url else self._HOST_API, 'domain': self._DEFAULT_DOMAIN,
                'api_version': self._API_VERSION, 'route': route}
        return 'https://{host}.{domain}/{api_version}/files/{route}'.format(**data)


class SendspaceAPI(object):
    _API_VERSION = 1.2
    _API_URL = 'http://api.sendspace.com/rest/'

    def __init__(self, api_key, username, password):
        assert len(api_key) > 0, 'API Key cannot be empty.'
        self._api_key = api_key
        assert len(username) > 0, 'Username cannot be empty.'
        self._username = username
        assert len(password) > 0, 'Password cannot be empty.'
        self._password = password

        self._create_session_key()

    def _create_session_key(self):
        payload = {'method': 'auth.createtoken', 'api_key': self._api_key, 'api_version': self._API_VERSION}
        r = post_request(self._API_URL, params=payload)
        token = ET.fromstring(r.content)[0].text

        # lowercase(md5(token+lowercase(md5(password))))
        tokened_password = hashlib.md5(token + hashlib.md5(self._password).hexdigest().lower()).hexdigest().lower()
        payload = {'method': 'auth.login', 'token': token, 'api_version': self._API_VERSION,
                   'user_name': self._username, 'tokened_password': tokened_password}
        r = post_request(self._API_URL, params=payload)
        self._session_key = ET.fromstring(r.content)[0].text

    def upload(self, filename, file):
        payload = {'method': 'upload.getinfo', 'session_key': self._session_key}
        r = post_request(self._API_URL, params=payload)

        response_xml = ET.fromstring(r.content)
        url = response_xml[0].attrib['url']
        max_file_size = response_xml[0].attrib['max_file_size']
        upload_identifier = response_xml[0].attrib['upload_identifier']
        extra_info = response_xml[0].attrib['extra_info']

        form_details = {'MAX_FILE_SIZE': max_file_size, 'UPLOAD_IDENTIFIER': upload_identifier,
                        'extra_info': extra_info, 'notify_uploader': 0}
        file = {'userfile': (filename, file)}
        post_request(url, data=form_details, files=file)

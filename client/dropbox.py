import json
import requests
from model import File, Folder


def post_request(url, headers=None, json=None, params=None, files=None, data=None):
    r = requests.post(url, headers=headers, json=json, params=params, files=files, data=data)

    if r.status_code != 200:
        http_error_msg = '%s %s Error message: %s' % (r.status_code, r.reason, r.content)
        raise Exception(http_error_msg)

    return r


def parse_entries(entries, folders, files):
    for entry in entries:
        if entry['.tag'] == 'folder':
            folders.append(Folder(entry['id'], entry['path_display']))
        else:
            files.append(File(entry['id'], entry['name'], entry['path_display']))
    return folders, files


class DropboxClient(object):
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

    def list_folder(self, path='/', recursive=False):
        url = self._build_url('list_folder')
        headers = self._build_headers({'Content-Type': 'application/json'})

        # Dropbox API requires to specify the root folder as an empty string rather than as "/"
        if path == '/':
            path = ''

        data = {
            'path': path,
            'recursive': recursive,
            'include_media_info': False,
            'include_deleted': False,
            'include_has_explicit_shared_members': False
        }
        json_response = post_request(url, headers=headers, json=data).content
        response = json.loads(json_response)

        folders, files = parse_entries(response['entries'], [], [])

        while response['has_more']:
            json_response = self._list_folder_continue(response['cursor'])
            response = json.loads(json_response)
            folders, files = parse_entries(response['entries'], folders, files)

        return folders, files

    def _list_folder_continue(self, cursor):
        url = self._build_url('list_folder/continue')
        headers = self._build_headers({'Content-Type': 'application/json'})

        data = {'cursor': cursor}
        return post_request(url, headers=headers, json=data).content

    def _build_headers(self, extra_headers):
        headers = {'Authorization': 'Bearer %s' % self._oauth2_access_token}
        headers.update(extra_headers)
        return headers

    def _build_url(self, route, is_content_url=False):
        data = {
            'host': self._HOST_CONTENT if is_content_url else self._HOST_API,
            'domain': self._DEFAULT_DOMAIN,
            'api_version': self._API_VERSION,
            'route': route
        }
        return 'https://{host}.{domain}/{api_version}/files/{route}'.format(**data)

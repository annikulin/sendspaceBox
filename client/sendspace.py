import hashlib
import xml.etree.ElementTree as ET

from requests_toolbelt import MultipartEncoder
import requests

from client.model import Folder, File


def post_request(url, headers=None, json=None, params=None, files=None, data=None, expect_xml_response=True):
    response_xml = requests.post(url, headers=headers, json=json, params=params, files=files, data=data)

    if response_xml.status_code != 200:
        http_error_msg = '%s %s Error message: %s' % (
            response_xml.status_code, response_xml.reason, response_xml.content)
        raise Exception(http_error_msg)

    if expect_xml_response:
        response = ET.fromstring(response_xml.content)
        if response.attrib['status'] != 'ok':
            raise Exception('Sendspace API request failed. Reason: %s. Info: %s' % (
                response[0].attrib['text'], response[0].attrib['info']))
    else:
        response = response_xml.content
        if 'upload_status=ok' not in response:
            raise Exception('Sendspace API file upload failed. Info: %s' % response)

    return response


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''


class SendspaceClient(object):
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
        response = post_request(self._API_URL, params=payload)
        token = response[0].text

        # lowercase(md5(token+lowercase(md5(password))))
        tokened_password = hashlib.md5(token + hashlib.md5(self._password).hexdigest().lower()).hexdigest().lower()
        payload = {'method': 'auth.login', 'token': token, 'api_version': self._API_VERSION,
                   'user_name': self._username, 'tokened_password': tokened_password}
        response = post_request(self._API_URL, params=payload)
        self._session_key = response[0].text

    def upload(self, filename, file_stream):
        payload = {'method': 'upload.getinfo', 'session_key': self._session_key}
        response = post_request(self._API_URL, params=payload)

        url = response[0].attrib['url']
        max_file_size = response[0].attrib['max_file_size']
        upload_identifier = response[0].attrib['upload_identifier']
        extra_info = response[0].attrib['extra_info']

        form_details = MultipartEncoder(fields={
            'MAX_FILE_SIZE': max_file_size,
            'UPLOAD_IDENTIFIER': upload_identifier,
            'extra_info': extra_info,
            'userfile': (filename, file_stream.read()),
            'notify_uploader': '0'
        })
        response = post_request(url, data=form_details, expect_xml_response=False, headers={'Content-Type': form_details.content_type})
        file_id = find_between(response, 'file_id=', '\n')
        return file_id

    def delete_file(self, file_id):
        payload = {
            'method': 'files.delete',
            'file_id': file_id,
            'session_key': self._session_key
        }
        post_request(self._API_URL, params=payload)

    def get_folder_content(self, folder_id=0):
        payload = {
            'method': 'folders.getContents',
            'folder_id': folder_id,
            'session_key': self._session_key
        }
        response = post_request(self._API_URL, params=payload)
        folders, files = [], []
        for entry in response:
            if entry.tag == 'folder':
                folder = Folder(entry.attrib['id'], entry.attrib['name'])
                folder.sendspace_id = entry.attrib['id']
                folders.append(folder)
            elif entry.tag == 'file':
                file = File(entry.attrib['id'], entry.attrib['name'])
                file.sendspace_folder_id = entry.attrib['folder_id']
                files.append(file)
        return folders, files

    def create_folder(self, name, parent_folder_id=0):
        payload = {
            'method': 'folders.create',
            'name': name,
            'parent_folder_id': parent_folder_id,
            'session_key': self._session_key
        }
        response = post_request(self._API_URL, params=payload)
        return response[0].attrib['id']

    def delete_folder(self, folder_id):
        payload = {
            'method': 'folders.delete',
            'folder_id': folder_id,
            'session_key': self._session_key
        }
        post_request(self._API_URL, params=payload)

    def move_file_to_folder(self, file_id, folder_id):
        payload = {
            'method': 'files.moveToFolder',
            'folder_id': folder_id,
            'file_id': file_id,
            'session_key': self._session_key
        }
        post_request(self._API_URL, params=payload)

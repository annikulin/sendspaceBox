from client import DropboxClient, SendspaceClient, DropboxSendspaceSync

token = '###'
drop = DropboxClient(token)

sendspace_key = '###'
sendspace_username = '###'
sendspace_password = '###'
send = SendspaceClient(sendspace_key, sendspace_username, sendspace_password)

sync = DropboxSendspaceSync(drop, send)
sync.sync_files()
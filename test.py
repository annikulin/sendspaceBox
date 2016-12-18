from client import DropboxClient, SendspaceClient, DropboxSendspaceSync

token = 'aovp6HXZg_AAAAAAAAAnwuf1knl4cLCZvufk4dzHoleqPPlI6SuRea5O0OschOPG'
drop = DropboxClient(token)

sendspace_key = 'Z7FYXR0RIW'
sendspace_username = 'antonnik94@gmail.com'
sendspace_password = 'U2QNDhpMrF'
send = SendspaceClient(sendspace_key, sendspace_username, sendspace_password)

sync = DropboxSendspaceSync(drop, send)
sync.sync_files()
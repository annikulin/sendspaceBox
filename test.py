from client import DropboxClient, SendspaceClient

token = 'aovp6HXZg_AAAAAAAAAnwuf1knl4cLCZvufk4dzHoleqPPlI6SuRea5O0OschOPG'
drop = DropboxClient(token)
folders, files = drop.list_folder('/', recursive=True)

sendspace_key = 'Z7FYXR0RIW'
sendspace_username = 'antonnik94@gmail.com'
sendspace_password = 'U2QNDhpMrF'
send = SendspaceClient(sendspace_key, sendspace_username, sendspace_password)
folders, files = send.get_folder_content()

for folder in folders:
    print folder

for file in files:
    print file

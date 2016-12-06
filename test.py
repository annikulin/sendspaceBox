from api import SendspaceAPI, DropboxAPI

token = 'aovp6HXZg_AAAAAAAAAnwuf1knl4cLCZvufk4dzHoleqPPlI6SuRea5O0OschOPG'
drop = DropboxAPI(token)
print drop.list_folder('/')

sendspace_key = 'Z7FYXR0RIW'
sendspace_username = 'antonnik94@gmail.com'
sendspace_password = 'U2QNDhpMrF'
send = SendspaceAPI(sendspace_key, sendspace_username, sendspace_password)
send.upload('test2.txt', 'IT WORKS 2!')

# sendspaceBox

sendspaceBox is a simple service which is able to back-up user’s files from Dropbox to  [sendSpace](https://www.sendspace.com). Service can be accessed through a simple website where the user authenticates to Dropbox using OAuth2 and give credentials for sendSpace. Once the user is authenticated, the back-up process can be started.

Service searches recursively in all directories comparing files by only their names. Search process is executed in one thread while actual copying (downloading/uploading) is be done in parallel at the same time.

### Tech

* Python3
* [Flask](http://flask.pocoo.org/) - Web microframework
* [Requests](http://docs.python-requests.org/) - HTTP library for Python, safe for human consumption
* [Twitter Bootstrap] - some CSS styles

### Deployment

Currently service is deployed [on Heroku on free dynos](https://sendspacebox.herokuapp.com/) (so it might take some time for it to start because it's sleeping when not active).
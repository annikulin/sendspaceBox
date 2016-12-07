class File(object):
    def __init__(self, id, name, path, folder=None):
        self.id = id
        self.name = name
        self.path = path
        self.folder = folder

    def __str__(self):
        return 'File [%s]' % self.name


class Folder(object):
    def __init__(self, id, path):
        self.id = id
        self.path = path

    def __str__(self):
        return 'Folder [%s]' % self.path

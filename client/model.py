class File(object):
    def __init__(self, id, name, path=None):
        self.id = id
        self.name = name
        self.path = path

    def __str__(self):
        return 'File [%s]' % self.name

    def __eq__(self, other):
        return self.name == other.name


class Folder(object):
    def __init__(self, id, name=None, path=None):
        self.id = id
        self.name = name
        self.path = path

    def __str__(self):
        return 'Folder [%s] [%s]' % (self.name, self.path)

    def __eq__(self, other):
        return self.name == other.name

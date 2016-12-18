from client.model import Folder


class DropboxSendspaceSync(object):
    def __init__(self, dropbox, sendspace):
        self._dropbox = dropbox
        self._sendspace = sendspace

        self.files_to_delete, self.files_to_create = list(), list()

    def sync_files(self):
        root_folder = Folder(0, path='/')
        root_folder.sendspace_id = 0
        self._sync_folder(root_folder)

        self._delete_files()
        self._create_files()

    def _sync_folder(self, folder):
        print 'Syncing {}'.format(folder)

        dropbox_folders, dropbox_files = self._dropbox.list_folder(folder.path)
        sendspace_folders, sendspace_files = self._sendspace.get_folder_content(folder.sendspace_id)

        folders = self._sync_folders(dropbox_folders, sendspace_folders, folder)
        self._sync_files(dropbox_files, sendspace_files, folder)

        for folder in folders:
            self._sync_folder(folder)

    def _sync_folders(self, dropbox_folders, sendspace_folders, current_folder):
        for folder in dropbox_folders:
            if folder not in sendspace_folders:
                print '[CREATE] {}'.format(folder)
                folder_id = self._sendspace.create_folder(folder.name, parent_folder_id=current_folder.sendspace_id)
                folder.sendspace_id = folder_id
            else:
                matches = [x for x in sendspace_folders if x.name == folder.name]
                folder.sendspace_id = matches[0].sendspace_id
                sendspace_folders.remove(matches[0])

        for folder in sendspace_folders:
            print '[DELETE] {}'.format(folder)
            self._sendspace.delete_folder(folder.sendspace_id)

        return dropbox_folders

    def _sync_files(self, dropbox_files, sendspace_files, folder):
        files_to_create = [x for x in dropbox_files if x not in sendspace_files]
        for file in files_to_create:
            file.folder = folder
        to_delete = [x for x in sendspace_files if x not in dropbox_files]

        self.files_to_delete = self.files_to_delete + to_delete
        self.files_to_create = self.files_to_create + files_to_create

    def _delete_files(self):
        for file_to_delete in self.files_to_delete:
            print '[DELETE] {}'.format(file_to_delete)
            self._sendspace.delete_file(file_to_delete.id)

    def _create_files(self):
        for file_to_create in self.files_to_create:
            print '[CREATE] {}'.format(file_to_create)
            file_stream = self._dropbox.download(file_to_create.path)
            file_id = self._sendspace.upload(file_to_create.name, file_stream)
            self._sendspace.move_file_to_folder(file_id, file_to_create.folder.sendspace_id)

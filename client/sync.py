from concurrent.futures import ThreadPoolExecutor

from client.model import Folder


class DropboxSendspaceSync(object):
    def __init__(self, dropbox, sendspace):
        self._dropbox = dropbox
        self._sendspace = sendspace

        self.errors = list()
        self.futures = list()

    def sync_files(self):
        self.errors.clear()
        self.futures.clear()

        self._executor = ThreadPoolExecutor(max_workers=10)

        root_folder = Folder(0, path='/')
        root_folder.sendspace_id = 0
        future = self._executor.submit(self._sync_folder, root_folder)
        self.futures.append(future)

        self._executor.shutdown(wait=False)

    def _sync_folder(self, folder):
        print('Syncing {}'.format(folder))
        try:
            dropbox_folders, dropbox_files = self._dropbox.list_folder(folder.path)
            sendspace_folders, sendspace_files = self._sendspace.get_folder_content(folder.sendspace_id)

            folders = self._sync_folders(dropbox_folders, sendspace_folders, folder)
            self._sync_files(dropbox_files, sendspace_files, folder)

            for folder in folders:
                self._sync_folder(folder)
        except Exception as e:
            self.errors.append('Failed to sync folder: %s. Error: %s' % (folder, str(e)))

    def _sync_folders(self, dropbox_folders, sendspace_folders, current_folder):
        for folder in dropbox_folders:
            if folder not in sendspace_folders:
                print('[CREATE] {}'.format(folder))
                folder_id = self._sendspace.create_folder(folder.name, parent_folder_id=current_folder.sendspace_id)
                folder.sendspace_id = folder_id
            else:
                matches = [x for x in sendspace_folders if x.name == folder.name]
                folder.sendspace_id = matches[0].sendspace_id
                sendspace_folders.remove(matches[0])

        for folder in sendspace_folders:
            print('[DELETE] {}'.format(folder))
            self._sendspace.delete_folder(folder.sendspace_id)

        return dropbox_folders

    def _sync_files(self, dropbox_files, sendspace_files, folder):
        files_to_create = [x for x in dropbox_files if x not in sendspace_files]
        for file in files_to_create:
            file.folder = folder
        files_to_delete = [x for x in sendspace_files if x not in dropbox_files]

        for file_to_create in files_to_create:
            future = self._executor.submit(self._create_file, file_to_create)
            self.futures.append(future)
        for file_to_delete in files_to_delete:
            future = self._executor.submit(self._delete_file, file_to_delete)
            self.futures.append(future)

    def _delete_file(self, file_to_delete):
        print('[DELETE] {}'.format(file_to_delete))
        try:
            self._sendspace.delete_file(file_to_delete.id)
        except Exception as e:
            self.errors.append('Failed to delete file: %s. Error: %s' % (file_to_delete, str(e)))

    def _create_file(self, file_to_create):
        print('[CREATE] {}'.format(file_to_create))
        try:
            file_stream = self._dropbox.download(file_to_create.path)
            file_id = self._sendspace.upload(file_to_create.name, file_stream)
            self._sendspace.move_file_to_folder(file_id, file_to_create.folder.sendspace_id)
        except Exception as e:
            self.errors.append('Failed to create file: %s. Error: %s' % (file_to_create, str(e)))

    def done(self):
        for future in self.futures:
            if not future.done():
                return False
        return True

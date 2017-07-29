from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload
import glob
from collections import namedtuple

# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = '~/.credentials/client_secret.json'
APPLICATION_NAME = 'pythonDrive'
MIMES = {
    '.jpg': 'image/jpeg',
    '.csv': 'text/plain'
}
EXTENSIONS = ['.jpg', '.csv']


class pDrive():
    def __init__(self, directories, extensions=None, credentials=None,
                 no_web_auth_flags=False
                 ):
        self.directories = directories
        self.no_web_auth_flags = no_web_auth_flags
        if no_web_auth_flags:
            self.args = tools.argparser.parse_args()
            self.args.noauth_local_webserver = True
        if not extensions:
            self.extensions = EXTENSIONS
            print('No extensions specified. using {}'.format(EXTENSIONS))

        self.credentials = (CLIENT_SECRET_FILE if not credentials else
                            credentials)

        self.file_paths = [os.path.join(d, '*' + e) for d in self.directories
                           for e in self.extensions]

        self.filesfromdirs = []
        Filetup = namedtuple('Filetup', 'parent files')

        for path in self.file_paths:
            self.filesfromdirs.append(Filetup(os.path.dirname(path),
                                              glob.glob(path)))

        # todo: error handling
        print('files to load: {}'.format(
            [d.files for d in self.filesfromdirs if d.files]
        )
              )
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=self.http)

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir,
                                       '{}.json'.format(APPLICATION_NAME))
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.credentials, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if self.no_web_auth_flags:
                print("working with no_web_auth")
                credentials = tools.run_flow(flow, store, self.args)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_mimetype(self, filename):
        _filename, extension = os.path.splitext(filename)
        return MIMES[extension]

    def create_dirs(self, dirs, parent_id):
        if dirs:
            folder_name = dirs.pop(0)
            folder_exists = self.folder_exists(parent_id, folder_name)

            if folder_exists:
                new_parent_id = folder_exists
            else:
                print('folder: {} dose not exists'.format(folder_name))
                new_parent_id = self.create_folder(folder_name, parent_id)

            return self.create_dirs(dirs, new_parent_id)
        else:
            return parent_id

    def folder_exists(self, parent_id, folder_name):
        '''
            Check if the folder exists in parent
        '''
        query = "\'{}\' in parents".format(parent_id)
        results = self.service.files().list(
            q=query,
            spaces='drive'
        ).execute()
        items = results.get('files', [])

        for item in items:
            if folder_name == item['name']:
                return item['id']

        return None

    def create_folder(self, folder, parent_id):
        print("Creating new folder: %s" % (folder))
        file_metadata = {
            'name': folder,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id],
        }
        folder = self.service.files().create(body=file_metadata,
                                             fields='id').execute()
        self.sub_folder_id = folder.get('id')
        return self.sub_folder_id

    def upload_file(self, filename, parent_id=None):
        if not filename:
            pass
        mimetype = self.get_mimetype(filename)
        file_metadata = {
            'name': os.path.split(filename)[-1],
            'mimeType': mimetype,
            'parents': [parent_id]
        }
        media = MediaFileUpload(filename,
                                mimetype=mimetype)
        print('UPLOADING: {:<40}'.format(filename), end=' ... ')
        sys.stdout.flush()
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        print ('UPLOADED. File ID: {}'.format(
            file.get('id')
        )
               )

    def upload_files(self, parent_id):
        for d in self.filesfromdirs:
            sub_pid = self.create_dirs(d.parent.replace('./', '').split('/'),
                                       parent_id)
            for f in d.files:
                self.upload_file(f, sub_pid)

    def test(self):
        """Shows basic usage of the Google Drive API.
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

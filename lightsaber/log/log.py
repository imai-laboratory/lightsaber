from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import glob
from collections import namedtuple

# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = '~/.credentials/client_secret.json'
APPLICATION_NAME = 'pythonlog'

# DEPRECATED
MIMES = {
    '.jpg': 'image/jpeg',
    '.csv': 'text/plain',
    '.ss': 'application/vnd.google-apps.spreadsheet'
}

SSMIME = 'application/vnd.google-apps.spreadsheet'
ROW_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
               'H', 'I', 'J', 'K', 'L', 'M', 'N'
               ]


class CloudLog():
    def __init__(self,
                 directory,
                 log_name,
                 root_id='root',
                 credentials=None,
                 no_web_auth_flags=True,
                 ):
        self.directory = directory
        self.log_name = log_name
        self.no_web_auth_flags = no_web_auth_flags
        self.root_id = root_id

        print('save to:{} (google drive)'.format(
            os.path.join(self.directory, self.log_name)
        )
              )

        if no_web_auth_flags:
            self.args = tools.argparser.parse_args()
            self.args.noauth_local_webserver = True

        self.credentials = (CLIENT_SECRET_FILE if not credentials else
                            credentials)

        # file_path = test_dir/test_log (spread sheet)
        self.file_path = os.path.join(self.directory, self.log_name)

        Filetup = namedtuple('Filetup', 'parent files')

        self.file_from_path = Filetup(
            os.path.dirname(self.file_path),
            glob.glob(self.file_path)
        )

        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=self.http)

        self.folders_list = self.directory.split('/')

        # get service for spread sheet
        self.ss_service = discovery.build(
            'sheets',
            'v4',
            http=self.http,
            discoveryServiceUrl=(
                'https://sheets.googleapis.com/$discovery/rest?'
                'version=v4'
            )
        )

        # create parent directory
        self.parent_id = self.create_folders(
            self.folders_list,
            self.root_id
        )

        # create spread sheet
        self.spread_sheet_id = self.create_spread_sheet(
            self.log_name,
            self.parent_id
        )

    def create_spread_sheet(self, filename, parent_id=None):
        '''
            Creates an empty spread sheet in google drive
        '''
        mimetype = SSMIME

        file_metadata = {
            'name': filename,
            'mimeType': mimetype,
            'parents': [parent_id]
        }

        request = self.service.files().create(body=file_metadata,
                                              fields='id').execute()

        print('CREATING: {:<10}'.format(filename), end=' ... ')
        sys.stdout.flush()

        file_id = request.get('id')
        print ('CERATED. Spread Sheet ID: {}'.format(
            file_id
        )
               )
        return file_id

    def get_credentials(self):
        '''
            get credentials from google platform
        '''
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir,
                                       '{}.json'.format(APPLICATION_NAME))
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            print('no credentials. looking for {}'.format(self.credentials))
            flow = client.flow_from_clientsecrets('client_secret.json',
                                                  SCOPES)
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

    def create_folders(self, path, parent_id):
        '''
            A recursive function to create directories
            path: a list which will be mutable
        '''
        if path:
            folder_name = path.pop(0)
            folder_exists = self.folder_exists(parent_id, folder_name)

            if folder_exists:
                new_parent_id = folder_exists
            else:
                print('folder: {} dose not exists'.format(folder_name))
                new_parent_id = self.create_folder(folder_name, parent_id)

            return self.create_folders(path, new_parent_id)
        else:
            return parent_id

    def folder_exists(self, parent_id, folder_name):
        '''
            Check if the folder exists in parent and
            if so return its id
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
        '''
            Creates new folder under designated parent folder
        '''
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

    def get_spread_sheet(self, spread_sheet_id):
        result = self.ss_service.spreadsheets().values().get(
            spreadsheetId=self.spread_sheet_id
        ).execute()

        values = result.get('values', [])
        if not values:
            print('No data found.')

        else:
            print('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s, %s' % (row[0], row[4]))

    def update_spread_sheet(self, contents):
        """
            update spread sheet
        """
        length = len(contents)
        values = [contents]
        range_name = 'A1:{}1'.format(ROW_LETTERS[length])
        body = {
            'values': values
        }

        result = self.ss_service.spreadsheets().values().append(
            spreadsheetId=self.spread_sheet_id, range=range_name,
            body=body, valueInputOption="USER_ENTERED"
        ).execute()
        return result


def test():
    cloud = CloudLog('testd1/testd2', 'log_name')
    cloud.update_spread_sheet(['hoge1', 'hoge2', 'hoge3', 'hoge4'])
    cloud.update_spread_sheet(['hoge11', 'hoge12', 'hoge13', 'hoge14'])
    cloud.update_spread_sheet(['hoge111', 'hoge112', 'hoge113', 'hoge114'])


if __name__ == '__main__':
    test()

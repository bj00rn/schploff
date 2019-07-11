import os
import requests
import sys
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive import settings
import logging

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


class GoogleStorage:
    def __init__(self, target_path, settings_file):
        self.path = target_path
        self.gauth = None
        self.config = settings.LoadSettingsFile(settings_file)

    def connect(self):
        try:
            self.gauth = GoogleAuth()
            # Try to load saved client credentials
            self.gauth.LoadCredentialsFile(
                self.config['save_credentials_file'])
            if self.gauth.credentials is None:
                if sys.stdout.isatty():
                    # Authenticate if they're not there and shell is interactive
                    self.gauth.CommandLineAuth()
                else:
                    raise ValueError(
                        'No credentials found, need to log in first. try running script from interactive shell'
                    )
            elif self.gauth.access_token_expired:
                # Refresh them if expired
                self.gauth.Refresh()
            else:
                # Initialize the saved creds
                self.gauth.Authorize()
            # Save the current credentials to a file
            self.gauth.SaveCredentialsFile(
                self.config['save_credentials_file'])
        except Exception as e:
            logger.error('failed to connect to google storage', exc_info=True)
            raise e


class PhotosStorage(GoogleStorage):
    def __init__(self, settings_file):
        super().__init__(target_path=None, settings_file=settings_file)

    def upload(self, file_path, file_name=None, description=None):
        base_name = os.path.basename(file_path)
        fn = file_name if file_name is not None else base_name
        try:
            headers = {
                'Content-Type': "application/octet-stream",
                'X-Goog-Upload-File-Name': fn,
                'X-Goog-Upload-Protocol': "raw",
                'Authorization':
                "Bearer " + self.gauth.credentials.access_token,
            }

            data = open(file_path, 'rb').read()
            response = requests.post(
                'https://photoslibrary.googleapis.com/v1/uploads',
                headers=headers,
                data=data)
            image_token = response.text
            logger.info('Uploaded [{checksum}] [{fn}]'.format(
                checksum=image_token, fn=fn))
        except Exception as e:
            logger.warning('failed to upload [{fn}] to google photos'.format(
                fn=file_path),
                           exc_info=True)


class DriveStorage(GoogleStorage):
    def __init__(self, target_path, settings_file):
        super().__init__(target_path=target_path, settings_file=settings_file)

    def upload(self, file_path, file_name=None, description=None):
        base_name = os.path.basename(file_path)
        fn = file_name if file_name is not None else base_name
        try:
            drive = GoogleDrive(self.gauth)

            file1 = drive.CreateFile({
                'parents': [{
                    'kind': 'drive#fileLink',
                    'id': self.path,
                }],
                'title':
                fn,
                'description':
                description,
            })
            # Set content of the file from given string.
            file1.SetContentFile(file_path)
            file1.Upload()
            logger.info('Uploaded [{checksum}] [{fn}]'.format(
                checksum=file1['md5Checksum'], fn=fn))
            return file1
        except Exception as e:
            logger(
                'failed to upload [{fn}] to google drive'.format(fn=file_path))
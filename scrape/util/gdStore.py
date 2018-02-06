import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive import settings
import logging

logger = logging.getLogger(__name__)


class GDStore:
    def __init__(self, path, settings_file, interactive=False):
        self.path = path
        self.gauth = None
        self.interactive = interactive
        self.config = settings.LoadSettingsFile(settings_file)

    def upload(self, file_path, description=None):
        try:
            base_name = os.path.basename(file_path)
            drive = GoogleDrive(self.gauth)
            file1 = drive.CreateFile({
                'parents': [{
                    'kind': 'drive#fileLink',
                    'id': self.path,
                }],
                'title':
                base_name,
                'description':
                description,
            })
            # Set content of the file from given string.
            file1.SetContentFile(file_path)
            file1.Upload()
            return file1
        except Exception as e:
            logger("failed to upload [{fn}] to google drive".format(fn=file_path))

    def connect(self):
        try:
            self.gauth = GoogleAuth()
            # Try to load saved client credentials
            self.gauth.LoadCredentialsFile(self.config['save_credentials_file'])
            if self.gauth.credentials is None:
                if self.interactive:
                    # Authenticate if they're not there
                    self.gauth.CommandLineAuth()
                else:
                    raise ValueError('No credentials found')
            elif self.gauth.access_token_expired:
                # Refresh them if expired
                self.gauth.Refresh()
            else:
                # Initialize the saved creds
                self.gauth.Authorize()
            # Save the current credentials to a file
            self.gauth.SaveCredentialsFile(self.config['save_credentials_file'])
        except Exception as e:
            logger.error("failed to connect to google drive")
            raise e

import json
import logging
import os
import sys

import requests
from pydrive import settings
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from loguru import logger

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

    def upload(self, file_path, **kwargs):
        try:
            fn = os.path.basename(file_path)
            description = kwargs.get('description', None)
            album_id = kwargs.get('album_id', None)

            headers = {
                'Content-Type': "application/octet-stream",
                'X-Goog-Upload-File-Name': fn,
                'X-Goog-Upload-Protocol': "raw",
                'Authorization':
                "Bearer " + self.gauth.credentials.access_token,
            }

            with open(file_path, 'rb') as file:
                data = file.read()
                response = requests.post(
                    'https://photoslibrary.googleapis.com/v1/uploads',
                    headers=headers,
                    data=data)
                upload_token = response.text

                if response.status_code != 200:
                    raise Exception(f'Failed to upload media: {response.text}')
                else:
                    logger.info(
                        'Uploaded to google photos [{checksum}] [{fn}]'.format(
                            checksum=upload_token, fn=fn))

                self._create_media_item(upload_token, description, album_id)
        except Exception as e:
            raise Exception("Failed to save to google photos") from e

    def _create_media_item(self, upload_token, description=None,
                           album_id=None):
        mediaItemRequestBody = {
            "newMediaItems": [{
                "simpleMediaItem": {
                    "uploadToken": upload_token,
                }
            }]
        }

        if (description):
            mediaItemRequestBody["newMediaItems"][0][
                'description'] = description

        if (album_id):
            mediaItemRequestBody['albumId'] = album_id
            mediaItemRequestBody["albumPosition"] = {
                "position": "FIRST_IN_ALBUM"
            }

        response = requests.post(
            'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
            headers={
                'Content-type': 'application/json',
                'Authorization':
                'Bearer ' + self.gauth.credentials.access_token,
            },
            data=json.dumps(mediaItemRequestBody))

        if response.status_code != 200 or response.json(
        )['newMediaItemResults'][0]['status']['message'].upper() not in [
                'SUCCESS', 'OK'
        ]:  # for some reason the api always seems to return 200, hence the need to check message
            raise Exception(f'Unexpected response: {response.json()}')

        logger.info('Created media item [{url}]'.format(
            url=json.loads(response.text)['newMediaItemResults'][0]
            ['mediaItem']['productUrl']))

    def list_albums(self):
        return requests.get('https://photoslibrary.googleapis.com/v1/albums',
                            headers={
                                'Content-type':
                                'application/json',
                                'Authorization':
                                'Bearer ' + self.gauth.credentials.access_token
                            }).json()


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
            logger.error(
                'failed to upload [{fn}] to google drive'.format(fn=file_path))

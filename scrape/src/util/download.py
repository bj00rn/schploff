import hashlib
import os
import time
from datetime import datetime

import piexif
import piexif.helper
from loguru import logger

from .fix_exif_date import fix_image_dates
from .image import remove_transparency
from .storage.google.googleStorage import DriveStorage, PhotosStorage
from .store import NoStore, SqliteStore

image_format = 'webp'


def process_files(db_file,
                  files,
                  archive_path,
                  quality,
                  upload_to_gdrive=False,
                  upload_to_photos=False,
                  photos_album=None):

    imageStorage = []
    if upload_to_gdrive:
        imageStorage.append(
            DriveStorage(target_path='0Byrk3xueZv-4cmtBb1cxdFY4WTg', settings_file='./google_api/settings.yaml'))
    if upload_to_photos:
        imageStorage.append(PhotosStorage(settings_file='./google_api/settings.yaml'))

    for storage in imageStorage:
        storage.connect()

    with SqliteStore(db_file) if db_file is not None else NoStore() as store:
        for (source_url, of_name, image_data) in files:
            try:
                hexh = hashlib.md5(image_data.tobytes()).hexdigest()

                # process the file if not already in db
                if not store.exists(hexh):
                    with remove_transparency(image_data) as processed_image:
                        image_date = datetime.now()
                        image_fn = "{fn}_{date}.{ext}".format(
                            fn=of_name,
                            date='{:%F_%H-%M-%S}'.format(image_date),
                            ext=image_format,
                        )

                        exif_ifd = {
                            piexif.ExifIFD.DateTimeOriginal: image_date.strftime('%Y:%m:%d %H:%M:%S'),
                            piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(image_fn, encoding="ascii"),
                        }

                        exif_dict = {'Exif': exif_ifd}

                        archive_file = save_image(
                            processed_image,
                            archive_path,
                            image_fn,
                            quality,
                            piexif.dump(exif_dict),
                        )

                        fix_image_dates(archive_file, image_date)

                        for storage in imageStorage:
                            storage.upload(archive_file, title=image_fn, album_id=photos_album, description=image_fn)

                        store.add(hash=hexh,
                                  timestamp=time.mktime(image_date.timetuple()),
                                  filename=archive_file,
                                  file_class='n/a')

                else:
                    logger.info('skipping [{hash}[ [{filename}] already in db'.format(hash=hexh, filename=of_name))

            except Exception as e:
                logger.exception('failed to process [{hexh}] [{fn}]'.format(hexh=hexh, fn=of_name))


def save_image(image, archive_path, file_name, quality=80, exif=None):
    fn = os.path.abspath(os.path.join(archive_path, file_name))
    image.save(
        fn,
        quality=quality,
    )
    piexif.insert(exif, fn)  # use piexif for now due to lack of web support in Pillow
    logger.info('Wrote [{fn}]'.format(fn=fn))
    return fn

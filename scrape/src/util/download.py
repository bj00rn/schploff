import os
from requests import get
import hashlib
from .fix_exif_date import fix_image_dates, set_exif_exiv2
from .store import SqliteStore, NoStore
from .storage.google.googleStorage import DriveStorage, PhotosStorage
from .image import replace_transparency
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

image_format = 'webp'


def process_files(db_file,
                  files,
                  archive_path,
                  quality,
                  upload_to_gdrive=False,
                  upload_to_photos=False):

    imageStorage = []
    if upload_to_gdrive:
        imageStorage.append(
            DriveStorage(target_path='0Byrk3xueZv-4cmtBb1cxdFY4WTg',
                         settings_file='./google_api/settings.yaml'))
    if upload_to_photos:
        imageStorage.append(
            PhotosStorage(settings_file='./google_api/settings.yaml'))

    for storage in imageStorage:
        storage.connect()

    with SqliteStore(db_file) if db_file is not None else NoStore() as store:
        for (source_url, of_name, image_data) in files:
            try:
                with replace_transparency(image_data) as im:
                    hexh = hashlib.md5(image_data.tobytes()).hexdigest()

                    # process the file if not already in db
                    if store.get(hexh) is None:
                        image_date = datetime.now()
                        processed_image = process_image(im)
                        image_fn = "{fn}_{date}.{ext}".format(
                            fn=of_name,
                            date='{:%F_%H-%M-%S}'.format(image_date),
                            ext=image_format,
                        )

                        archive_file = save_image(processed_image,
                                                  archive_path, image_fn,
                                                  quality)

                        set_exif_exiv2(archive_file,
                                       image_date,
                                       comment=image_fn)

                        fix_image_dates(archive_file, image_date)

                        for storage in imageStorage:
                            storage.upload(archive_file, image_fn, image_fn)

                        store.add(hash=hexh,
                                  timestamp=time.mktime(
                                      image_date.timetuple()),
                                  filename=archive_file,
                                  file_class='n/a')

                    else:
                        logger.info(
                            'skipping [{hash}[ [{filename}] already in db'.
                            format(hash=hexh, filename=of_name))

            except Exception as e:
                logger.exception('failed to process [{hexh}] [{fn}]'.format(
                    hexh=hexh, fn=of_name))


def save_image(image, archive_path, file_name, quality=80, exif=None):
    fn = os.path.join(archive_path, file_name)
    image.save(
        fn,
        quality=quality)  # don't use exif for now due to lack of web support

    logging.info('Wrote [{fn}]'.format(fn=fn))
    return fn


def process_image(image_data):
    return replace_transparency(image_data)

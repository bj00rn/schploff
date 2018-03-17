import os
from requests import get
import hashlib
from .fix_exif_date import fix_image_dates, set_exif_exiv2
from .store import SqliteStore, NoStore
from .gdStore import GDStore
from .image import replace_transparency
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

image_format = 'webp'


def process_files(db_file, files, archive_path, upload_to_gdrive=False):
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

                        archive_file = save_image(
                            processed_image,
                            archive_path,
                            image_fn,
                        )

                        set_exif_exiv2(
                            archive_file, image_date, comment=image_fn)

                        fix_image_dates(archive_file, image_date)

                        if upload_to_gdrive:
                            upload_to_drive(
                                source_file=archive_file,
                                target_path='0Byrk3xueZv-4cmtBb1cxdFY4WTg',
                                settings_file='./google_api/settings.yaml',
                                file_name=image_fn,
                                description=image_fn)

                        store.add(
                            hash=hexh,
                            timestamp=time.mktime(image_date.timetuple()),
                            filename=archive_file,
                            file_class='n/a')

                    else:
                        logger.info(
                            'skipping [{hash}[ [{filename}] already in db'.
                            format(hash=hexh, filename=of_name))

            except Exception as e:
                logger.exception('failed to process [{hexh}] [{fn}]'.format(
                    hexh=hexh, fn=of_name))


def upload_to_drive(source_file,
                    target_path,
                    settings_file,
                    file_name,
                    description=''):
    gd = GDStore(target_path, settings_file)
    gd.connect()
    return gd.upload(source_file, file_name, description)


def save_image(image, archive_path, file_name, exif=None):
    fn = os.path.join(archive_path, file_name)
    image.save(fn)  # don't use exif for now due to lack of web support

    logging.info('Wrote [{fn}]'.format(fn=fn))
    return fn


def process_image(image_data):
    return replace_transparency(image_data)

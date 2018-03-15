import os
from requests import get
import hashlib
from .fix_exif_date import fix_image_dates, generate_exif_data
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

                        archive_file = save_image(
                            processed_image,
                            archive_path,
                            "{fn}_{date}".format(
                                fn=of_name,
                                date='{:%F_%H-%M-%S}'.format(image_date),
                                ext=image_format,
                            ),
                            exif=generate_exif_data(
                                processed_image,
                                image_date,
                            ))

                        fix_image_dates(archive_file, image_date)

                        if upload_to_gdrive:
                            upload_to_drive(
                                archive_file, '0Byrk3xueZv-4cmtBb1cxdFY4WTg',
                                './google_api/settings.yaml',
                                '{fn}_{date}.{ext}'.format(
                                    fn=of_name,
                                    date='{:%F_%H-%M-%S}'.format(image_date),
                                    ext=image_format,
                                ))

                        store.add(
                            hash=hexh,
                            timestamp=time.mktime(image_date.timetuple()),
                            filename=os.path.basename(archive_file),
                            file_class='n/a')

                    else:
                        logger.info(
                            'skipping [{hash}[ [{filename}] already in db'.
                            format(hash=hexh, filename=of_name))

            except Exception as e:
                logger.exception('failed to process [{hexh}] [{fn}]'.format(
                    hexh=hexh, fn=of_name))


def upload_to_drive(source_file, target_path, settings_file, file_name=None):
    gd = GDStore(target_path, settings_file)
    gd.connect()
    return gd.upload(source_file, file_name, 'test')


def save_image(image, archive_path, file_name, ext='webp', exif=None):
    fn = os.path.join(archive_path, file_name)
    image.save('{fn}.{ext}'.format(fn=fn, ext=ext), exif=exif)
    logging.info('Wrote [{fn}.{ext}]'.format(fn=fn, ext=ext))
    return '{fn}.{ext}'.format(fn=fn, ext=ext)


def process_image(image_data):
    return replace_transparency(image_data)

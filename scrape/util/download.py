import os, io
from requests import get
from PIL import Image
import hashlib
from .fix_exif_date import fix_image_dates
from .store import Store
from .gdStore import GDStore
from .image import replace_transparency
import shutil
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

image_format = 'webp'

def process_files(db_file, files, archive_path, temp_path):
    with Store(db_file) as store:
        for (image_data, of_name, file_class, source_url) in files:
            try:
                with replace_transparency(Image.open(
                        io.BytesIO(image_data))) as im:
                    hexh = hashlib.md5(image_data).hexdigest()

                    # process the file if not already in db
                    if store.get(hexh) is None:
                        processed_image = process_file(im)
                        temp_file = save_image(processed_image, temp_path,
                                               hexh, image_format)

                        fix_image_dates(temp_file)

                        archive_file = archive_image(
                            archive_path=archive_path,
                            source_path=temp_file,
                            of_name="{fn}.{ext}".format(fn=of_name, ext=image_format),
                        )

                        upload_to_drive(archive_file, "0Byrk3xueZv-4cmtBb1cxdFY4WTg", './google_api/settings.yaml', '{fn}.{ext}'.format(fn=of_name, ext=image_format))

                        store.add(
                            hash=hexh,
                            timestamp=time.mktime(datetime.now().timetuple()),
                            filename=os.path.basename(archive_file),
                            file_class=file_class)

                        if os.path.isfile(temp_file):
                            os.remove(temp_file)

                    else:
                        logger.info(
                            "skipping [{hash}[ [{filename}] already in db".format(
                                hash=hexh, filename=of_name))

            except Exception as e:
                logger.exception("failed to process [{hexh}] [{fn}]".format(hexh=hexh, fn=of_name))


def upload_to_drive(source_file, target_path, settings_file, file_name=None):
        gd = GDStore(target_path, settings_file)
        gd.connect()
        gd_file = gd.upload(source_file, file_name, 'test')

def save_image(image, archive_path, file_name, ext='webp'):
    fn = os.path.join(archive_path, file_name)
    image.save("{fn}.{ext}".format(fn=fn, ext=ext), ext, quality=50)
    return "{fn}.{ext}".format(fn=fn, ext=ext)


def archive_image(source_path, of_name, archive_path):
    fn = os.path.join(archive_path, os.path.basename(of_name))
    shutil.copyfile(src=source_path, dst=fn, )
    return fn


def process_file(image_data):
    return replace_transparency(image_data)


def get_image(url):
    logger.info("getting url {url}".format(url=url))
    i = get(url).content
    return (
        url,
        i,
    )


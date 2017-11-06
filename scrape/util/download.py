import os
import urllib
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from StringIO import StringIO
import hashlib
import util.fix_exif_date
from util.store import Store
from util.gdStore import GDStore
import time
import shutil
from datetime import datetime


def process_files(db_file, files, archive_path):
    gd = GDStore("0Byrk3xueZv-4cmtBb1cxdFY4WTg", './google_api/settings.yaml')
    gd.connect()

    with Store(db_file) as store:
        for (source_url, fn, file_class,) in files:
            try:
                ext = os.path.splitext(fn)[1]

                with Image.open(fn) as im:
                    hexh = hashlib.md5(im.tobytes()).hexdigest()

                # process the file if not already in db
                if store.get(hexh) is None:

                    gd_file = None
                    try:
                        print('Uploading to GoogleDrive...')
                        gd_file = gd.upload(fn, '')
                        print 'Uploaded {checksum}'.format(checksum=gd_file['md5Checksum'])
                    except Exception as e:
                        print('Error uploading to GoogleDrive')

                    new_fn = os.path.join(archive_path, os.path.basename(fn))
                    if not os.path.isfile(new_fn):
                        shutil.move(fn, new_fn)
                    else:
                        print("file {0} exists, skipping".format(new_fn))

                    print('adding {hexh} {fn} to database'.format(
                        hexh=hexh, fn=fn))

                    store.add(hash=hexh, timestamp=time.mktime(
                        datetime.now().timetuple()), filename=os.path.basename(fn), file_class=file_class)

                else:
                    print('skipping {hexh} {fn}, already in database'.format(
                        hexh=hexh, fn=fn))
            except Exception, e:
                print(e)
            finally:
                # clean up
                if os.path.isfile(fn):
                    os.remove(fn)


def download_file(url, destination):
    """
    This will download whatever is on the internet at 'url' and save it to 'destination'.

    Parameters
    ----------
    url : str
        The URL to download from.
    destination : str
        The filesystem path (including file name) to download the file to.

    Returns
    -------
    Tuple/None
        (Source url, The path of the file that was downloaded) or None if download failed
    """
    destination = os.path.realpath(destination)
    print ('Downloading data from {0} to {1}'.format(url, destination))
    try:
        page = urllib.urlopen(url)
        if page.getcode() is not 200:
            print('Tried to download data from %s and got http response code %s', url, str(
                page.getcode()))
            return None
        urllib.urlretrieve(url, destination)
        return (url, destination)
    except Exception, e:
        print('Error downloading data from {0} to {1}'.format(
            url, destination))
        print str(e)
        return None

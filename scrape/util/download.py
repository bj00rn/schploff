import os
import urllib2
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from StringIO import StringIO
import hashlib
import util.fix_exif_date
from util.store import Store
from util.gdStore import GDStore
from util.image replace_transparency
from util.fix_exif_date import fix_image_dates

import time
import shutil
from datetime import datetime


def process_files(db_file, files, archive_path, temp_path):
    with Store(db_file) as store:
        for (image_data, of_name, file_class, source_url) in files:
            try:
                with Image.open(StringIO(image_data)) as im:
                    im.verify()
                    hexh = hashlib.md5(im.tobytes()).hexdigest()                    
 
                    # process the file if not already in db
                    if store.get(hexh) is None:
                        
                        new_fn = process_file(os.path., im)

                        upload_to_drive(new_fn, "0Byrk3xueZv-4cmtBb1cxdFY4WTg", './google_api/settings.yaml')

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

def upload_to_drive(source_file, target_path, settings_file):
    try:
        print('Uploading to GoogleDrive...')
        gd = GDStore(target_path, settings_file)
        gd.connect()
        gd_file = gd.upload(outfilename, '')
        print 'Uploaded {checksum}'.format(checksum=gd_file['md5Checksum'])
    except Exception as e:
        print('Error uploading to GoogleDrive')
    
def process_file(image_data)
    image.replace_transparency(image_data)

def get_image(url)
      img = urllib2.urlopen(url).read()
      return (url, img)


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

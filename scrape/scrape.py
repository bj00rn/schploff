#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
from datetime import datetime
import urllib, json
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from StringIO import StringIO
import requests
import os
import hashlib
import util.fix_exif_date
from util.store import Store
import time
import sys
 
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
            print('Tried to download data from %s and got http response code %s', url, str(page.getcode()))
            return None
        urllib.urlretrieve(url, destination)
        return (url, destination)
    except Exception,e:
        print('Error downloading data from {0} to {1}'.format(url, destination))
        print str(e)
        return None


def prepare_dowload():

   files_to_download = []
   date="{:%F_%H-%M-%S}".format(datetime.now())

   #fi northern balic bouy
   fi_bouy_base_url = "http://cdn.fmi.fi/legacy-fmi-fi-content/products/wave-height-graphs/wave-plot.php?station=1&lang=sv"
   fi_bouy_of = "fi_bouy_northern_baltic_{date}.png"
  
   files_to_download.append((fi_bouy_base_url, fi_bouy_of.format(date=date)))

 
   #fi significant wave height forecast
   fi_forecast_base_url = "http://cdn.fmi.fi/marine-forecasts/products/wave-forecast-maps/wave03.gif"
   fi_forecast_of = "fi_forecast_significant_wave_height_{date}.gif"
   
   files_to_download.append((fi_forecast_base_url, fi_forecast_of.format(date=date)))
   
   #dmi swell
   dmi_forecast_base_url="http://ocean.dmi.dk/anim/plots/{idx}.ba.1.png"
   dmi_forecast_of = "dmi_forecast_{desc}_{date}.png"
   
   dmi_image_range = [
      ("tp", "dominant_wave_period"),
      ("hs", "significant_wave_height"),
      ("hsw", "swell_height"),
      ("tsw", "period_of_total_swell"),
      ("win", "wind"),
   ]
                 
   for (idx, desc) in dmi_image_range:
     files_to_download.append((dmi_forecast_base_url.format(idx=idx), dmi_forecast_of.format(desc=desc, date=date)))
   
   #smhi 
   smhi_bouy_base_url = "https://www.smhi.se/hfa_coord/BOOS/Waves/Stationplot/Last_24h/{idx}.png"
   smhi_bouy_of = "smhi_observation_bouy_{desc}_{date}.png"
   smhi_bouy_image_range = [
      ("HuvudskarOst_SMHI", "huvudskar_ost"),
      ("Knollsgrund_SMHI", "knolls_grund"),
      ("FinngrundetWR_SMHI","finngrundet_wr")
   ]
      
   for (idx, desc) in smhi_bouy_image_range:
      files_to_download.append((smhi_bouy_base_url.format(idx=idx), smhi_bouy_of.format(desc=desc, date=date)))
   
   return files_to_download
   
def process_files(db_file, files, archive_path):
   with Store(db_file) as store:
      for (source_url, fn) in files:
         try:
            ext = os.path.splitext(fn)[1]
            
            with Image.open(fn) as im:
               hexh = hashlib.md5(im.tobytes()).hexdigest()
      
            # process the file if not already in db
            if store.get(hexh) is None:
               print('adding {hexh} {fn} to database'.format(hexh=hexh, fn=fn))           
               store.add(hash=hexh, timestamp=time.mktime(datetime.now().timetuple()), filename=fn)
        
               new_fn = os.path.join(archive_path, os.path.basename(fn))
               if not os.path.isfile(new_fn):
                  os.rename(fn, new_fn)
               else:
                  print("file {0} exists, skipping".format(new_fn))
            else:
               print('skipping {hexh} {fn}, already in database'.format(hexh=hexh, fn=fn))
         except Exception, e:
            print(e)
         finally:  
            #clean up
            if os.path.isfile(fn):
               os.remove(fn)

def main(argv):
   dir = os.path.dirname(__file__)
   base_dir = argv[0]
   archive_dir = os.path.join(base_dir,  "archive")
   temp_dir = os.path.join(dir,  "temp")
   db_file = os.path.join(dir, 'scrape.sqlite3')
   downloads = []
   
   for(url, of) in prepare_dowload():
      result = download_file(url, os.path.join(temp_dir, of))
      if result is not None:
         downloads.append(result)
   
   process_files(db_file, downloads, archive_dir)
   
if __name__ == "__main__": main(sys.argv[1:])


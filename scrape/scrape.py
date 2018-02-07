#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from datetime import datetime
from util.download import process_files, get_image
import logging
import logging.config



def prepare_download():

    files_to_download = []  # (baseurl, outfile, class)
    date = "{:%F_%H-%M-%S}".format(datetime.now())

    # fi northern balic bouy
    fi_bouy_base_url = "http://cdn.fmi.fi/legacy-fmi-fi-content/products/wave-height-graphs/wave-plot.php?station=1&lang=sv"
    fi_bouy_of = "fi_bouy_northern_baltic_{date}"

    files_to_download.append((fi_bouy_base_url, fi_bouy_of.format(date=date),
                              "fi_bouy_northern_baltic"))

    # fi significant wave height forecast
    fi_forecast_base_url = "http://cdn.fmi.fi/marine-forecasts/products/wave-forecast-maps/wave03.gif"
    fi_forecast_of = "fi_forecast_significant_wave_height_{date}"

    files_to_download.append(
        (fi_forecast_base_url, fi_forecast_of.format(date=date),
         "fi_forecast_significant_wave_height"))

    # dmi swell
    dmi_forecast_base_url = "http://ocean.dmi.dk/anim/plots/{idx}.ba.1.png"
    dmi_forecast_of = "dmi_forecast_{desc}_{date}"

    dmi_image_range = [
        ("tp", "dominant_wave_period"),
        ("hs", "significant_wave_height"),
        ("hsw", "swell_height"),
        ("tsw", "period_of_total_swell"),
        ("win", "wind"),
    ]

    for (idx, desc) in dmi_image_range:
        files_to_download.append((dmi_forecast_base_url.format(idx=idx),
                                  dmi_forecast_of.format(desc=desc, date=date),
                                  "dmi_forecast_{desc}".format(desc=desc)))

    # smhi
    smhi_bouy_base_url = "https://www.smhi.se/hfa_coord/BOOS/Waves/Stationplot/Last_24h/{idx}.png"
    smhi_bouy_of = "smhi_observation_bouy_{desc}_{date}"
    smhi_bouy_image_range = [("HuvudskarOst_SMHI", "huvudskar_ost"),
                             ("Knollsgrund_SMHI", "knolls_grund"),
                             ("FinngrundetWR_SMHI", "finngrundet_wr")]

    for (idx, desc) in smhi_bouy_image_range:
        files_to_download.append(
            (smhi_bouy_base_url.format(idx=idx), smhi_bouy_of.format(
                desc=desc, date=date),
             "smhi_observation_bouy_{desc}".format(desc=desc)))

    return files_to_download

def main(argv):
    logger = logging.getLogger(__name__)
    logger.debug('hej')
    dir = os.path.dirname(__file__)
    os.chdir(dir)
    base_dir = argv[0]
    archive_dir = os.path.join(base_dir, "archive")
    temp_dir = os.path.join(dir, "temp")
    db_file = os.path.join(dir, 'scrape.sqlite3')
    downloads = []

    for (url, of, file_class) in prepare_download():
        #        result = download_file(url, os.path.join(temp_dir, of))
        u, i = get_image(url)
        if i is not None:
            downloads.append((i,) + (
                of,
                file_class,
                url,
            ))

    process_files(db_file, downloads, archive_dir, temp_dir)


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})


if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from util.download import process_files
import logging
import logging.config
from util.image_source import FIBouySource, DMISource, SMHIBouySource, FIForecastSource
import argparse


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("archive_path")
    parser.add_argument("database")
    parser.add_argument("upload_to_gdrive")
    parser.add_argument("check_fi")

    aargs = parser.parse_args()
    logger = logging.getLogger(__name__)

    if not os.path.isdir(os.path.realpath(aargs.archive_path)):
        logger.error(
            'Invalid argument. Archive path [{p}] does not exist'.format(
                p=aargs.archive_path))
        sys.exit(1)

    if not os.path.isfile(os.path.realpath(aargs.database)):
        logger.error("Invalid argument. Database [{}] does not exist".format(aargs.database))
        sys.exit(1)

    logger.debug('program started')

    archive_dir = os.path.join(aargs.archive_path)

    db_file = os.path.join(dir, 'scrape.sqlite3')

    files = DMISource().get_files() + SMHIBouySource().get_files(
    ) + FIForecastSource().get_files()

    if aargs.check_fi == 'True':
        files += FIBouySource().get_files()

    process_files(aargs.database, files, archive_dir,
                  aargs.upload_to_gdrive == 'True')


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

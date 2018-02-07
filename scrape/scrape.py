#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from util.download import process_files
import logging
import logging.config
from util.image_source import FIBouySource, DMISource, SMHIBouySource, FIForecastSource


def main(argv):
    logger = logging.getLogger(__name__)
    logger.debug('program started')
    dir = os.path.dirname(__file__)
    os.chdir(dir)
    base_dir = argv[0]
    archive_dir = os.path.join(base_dir, "archive")

    db_file = os.path.join(dir, 'scrape.sqlite3')

    files = DMISource().get_files() + SMHIBouySource().get_files(
    ) + FIBouySource().get_files() + FIForecastSource().get_files()

    process_files(db_file, files, archive_dir)


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

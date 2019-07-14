#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import os
import sys
from datetime import datetime

from loguru import logger
from util.download import process_files
from util.image_source import (DMISourceBaltic, DMISourceNorthsea, FIBouySource, FIForecastSource, SMHIBouySource)


def dir(path, permission=os.R_OK):
    real_path = path

    if not os.path.isdir(real_path):
        raise argparse.ArgumentTypeError('{0} is not a valid path'.format(real_path))
    if os.access(real_path, permission):
        return real_path
    else:
        raise argparse.ArgumentTypeError('{0} insufficient permissions'.format(real_path))


def writable_dir(path):
    return dir(path=path, permission=os.W_OK)


def readable_dir(path):
    return dir(path=path)


def database(db_file_path):
    if not os.path.isfile(db_file_path):
        raise argparse.ArgumentTypeError('database {0} does not exist'.format(db_file_path))
    return os.path.realpath(db_file_path)


def main(argv):
    local_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(local_dir)

    parser = argparse.ArgumentParser(prog='Scrape')
    parser.add_argument(
        'archivepath',
        metavar='archive path',
        type=writable_dir,
        help='archive path to copy images',
    )
    parser.add_argument('--database', dest='database', type=database, help='database to check downloaded files against')
    parser.add_argument('--upload-to-gdrive',
                        dest='upload_to_gdrive',
                        action='store_true',
                        help='upload files to google drive')
    parser.add_argument('--upload-to-photos',
                        dest='upload_to_photos',
                        action='store_true',
                        help='upload files to google photos')
    parser.add_argument(
        '--photos-album',
        dest='photos_album',
        type=str,
        help='id of google photos album to add images to. only appliccable when uploading to google photos')
    parser.add_argument('--quality',
                        dest='quality',
                        type=int,
                        metavar='Q',
                        default=80,
                        help='image quality, integer 10-100 (default 80)')
    parser.add_argument('--check-fi',
                        dest='check_fi',
                        action='store_true',
                        help='get finnish wave bouy observations (generates a new image on every run)')
    parser.add_argument('--verbose', '-v', action='store_true', dest='verbose', help='verbose logging')

    aargs = parser.parse_args()

    logger.info('Program started {0}'.format('{:%F_%H-%M-%S}'.format(datetime.now())))

    files = DMISourceBaltic().get_images() + DMISourceNorthsea().get_images() + SMHIBouySource().get_images(
    ) + FIForecastSource().get_images()

    if aargs.check_fi:
        files += FIBouySource().get_images()

    process_files(aargs.database, files, aargs.archivepath, aargs.quality, aargs.upload_to_gdrive,
                  aargs.upload_to_photos, aargs.photos_album)


if __name__ == '__main__':
    main(sys.argv[1:])

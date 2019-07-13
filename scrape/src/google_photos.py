#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import json
import os
import sys
from datetime import datetime
from util.storage.google.googleStorage import PhotosStorage


def entity(entity):
    options = ['album']
    if entity.lower() in options:
        return 'ALBUM'
    raise argparse.ArgumentTypeError('Options are: ALBUM')


def action(action):
    options = ['ls', 'list']
    if action.lower() in options:
        return 'LIST'


def main(argv):
    parser = argparse.ArgumentParser(prog='google_photos')

    parser.add_argument('entity', type=entity, help='entity type')

    parser.add_argument('action', type=action, help='action type')

    aargs = parser.parse_args()

    storage = PhotosStorage(settings_file='./google_api/settings.yaml')
    storage.connect()

    if aargs.entity == 'ALBUM':
        if aargs.action == 'LIST':
            print(json.dumps(storage.list_albums(), indent=4))


if __name__ == '__main__':
    main(sys.argv[1:])
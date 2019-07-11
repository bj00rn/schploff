#!/usr/bin/env python

import os
import time
import pyexiv2

import subprocess

from PIL import Image
import logging
from loguru import logger


def set_exif_tag(tag_name, tag_value, file_name):
    try:
        subprocess.call([
            "exiv2", "-M", 'set {t} {v}'.format(t=tag_name, v=tag_value),
            file_name
        ])
    except Exception as e:
        logger.exception(
            "Failed to set exif tag {t}={v} in file {f} using shell, is exiv2 installed?"
            .format(t=tag_name, v=tag_value, f=file_name))


def set_exif_exiv2(filename, createDate, comment):
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    exif_dict = [
        (
            'Exif.Image.DateTime',
            createDate,
        ),
        (
            'Exif.Photo.DateTimeOriginal',
            createDate,
        ),
        (
            'Exif.Image.DateTimeOriginal',
            createDate,
        ),
        (
            'Exif.Photo.DateTimeDigitized',
            createDate,
        ),
        (
            'Exif.Photo.UserComment',
            comment,
        ),
    ]
    for (key, value) in exif_dict:
        metadata[key] = pyexiv2.ExifTag(key, value)
    metadata.write(preserve_timestamps=True)


def fix_image_dates(img_path, date_to_set):
    t = date_to_set.timestamp()
    os.utime(img_path, (t, t))

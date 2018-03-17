#!/usr/bin/env python
#
# gexiv2 image Exif date fixer.
# Corey Goldberg, 2014
"""Recursively scan a directory tree, fixing dates
on all jpg/png image files.

Each file's Exif metadata and atime/mtime are all
set to the file's ctime.

Modifications are done in-place.

Requires: gexiv2
"""

import os
import time
import piexif

import subprocess

from PIL import Image
import logging
logger = logging.getLogger(__name__)


def set_exif_tag(tag_name, tag_value, file_name):
    try:
        subprocess.call([
            "exiv2", "-M", 'set {t} {v}'.format(t=tag_name, v=tag_value),
            file_name
        ])
    except Exception as e:
        logger.exception(
            "Failed to set exif tag {t}={v} in file {f} using shell, is exiv2 installed?".
            format(t=tag_name, v=tag_value, f=file_name))


def set_exif_shell(filename, createDate, comment):
    date_str = u'{:%Y:%m:%d %H:%M:%S}'.format(createDate)
    set_exif_tag('Exif.Image.DateTimeOriginal', date_str, filename)
    set_exif_tag('Exif.Photo.DateTimeOriginal', date_str, filename)
    set_exif_tag('Exif.Image.DateTime', date_str, filename)
    set_exif_tag('Exif.Photo.DateTimeDigitized', date_str, filename)


def generate_exif_data(image, createDate, comment=''):
    date_str = u'{:%Y:%m:%d %H:%M:%S}'.format(createDate)
    _comment = u'{0}'.format(comment)
    w, h = image.size

    user_comment_encoding = b'\x55\x4E\x49\x43\x4F\x44\x45\x00'
    user_comment = bytes(_comment, 'utf-8')

    c = user_comment_encoding.join(user_comment)

    exif_dict = {
        "0th": {
            piexif.ImageIFD.XResolution: (w, 1),
            piexif.ImageIFD.YResolution: (h, 1),
            piexif.ImageIFD.DateTime: date_str,
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: date_str,
            piexif.ExifIFD.DateTimeDigitized: date_str,
            piexif.ExifIFD.UserComment: c,
        },
    }
    return piexif.dump(exif_dict)


def fix_image_dates(img_path, date_to_set):
    t = date_to_set.timestamp()
    os.utime(img_path, (t, t))


# if __name__ == '__main__':
#    dir = '.'
#    for root, dirs, file_names in os.walk(dir):
#        for file_name in file_names:
#            if file_name.lower().endswith(('jpg', 'png')):
#                img_path = os.path.join(root, file_name)
#                fix_image_dates(img_path)

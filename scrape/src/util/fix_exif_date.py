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

from PIL import Image


def generate_exif_data(image, createDate):
    date_str = u'{:%Y:%m:%d %H:%M:%S}'.format(createDate)
    w, h = image.size

    exif_dict = {
        "0th": {
            piexif.ImageIFD.XResolution: (w, 1),
            piexif.ImageIFD.YResolution: (h, 1),
            piexif.ImageIFD.DateTime: date_str,
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: date_str,
            piexif.ExifIFD.DateTimeDigitized: date_str,
        },
    }
    return piexif.dump(exif_dict)


def fix_image_dates(img_path):
    t = os.path.getctime(img_path)
    os.utime(img_path, (t, t))


# if __name__ == '__main__':
#    dir = '.'
#    for root, dirs, file_names in os.walk(dir):
#        for file_name in file_names:
#            if file_name.lower().endswith(('jpg', 'png')):
#                img_path = os.path.join(root, file_name)
#                fix_image_dates(img_path)

#!/usr/bin/env python

import os




def fix_image_dates(img_path, date_to_set):
    t = date_to_set.timestamp()
    os.utime(img_path, (t, t))

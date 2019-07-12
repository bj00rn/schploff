#!/usr/bin/env python

import logging
import os
import subprocess
import time

from PIL import Image

from loguru import logger


def fix_image_dates(img_path, date_to_set):
    t = date_to_set.timestamp()
    os.utime(img_path, (t, t))

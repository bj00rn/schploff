#!/usr/bin/env python

import os
import time
import subprocess

from PIL import Image
import logging
from loguru import logger


def fix_image_dates(img_path, date_to_set):
    t = date_to_set.timestamp()
    os.utime(img_path, (t, t))

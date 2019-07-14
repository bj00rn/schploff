import unittest

from .image_source import (DMISource, FIBouySource, FIForecastSource, SMHIBouySource)


class TestImageClass(unittest.TestCase):
    def TestDownload(self):

        for url, of, image in DMISource().get_images() + SMHIBouySource().get_images() + FIBouySource().get_images(
        ) + FIForecastSource().get_images():
            print(of)

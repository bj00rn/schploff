import unittest
from .image_source import DMISource, SMHIBouySource, FIBouySource, FIForecastSource


class TestImageClass(unittest.TestCase):
    def TestDownload(self):

        for url, of, image in DMISource().get_files() + SMHIBouySource(
        ).get_files() + FIBouySource().get_files() + FIForecastSource(
        ).get_files():
            print(of)

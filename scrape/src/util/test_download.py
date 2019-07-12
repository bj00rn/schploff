import unittest
from io import BytesIO

from PIL import Image

from scrape.util.download import get_image


class TestDownload(unittest.TestCase):
    def test_get_image(self):
        url = 'https://www.python.org/static/img/python-logo@2x.png'
        u, i = get_image(url)
        self.assertEqual(url, u)
        im = Image.open(BytesIO(i))
        self.assertTrue(im.verify() is None)

    def test_process_files(self):
        (db_file, files, archive_path, temp_path)

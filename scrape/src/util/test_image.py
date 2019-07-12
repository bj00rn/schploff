import unittest
from io import BytesIO

from PIL import Image

from util.download import get_image


class TestImage(unittest.TestCase):
    def test_replace_transparency(self):
        url = 'https://www.python.org/static/img/python-logo@2x.png'
        url = 'http://cdn.fmi.fi/legacy-fmi-fi-content/products/wave-height-graphs/wave-plot.php?station=1&lang=sv'

        u, i = get_image(url)
        im = Image.open(BytesIO(i))
        im2 = repmove_transparency(im)
        self.assertTrue(im2.verify() is None)

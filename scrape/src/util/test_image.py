from util.image import replace_transparency
from util.download import get_image
from io import BytesIO
from PIL import Image
import unittest


class TestImage(unittest.TestCase):
    def test_replace_transparency(self):
        url = 'https://www.python.org/static/img/python-logo@2x.png'
        url = "http://cdn.fmi.fi/legacy-fmi-fi-content/products/wave-height-graphs/wave-plot.php?station=1&lang=sv"

        u, i = get_image(url)
        im = Image.open(BytesIO(i))
        im2 = replace_transparency(im)
        self.assertTrue(im2.verify() is None)

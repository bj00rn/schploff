from io import BytesIO

from PIL import Image
from requests import get

from loguru import logger


class ImageSource(object):
    base_url = None
    base_fn = None

    def get_urls(self):
        return [(self.base_url, self.base_fn)]

    def get_images(self):
        files = []
        for url, of in self.get_urls():
            try:
                logger.info('Getting [{url}]'.format(url=url))
                files.append((url, of, Image.open(BytesIO(get(url).content))))
                logger.info('Got [{url}]'.format(url=url))
            except Exception:
                logger.exception('Failed to get [{url}]'.format(url=url))
        return files

    def __init__(self):
        pass


class MultiSource(ImageSource):
    base_url = None
    base_fn = None
    expr_list = []

    def get_urls(self):
        sources = []
        for idx, desc, in self.expr_list:
            sources.append((self.base_url.format(idx=idx), self.base_fn.format(desc)))
        return sources

    def __init__(self):
        super(MultiSource, self).__init__()


class DMISourceBaltic(MultiSource):
    base_url = 'http://ocean.dmi.dk/anim/plots/{idx}.ba.1.png'
    base_fn = 'dmi_forecast_{}'
    expr_list = [
        ('tp', 'dominant_wave_period'),
        ('hs', 'significant_wave_height'),
        ('hsw', 'swell_height'),
        ('tsw', 'period_of_total_swell'),
        ('win', 'wind'),
    ]

    def __init__(self):
        super(DMISourceBaltic, self).__init__()


class DMISourceNorthsea(MultiSource):
    base_url = 'http://ocean.dmi.dk/anim/plots/{idx}.nsb.1.png'
    base_fn = 'dmi_forecast_north_sea_{}'
    expr_list = [
        ('tp', 'dominant_wave_period'),
        ('hs', 'significant_wave_height'),
        ('hsw', 'swell_height'),
        ('tsw', 'period_of_total_swell'),
        ('win', 'wind'),
    ]

    def __init__(self):
        super(DMISourceNorthsea, self).__init__()


class SMHIBouySource(MultiSource):
    base_url = 'https://www.smhi.se/hfa_coord/BOOS/Waves/Stationplot/Last_24h/{idx}.png'
    base_fn = 'smhi_observation_bouy_{}'
    expr_list = [
        ('HuvudskarOst_SMHI', 'huvudskar_ost'),
        ('Knollsgrund_SMHI', 'knolls_grund'),
        ('FinngrundetWR_SMHI', 'finngrundet_wr'),
    ]

    def __init__(self):
        super(SMHIBouySource, self).__init__()


class FIBouySource(ImageSource):
    base_url = 'http://cdn.fmi.fi/legacy-fmi-fi-content/products/wave-height-graphs/wave-plot.php?station=1&lang=sv'
    base_fn = 'fi_bouy_northern_baltic'

    def __init__(self):
        super(FIBouySource, self).__init__()


class FIForecastSource(ImageSource):
    base_url = 'http://cdn.fmi.fi/marine-forecasts/products/wave-forecast-maps/wave03.gif'
    base_fn = 'fi_forecast_significant_wave_height'

    def __init__(self):
        super(FIForecastSource, self).__init__()

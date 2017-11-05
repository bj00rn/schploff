#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import sys
from datetime import datetime
import urllib
import json
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from StringIO import StringIO
import requests
import os


def set_photo(url, filename, paramList, outDir):

    try:
        image_request_result = requests.get(url)
        oldImage = Image.open(StringIO(image_request_result.content))
    except:
        oldImage = Image.new(
            3, (1280, 960), new_background=(255, 255, 255, 255))

    old_width, old_height = oldImage.size

    mode = oldImage.mode
    if len(mode) == 1:  # L, 1
        new_background = (0)
    if len(mode) == 3:  # RGB
        new_background = (0, 0, 0)
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (0, 0, 0, 0)

    newImage = Image.new(mode, (old_width, old_height + 200), new_background)
    newImage.paste(oldImage, (0, 0, old_width, old_height))
    draw = ImageDraw.Draw(newImage)
    fontsize = 12
    fontpadding = 2
    fontcolor = (255, 255, 255)
    width, height = newImage.size
    x1 = 0
    y1 = height - (fontsize + fontpadding) * len(paramList)
    x2 = width
    y2 = height

    print(x1, y1, x2, y2)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/msttcorefonts/arial.ttf", fontsize)
    draw.rectangle(((0, height - (fontsize + fontpadding) *
                     len(paramList)), (width, height)), fill="black")
    idx = 0

    for item in paramList:
        idx = idx + 1
        draw.text((0, height - idx * (fontsize + fontpadding)),
                  "{value} {unit} ({station} {updated} {parameter})".format(
            value=item["value"],
            station=item['station'],
            unit=item['unit'],
            updated="{:%F %H:%M:%S}".format(
                datetime.fromtimestamp(item['updated'] / 1000)),
            parameter=item['parameter']
        ),
            fontcolor,
            font=font
        )
    newImage.save(os.path.join(outDir, filename), 'JPEG')


def fetchParameter(source, station, parameter, period):
    url = "https://opendata-download-{source}.smhi.se/api/version/latest/parameter/{parameter}/station/{station}/period/{period}/data.json".format(
        station=station, parameter=parameter, source=source, period=period)
    try:
        print("fetching {url} ... ".format(url=url))
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        # print(data)
        return {
            'value': data["value"][-1]["value"],
            'updated': data['updated'],
            'parameter': (data["parameter"]["name"]).encode('ascii', 'ignore').decode('ascii'),
            'unit': (data["parameter"]["unit"]).encode('ascii', 'ignore').decode('ascii'),
            'station': (data['station']['name']).encode('ascii', 'ignore').decode('ascii')}
    except:
        return {
            'value': 'Nan',
            'updated': 1,
            'parameter': 'NaN',
            'unit': 'NaN',
            'station': 'NaN'
        }


def main(argv):
    date = datetime.now()
    datestring = ("{:%F_%H-%M-%S}".format(date))
    out_dir = argv[0]

    paramList = [
        fetchParameter(station=87440, parameter=3,
                       source='metobs', period='latest-hour'),
        fetchParameter(station=87440, parameter=4,
                       source='metobs', period='latest-hour'),
        fetchParameter(station=33008, parameter=1, source='ocobs',
                       period='latest-day'),  # Vaghöjd, signifikant 30 mi
        fetchParameter(station=33008, parameter=9, source='ocobs',
                       period='latest-day'),  # Vagperiod timvärde
        # Vagriktning vid Tp (energimax 30 min)
        fetchParameter(station=33008, parameter=8,
                       source='ocobs', period='latest-day'),
        fetchParameter(station=33002, parameter=1, source='ocobs',
                       period='latest-day'),  # Vaghöjd, signifikant 30 mi
        fetchParameter(station=33002, parameter=9, source='ocobs',
                       period='latest-day'),  # Vagperiod timvärde
        fetchParameter(station=33002, parameter=7, source='ocobs',
                       period='latest-day'),  # Vagriktning timvärde
    ]

    #set_photo(url="http://83.140.123.183/ImageHarvester/Images/3009-landsort_1_live.jpg", filename="landsort_{0}.jpg".format(datestring), paramList=paramList)
    set_photo(url="http://83.140.123.183/ImageHarvester/Images/3009-landsort_1_1280.jpg",
              filename="landsort_{0}.jpg".format(datestring), paramList=paramList, outDir=out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])

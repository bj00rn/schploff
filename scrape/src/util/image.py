#!/usr/bin/python

import sys
import getopt
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def remove_transparency(source_image, bg_colour=(255, 255, 255)):
    try:
        processed_image = Image.new('RGB', source_image.size,
                                    bg_colour + (255, ))
        # Only process if image has transparency (http://stackoverflow.com/a/1963146)
        if source_image.mode in ('RGBA', 'LA',
                                 'P') or (source_image.mode == 'P' and
                                          'transparency' in source_image.info):

            # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
            alpha = source_image.convert('RGBA').split()[-1]

            # Create a new background image of our matt color.
            # Must be RGBA because paste requires both images have the same format
            # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)

            processed_image.paste(source_image, mask=alpha)
        else:
            processed_image.paste(source_image)
        return processed_image
    except Exception as e:
        logger.warning('failed to remove transparency', exc_info=True)

    return source_image


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['ifile=', 'ofile='])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-i', '-ifile'):
            print('inputfile is ', arg)
            inputfile = arg
        if opt in ('-o', '-ofile'):
            print('outputfile is ', arg)
            outputfile = arg

    try:
        im = Image.open(inputfile)
    except Exception as e:
        print('cant open {fn}'.format(fn=inputfile))

    try:
        remove_transparency(im, (255, 255, 255))
    except Exception as e:
        print('error processing {fn}'.format(fn=inputfile))

    try:
        im.save(outputfile)
    except Exception as e:
        print('error writing to {fn}'.format(fn=outputfile))


if __name__ == '__main__':
    main(sys.argv[1:])

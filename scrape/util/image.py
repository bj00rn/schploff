#!/usr/bin/python

import sys, getopt
from PIL import Image

def replace_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print ('test.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-i", "-ifile"):
         print('inputfile is ', arg)
         inputfile = arg
      if opt in ("-o", "-ofile"):
         print('outputfile is ', arg)
         outputfile = arg

   try:
      im = Image.open(inputfile)
   except Exception as e:
      print("can't open {fn}".format(fn=inputfile)) 

   try:  
      replace_transparency(im, (255,255,255))
   except Exception as e:
      print("error processing {fn}".format(fn=inputfile))
   
   try:
      im.save(outputfile)
   except Exception as e:
      print("error writing to {fn}".format(fn=outputfile))

if __name__ == "__main__":
   main(sys.argv[1:])

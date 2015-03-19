#!/usr/bin/env python

# Based on original picam by brianflakes, improved by pageauc, peewee2
# and Kesthal
# Modified to use multiple storage backend and provide a pure python interface

# PIL and python-picamera are required to run this script
# sudo apt-get update
# sudo apt-get install python-imaging-tk python-picamera

import io
# import subprocess
import os
# import time
import picamera
from datetime import datetime
from PIL import Image

# Motion detection settings:
# Threshold
#  - how much a pixel has to change by to be marked as "changed"
# Sensitivity
#  - how many changed pixels before capturing an image, needs to be higher if
#    noisy view
# ForceCapture
#  - whether to force an image to be captured every forceCaptureTime seconds,
#    values True or False
# filepath
#  - location of folder to save photos
# filenamePrefix
#  - string that prefixes the file name for easier identification of files.
# diskSpaceToReserve 
#  - Delete oldest images to avoid filling disk. How much byte to keep free
#    on disk.
# cameraSettings
#  - "" = no extra settings; "-hf" = Set horizontal flip of image; 
#  "-vf" = Set vertical flip; "-hf -vf" = both horizontal and vertical flip
threshold = 10
sensitivity = 20
forceCapture = True
forceCaptureTime = 60 * 60  # Once an hour
filepath = "/home/pi/picam"
filenamePrefix = "capture"
diskSpaceToReserve = 40 * 1024 * 1024  # Keep 40 mb free on disk
cameraSettings = ""

# settings of the photos to save
saveWidth = 1296
saveHeight = 972
saveQuality = 15  # Set jpeg quality (0 to 100)

# Test-Image settings
testWidth = 100
testHeight = 75

# this is the default setting, if the whole image should be scanned for
# changed pixel
testAreaCount = 1
testBorders = [[[1, testWidth], [1, testHeight]]]

# [ [[start pixel on left side,end pixel on right side],
#  [start pixel on top side,stop pixel on bottom side]] ]
#
# testBorders are NOT zero-based, the first pixel is 1 and the last pixel is
# testWith or testHeight

# with "testBorders", you can define areas, where the script should scan for 
# changed pixel
# for example, if your picture looks like this:
#
#     ....XXXX
#     ........
#     ........
#
# "." is a street or a house, "X" are trees which move arround like crazy when
# the wind is blowing
# because of the wind in the trees, there will be taken photos all the time.
# To prevent this, your setting might look like this:

# testAreaCount = 2
# testBorders = [ [[1,50],[1,75]], [[51,100],[26,75]] ] # area y=1 to 25 not
# scanned in x=51 to 100

# even more complex example
# testAreaCount = 4
# testBorders = [
#    [[1,39],[1,75]],
#    [[40,67],[43,75]],
#    [[68,85],[48,75]],
#    [[86,100],[41,75]]
#  ]

# in debug mode, a file debug.bmp is written to disk with marked changed
# pixel an with marked border of scan-area
# debug mode should only be turned on while testing the parameters above
debugMode = False  # False or True


# Capyture a small test image (for motion detection)
def captureTestImage(settings, width, height):
    imageData = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.resolution = (width, height)
        camera.capture(imageData, format='bmp')
    imageData.seek(0)
    im = Image.open(imageData)
    buffer = im.load()
    imageData.close()
    return im, buffer


def captureImage(settings, width, height, quality, diskSpaceToReserve):
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()
    filename = filenamePrefix + "-%04d%02d%02d-%0d2%02d%02d.jpg".format(
        time.year, time.month, time.day, time.hour, time.minute, time.second
    )
    outFile = os.path.join(filepath, filename)
    print outFile


def keepDiskSpaceFree(diskSpaceToReserve):
    return

image1, buffer1 = captureTestImage(cameraSettings, testWidth, testHeight)
debugimage = Image.new("RGB", (testWidth, testHeight))
debugim = debugimage.load()

for z in xrange(0, testAreaCount):
    for x in xrange(testBorders[z][1][0]-1, testBorders[z][0][1]):
        for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):
            debugim[x, y] = buffer1[x, y]

debugimage.save('debug.bmp')


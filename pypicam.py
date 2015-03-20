#!/usr/bin/env python

# Based on original picam by brianflakes, improved by pageauc, peewee2
# and Kesthal
# Modified to use multiple storage backend and provide a pure python interface
# by Dave Wilde <david.wilde@rackspace.com>

# PIL and python-picamera are required to run this script
# sudo apt-get update
# sudo apt-get install python-imaging-tk python-picamera

import io
import os
import picamera
import time
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
#  "" = no extra settings
#  "hflip" = Set horizontal flip of image
#  "vflip" = Set vertical flip of the image
threshold = 20
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
testWidth = 800
testHeight = 600

# this is the default setting, if the whole image should be scanned for
# changed pixel
testAreaCount = 2
testBorders = [[[1, 500], [1, 400]], [[1, 800], [401, 600]]]

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
debugMode = True  # False or True


# Capture a small test image (for motion detection)
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


# Capture the full image and save it to disk
def captureImage(settings, width, height, jpegQuality, diskSpaceToReserve):
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()
    filename = filenamePrefix + "-%04d%02d%02d-%0d2%02d%02d.jpg" % (
        time.year, time.month, time.day, time.hour, time.minute, time.second
    )
    outfile = os.path.join(filepath, filename)
    with picamera.PiCamera() as camera:
        if 'hflip' in settings:
            camera.hflip = True
        if 'vflip' in settings:
            camera.vflip = True
        camera.resolution = (width, height)
        camera.capture(outfile, quality=jpegQuality)
    print "Captured {}".format(outfile)


# Check on our free space
def keepDiskSpaceFree(diskSpaceToReserve):
    return


# Do the motion detection
def detectMotion(image1, buffer1, image2, buffer2, testAreaCount, testBorders):

    # If debugMode is true we create a debug bitmap
    if (debugMode):
        debugimage = Image.new("RGB", (testWidth, testHeight))
        debugim = debugimage.load()

    changedPixels = 0
    takePicture = False
    for z in xrange(0, testAreaCount):
        for x in xrange(testBorders[z][0][0]-1, testBorders[z][0][1]):
            for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):
                if (debugMode):
                    # Mark the borders of the test area blue
                    debugim[x, y] = buffer2[x, y]
                    if (
                            (x == testBorders[z][0][0]-1) or
                            (x == testBorders[z][0][1]-1) or
                            (y == testBorders[z][1][0]-1) or
                            (y == testBorders[z][1][1]-1)):
                        debugim[x, y] = (0, 0, 255)
                # Check the green channel for motion as it has the greatest
                # contrast
                pixdiff = abs(buffer1[x, y][1] - buffer2[x, y][1])
                if (pixdiff > threshold):
                    changedPixels += 1
                    if (debugMode):
                        # Make the changed pixels green
                        debugim[x, y] = (0, 255, 0)
                if (changedPixels > sensitivity):
                    takePicture = True
                # Break out of the loops if we're taking the picture
                # and we're not in debug mode
                if ((not debugMode) and takePicture):
                    break
            if ((not debugMode) and takePicture):
                break
        if ((not debugMode) and takePicture):
            break
    if (debugMode):
        debugimage.save('debug.bmp')
        print "Debug Image Written"
    return takePicture


if __name__ == "__main__":
    image1, buffer1 = captureTestImage(cameraSettings, testWidth, testHeight)
    lastCapture = time.time()

    while (True):
        image2, buffer2 = captureTestImage(cameraSettings, testWidth,
                                           testHeight)

        if detectMotion(image1, buffer1, image2, buffer2, testAreaCount,
                        testBorders):
            captureImage(cameraSettings, saveWidth, saveHeight, saveQuality,
                         diskSpaceToReserve)
            lastCapture = time.time()

        if (forceCapture and time.time() - lastCapture > forceCaptureTime):
            captureImage(cameraSettings, saveWidth, saveHeight, saveQuality,
                         diskSpaceToReserve)
            lastCapture = time.time()

        image1, buffer1 = image2, buffer2

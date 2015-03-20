PyPiCam
=======

Python implementation of motion detection timelapse software for the
RaspberryPi camera module.

How It Works
------------

PyPiCam starts by taking two small test images and calculating the
differences in the green channels of each image. If the number of changed
pixels is greater than the threshold a full size image is captured, the
test images are swapped and a new test image is taken in order to repeat
the process.

Since there is the possibility that there can be frequently moving yet
uninteresting objects in the frame PyPiCam allows you to setup portions
of the image that are ignored by the motion detection algorithm. Turning
on debug mode will place debug bitmaps in the CWD with the motion detected
pixels changed to green and the exclusion borders highlited in blue. The
`testPrinter.py` program will print an ASCII representation of the test
borders.

### Test areas and borders

Test areas and borders are the exlusion zones for the motion capture
algorithm(s) and are defined as a list of x,y pairs defining the corners
of a box in the image. From TFC:



TODO
----
* Automatic upload to cloudfiles/swift
* Flask application to stream jpegs from cloudfiles based on Miguels work
  here: https://github.com/miguelgrinberg/flask-video-streaming
* Alternate motion detection algorithms, convolution matrix, H.264 motion
  vector
* Daemonize PyPiCam
* Move configuration options to a config file


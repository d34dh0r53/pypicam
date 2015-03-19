#!/usr/bin/env python

testWidth = 100
testHeight = 100

testImage = [['.' for x in xrange(testWidth)] for x in xrange(testHeight)]

testAreaCount = 2
testBorders = [[[1, 50], [1, 75]], [[51, 100], [26, 75]]]

for z in xrange(0, testAreaCount):
    for x in xrange(testBorders[z][0][0]-1, testBorders[z][0][1]):
        for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):
            testImage[x][y] = 'X'


def printMatrix(testMatrix):
    for i, element in enumerate(testMatrix):
        print ''.join(element)

printMatrix(testImage)

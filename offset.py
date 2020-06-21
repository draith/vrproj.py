#! /usr/bin/python

import sys
import math
import os
import fnmatch
import numpy as np
from PIL import Image
from PIL import ImageFilter
from skimage.transform import warp
from skimage.exposure import match_histograms
from skimage.exposure import rescale_intensity
from skimage.feature import canny

orig = Image.open("Alfa3_Marilin.jpg")
limX, limY = orig.size
maxShift = round(limX / 10)

red, green, blue = orig.split()

redArray = np.array(red)
greenArray = np.array(green)
blueArray = np.array(blue)

sigma=maxShift/10
low_threshold=0.25
high_threshold=0.75

while True:
    redEdges = canny(redArray, sigma, low_threshold, high_threshold, None, True)
    greenEdges = canny(greenArray, sigma, low_threshold, high_threshold, None, True)

    Image.fromarray((redEdges * 255).astype(np.uint8)).show()
    Image.fromarray((greenEdges * 255).astype(np.uint8)).show()

    newSigma = input(f"sigma [{sigma}]: ")
    newLow = input(f"Low join threshold [{low_threshold}]: ")
    newHigh = input(f"High join threshold [{high_threshold}]: ")

    if newSigma == "" and newLow == "" and newHigh == "":
        break

    if newSigma != "":
        sigma = float(newSigma)
    if newLow != "":
        low_threshold = float(newLow)
    if newHigh != "":
        high_threshold = float(newHigh)

leftImage = np.array(orig)
rightImage = np.array(orig)


for y in range(limY):
    print(f"Line {y+1} of {limY + 1}", end='\r')
    # Find any overlapping regions between edges, and shift channels to match in each output image
    redLine = redEdges[y]
    greenLine = greenEdges[y]
    redStarts = []
    greenStarts = []
    redEnds = []
    greenEnds = []
    redRunStart = 0
    greenRunStart = 0
    lastRed = redLine[0]
    lastGreen = greenLine[0]
    lastRedChange = 0
    lastGreenChange = 0

    # Get runs between edges >= maxShift, in red and green images

    for x in range(limX):
        if redLine[x] != lastRed:
            if redLine[x] and x > lastRedChange + (2*maxShift):
                # End of a run between edges
                redStarts.append(lastRedChange)
                redEnds.append(x)
                # for rangeX in range(lastRedChange,x):
                #     rangeImage[y, rangeX, 0] = 255
            lastRedChange = x
            lastRed = redLine[x]

        if greenLine[x] != lastGreen:
            if greenLine[x] and x > lastGreenChange + (2*maxShift):
                # End of a run between edges
                greenStarts.append(lastGreenChange)
                greenEnds.append(x)
                # for rangeX in range(lastGreenChange,x):
                #     rangeImage[y, rangeX, 1] = 255
            lastGreenChange = x
            lastGreen = greenLine[x]
    
    # Find matching runs in red and green, and write shifted red...
    redRunNumber = 0
    greenRunNumber = 0
    redX = 0
    shiftedRedX = 0
    redStart = 0
    while redRunNumber < len(redStarts) and greenRunNumber < len(greenStarts):
        # Search for matching starts
        if greenStarts[greenRunNumber] > redStarts[redRunNumber] + maxShift:
            redRunNumber += 1
        elif greenStarts[greenRunNumber] < redStarts[redRunNumber] - maxShift:
            greenRunNumber += 1
        else:
            # Matching starts - note starting positions and look for matching ends
            redStart = redStarts[redRunNumber]
            greenStart = greenStarts[greenRunNumber]

            # Perform shifts, up to start
            if greenStart > shiftedRedX:
                xStep = (redStart - redX) / (greenStart - shiftedRedX)
                for x in range(shiftedRedX, greenStart):
                    rightImage[y, x, 0] = redArray[y, round(redX)]
                    redX += xStep
                redX = redStart
                shiftedRedX = greenStart

            while redRunNumber < len(redEnds) and greenRunNumber < len(greenEnds):
                if greenEnds[greenRunNumber] > redEnds[redRunNumber] + maxShift:
                    redRunNumber += 1
                elif greenEnds[greenRunNumber] < redEnds[redRunNumber] - maxShift:
                    greenRunNumber += 1
                else:
                    # Matching ends => matching RUNS - write shifted red pixels through range
                    # Start point: shiftedRedX from redX
                    # End point: greenEnd from redEnd
                    xStep = (redEnds[redRunNumber] - redStart) / (greenEnds[greenRunNumber] - greenStart) 
                    for x in range(shiftedRedX, greenEnds[greenRunNumber]):
                        rightImage[y, x, 0] = redArray[y, round(redX)]
                        redX += xStep

                    redX = redEnds[redRunNumber]
                    shiftedRedX = greenEnds[greenRunNumber]
                    redRunNumber += 1
                    greenRunNumber += 1

    # Now finish line from redX to limX
    if shiftedRedX < limX:
        xStep = (limX - redX) / (limX - shiftedRedX)
        for x in range(shiftedRedX, limX):
            rightImage[y, x, 0] = redArray[y,min(round(redX),limX-1)]
            redX += xStep

# Image.fromarray(rangeImage).show()
Image.fromarray(rightImage).show()

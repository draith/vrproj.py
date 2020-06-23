#! /usr/bin/python

import sys
import math
import os
import fnmatch
import numpy as np
from PIL import Image
from PIL import ImageFilter
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
    newShift = input(f"maxShift [{maxShift}]: ")
    newLow = input(f"Low join threshold [{low_threshold}]: ")
    newHigh = input(f"High join threshold [{high_threshold}]: ")

    if newSigma == "" and newShift == "" and newLow == "" and newHigh == "":
        break

    if newSigma != "":
        sigma = float(newSigma)
    if newShift != "":
        maxShift = int(newShift)
    if newLow != "":
        low_threshold = float(newLow)
    if newHigh != "":
        high_threshold = float(newHigh)

Image.fromarray((redEdges * 255).astype(np.uint8)).save("redEdges.jpg")
Image.fromarray((greenEdges * 255).astype(np.uint8)).save("greenEdges.jpg")

leftImage = np.array(orig)
rightImage = np.array(orig)

for y in range(limY):
    print(f"Line {y+1} of {limY + 1}", end='\r')
    # Find any overlapping regions between edges, and shift channels to match in each output image
    redLine = redEdges[y]
    greenLine = greenEdges[y]
    prevRedLine = redEdges[max(0, y-1)]
    prevGreenLine = greenEdges[max(0, y-1)]
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
            if redLine[x] and x > lastRedChange + maxShift:
                # End of a run between edges
                redStarts.append(lastRedChange)
                redEnds.append(x)
            lastRedChange = x
            lastRed = redLine[x]

        if greenLine[x] != lastGreen:
            if greenLine[x] and x > lastGreenChange + maxShift:
                # End of a run between edges
                greenStarts.append(lastGreenChange)
                greenEnds.append(x)
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
        elif (redRunNumber < len(redStarts)-1 and
                abs(redStarts[redRunNumber+1] - greenStarts[greenRunNumber]) <
                abs(redStarts[redRunNumber] - greenStarts[greenRunNumber])):
            redRunNumber += 1 # Next run is closer
        elif greenStarts[greenRunNumber] < redStarts[redRunNumber] - maxShift:
            greenRunNumber += 1
        elif (greenRunNumber < len(greenStarts)-1 and
                abs(greenStarts[greenRunNumber+1] - redStarts[redRunNumber]) <
                abs(greenStarts[greenRunNumber] - redStarts[redRunNumber])):
            greenRunNumber += 1 # Next run is closer
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
                elif (redRunNumber < len(redEnds)-1 and
                        abs(redEnds[redRunNumber+1] - greenEnds[greenRunNumber]) <
                        abs(redEnds[redRunNumber] - greenEnds[greenRunNumber])):
                    redRunNumber += 1 # Next run is closer
                elif greenEnds[greenRunNumber] < redEnds[redRunNumber] - maxShift:
                    greenRunNumber += 1
                elif (greenRunNumber < len(greenEnds)-1 and
                        abs(greenEnds[greenRunNumber+1] - redEnds[redRunNumber]) <
                        abs(greenEnds[greenRunNumber] - redEnds[redRunNumber])):
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

Image.fromarray(rightImage).show()
Image.fromarray(rightImage).save("rightImage.jpg")

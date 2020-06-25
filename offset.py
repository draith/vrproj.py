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
maxShift = round(limX / 40)

red, green, blue = orig.split()

redArray = np.array(red)
greenArray = np.array(green)
blueArray = np.array(blue)

sigma=maxShift/3
low_threshold=0.25
high_threshold=0.75

while True:
    redEdges = canny(redArray, sigma, low_threshold, high_threshold, None, True)
    greenEdges = canny(greenArray, sigma, low_threshold, high_threshold, None, True)

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
leftMatches = np.zeros(leftImage.shape, np.uint8)
rightMatches = np.zeros(rightImage.shape, np.uint8)

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
    lastRed = False
    lastGreen = False
    lastRedChange = 0
    lastGreenChange = 0

    # TODO: Right to left from right side.  Reconcile.
    # Find matching edges

    for x in range(limX):
        if redLine[x] != lastRed:
            if not redLine[x]:
                # End of an edge
                redStarts.append(lastRedChange)
                redEnds.append(x)
            lastRedChange = x
            lastRed = redLine[x]

        if greenLine[x] != lastGreen:
            if not greenLine[x]:
                # End of a green edge
                greenStarts.append(lastGreenChange)
                greenEnds.append(x)
            lastGreenChange = x
            lastGreen = greenLine[x]
    
    # Find matching red and green edges, and write shifted red...
    redEdgeNumber = 0
    greenEdgeNumber = 0
    redX = 0
    shiftedRedX = 0
    redStart = 0
    while redEdgeNumber < len(redStarts) and greenEdgeNumber < len(greenStarts):
        # Search for matching edges
        if greenStarts[greenEdgeNumber] > redStarts[redEdgeNumber] + maxShift:
            for edgeX in range(redStarts[redEdgeNumber], redEnds[redEdgeNumber]):
                leftMatches[y, edgeX, 0] = 255
                leftMatches[y, edgeX, 1] = 255
                leftMatches[y, edgeX, 2] = 255
            redEdgeNumber += 1
        elif greenStarts[greenEdgeNumber] < redStarts[redEdgeNumber] - maxShift:
            for edgeX in range(greenStarts[greenEdgeNumber], greenEnds[greenEdgeNumber]):
                leftMatches[y, edgeX, 0] = 255
                leftMatches[y, edgeX, 1] = 255
                leftMatches[y, edgeX, 2] = 255
            greenEdgeNumber += 1
        else:
            # Matching starts
            redStart = redStarts[redEdgeNumber]
            greenStart = greenStarts[greenEdgeNumber]

            mapcolour = (redEdgeNumber % 6) + 1

            for edgeX in range(redStarts[redEdgeNumber], redEnds[redEdgeNumber]):
                leftMatches[y, edgeX, 0] = (mapcolour & 1)  * 255
                leftMatches[y, edgeX, 1] = (mapcolour >> 1 & 1) * 255
                leftMatches[y, edgeX, 2] = (mapcolour >> 2 & 1) * 255
            for edgeX in range(greenStarts[greenEdgeNumber], greenEnds[greenEdgeNumber]):
                rightMatches[y, edgeX, 0] = (mapcolour & 1) * 255
                rightMatches[y, edgeX, 1] = (mapcolour >> 1 & 1) * 255
                rightMatches[y, edgeX, 2] = (mapcolour >> 2 & 1) * 255

            # Perform shifts, up to start
            if greenStart > shiftedRedX:
                xStep = (redStart - redX) / (greenStart - shiftedRedX)
                for x in range(shiftedRedX, greenStart):
                    rightImage[y, x, 0] = redArray[y, round(redX)]
                    redX += xStep
                redX = redStart
                shiftedRedX = greenStart
            redEdgeNumber += 1
            greenEdgeNumber += 1

    # Now finish line from redX to limX
    if shiftedRedX < limX:
        xStep = (limX - redX) / (limX - shiftedRedX)
        for x in range(shiftedRedX, limX):
            rightImage[y, x, 0] = redArray[y,min(round(redX),limX-1)]
            redX += xStep

Image.fromarray(rightImage).show()
Image.fromarray(leftMatches).show()
Image.fromarray(rightMatches).show()
# Image.fromarray(rightImage).save("rightImage.jpg")

#! /usr/bin/python

import sys
import math
import os
import fnmatch
import numpy as np
from PIL import Image
from PIL import ImageFilter
from skimage.feature import canny

def nearMatch(fromX, toX, prevMatchDict):
    for x in range(fromX-1, fromX+2):
        if x in prevMatchDict and prevMatchDict[x] in range(toX-1, toX+2):
            return True
    return False

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


leftImage = np.array(orig)
rightImage = np.array(orig)
leftMatchesImage = np.zeros(leftImage.shape, np.uint8)
rightMatchesImage = np.zeros(rightImage.shape, np.uint8)
prevLineRedMatches = {}
prevLineGreenMatches = {}

for y in range(limY):
    print(f"Line {y+1} of {limY + 1}", end='\r')
    # Find any overlapping regions between edges, and shift channels to match in each output image
    redLine = redEdges[y]
    greenLine = greenEdges[y]
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
    thisLineRedMatches = {}
    thisLineGreenMatches = {}

    while redEdgeNumber < len(redStarts) and greenEdgeNumber < len(greenStarts):
        nextRedStart = redStarts[redEdgeNumber]
        nextGreenStart = greenStarts[greenEdgeNumber]
        # Search for matching edges

        # Skip this red edge if too far to the left, or if nextGreenStart matched 
        # the next redStart in the previous line
        if (nextGreenStart > nextRedStart + maxShift
            or (redEdgeNumber+1 < len(redStarts) and nearMatch(nextGreenStart, redStarts[redEdgeNumber+1], prevLineGreenMatches))):
            for edgeX in range(nextRedStart, redEnds[redEdgeNumber]):
                leftMatchesImage[y, edgeX, 0] = 255
                leftMatchesImage[y, edgeX, 1] = 255
                leftMatchesImage[y, edgeX, 2] = 255
            redEdgeNumber += 1
        # Skip this green edge if too far to the left, or if nextRedStart matched 
        # the next redStart in the previous line
        elif (nextGreenStart < nextRedStart - maxShift
            or (greenEdgeNumber+1 < len(greenStarts) and nearMatch(nextRedStart, greenStarts[greenEdgeNumber+1], prevLineRedMatches))):
            for edgeX in range(nextGreenStart, greenEnds[greenEdgeNumber]):
                rightMatchesImage[y, edgeX, 0] = 255
                rightMatchesImage[y, edgeX, 1] = 255
                rightMatchesImage[y, edgeX, 2] = 255
            greenEdgeNumber += 1
        else:
            # Matching starts
            redStart = nextRedStart
            greenStart = nextGreenStart

            thisLineRedMatches[redStart] = greenStart
            thisLineGreenMatches[greenStart] = redStart

            mapcolour = (redEdgeNumber % 6) + 1

            for edgeX in range(nextRedStart, redEnds[redEdgeNumber]):
                leftMatchesImage[y, edgeX, 0] = (mapcolour & 1)  * 255
                leftMatchesImage[y, edgeX, 1] = (mapcolour >> 1 & 1) * 255
                leftMatchesImage[y, edgeX, 2] = (mapcolour >> 2 & 1) * 255
            for edgeX in range(nextGreenStart, greenEnds[greenEdgeNumber]):
                rightMatchesImage[y, edgeX, 0] = (mapcolour & 1) * 255
                rightMatchesImage[y, edgeX, 1] = (mapcolour >> 1 & 1) * 255
                rightMatchesImage[y, edgeX, 2] = (mapcolour >> 2 & 1) * 255

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

    prevLineGreenMatches = thisLineGreenMatches
    prevLineRedMatches = thisLineRedMatches

Image.fromarray(rightImage).show()
Image.fromarray(leftMatchesImage).show()
Image.fromarray(rightMatchesImage).show()
# Image.fromarray(rightImage).save("rightImage.jpg")

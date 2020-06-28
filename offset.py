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
        if x in prevMatchDict and abs(prevMatchDict[x] - toX) < 2:
            return True
    return False

# def exrapolatedMatch(fromX, prevMatchDict):
#     for x in range(fromX-1, fromX+2):
#         if x in prevMatchDict:
#             return prevMatchDict[x] + fromX - x
#     return 0

filename = sys.argv[1] if len(sys.argv) > 1 else input("Filename: ")
orig = Image.open(filename)
limX, limY = orig.size
maxShift = round(limX / 40)
newShift = input(f"maximum offset [{maxShift}]: ")
if newShift != "":
    maxShift = int(newShift)

red, green, blue = orig.split()

redArray = np.array(red)
greenArray = np.array(green)
blueArray = np.array(blue)

sigma=round(limX / 80)
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
leftMatchesImage = np.zeros(leftImage.shape, np.uint8)
rightMatchesImage = np.zeros(rightImage.shape, np.uint8)
prevLineRedMatches = {}
prevLineGreenMatches = {}

for y in range(limY):
    print(f" Line {y+1} of {limY + 1}", end='\r')
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
    mismatch = False

    # Find edges in Red and Green channels

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
    
    # Find matching red and green edges, and shift channels to match in left and right images
    redEdgeNumber = 0
    greenEdgeNumber = 0
    redX = 0
    shiftedRedX = 0
    redStart = 0
    greenStart = 0
    greenX = 0
    shiftedGreenX = 0
    thisLineRedMatches = {}
    thisLineGreenMatches = {}

    # Search for matching edges
    while redEdgeNumber < len(redStarts) and greenEdgeNumber < len(greenStarts):
        nextRedStart = redStarts[redEdgeNumber]
        nextGreenStart = greenStarts[greenEdgeNumber]

        nextRedJump = limX if redEdgeNumber == len(redStarts) - 1 else redStarts[redEdgeNumber+1] - nextRedStart
        nextGreenJump = limX if greenEdgeNumber == len(greenStarts) - 1 else greenStarts[greenEdgeNumber+1] - nextGreenStart

        # Skip this red edge if too far to the left, or if nextGreenStart matched 
        # the next redStart in the previous line
        if (nextGreenStart > nextRedStart + maxShift # Diff > maxshift: green edge out of range
            or (redEdgeNumber+1 < len(redStarts) # or next red edge is a better match
            and not (nextRedJump < maxShift and abs(nextRedJump - nextGreenJump) < 2)
            and nearMatch(nextGreenStart, redStarts[redEdgeNumber+1], prevLineGreenMatches))):

            # NO MATCH FOR RED EDGE
            for edgeX in range(nextRedStart, redEnds[redEdgeNumber]):
                leftMatchesImage[y, edgeX, 0] = 255
                leftMatchesImage[y, edgeX, 1] = 255
                leftMatchesImage[y, edgeX, 2] = 255
            
            redEdgeNumber += 1

            # exrapolatedGreenStart = exrapolatedMatch(nextRedStart, prevLineRedMatches)
            # if exrapolatedGreenStart > 0:
            #     redStart = nextRedStart
            #     greenStart = exrapolatedGreenStart
            #     print(f"Extrapolated match red {redStart} to green {greenStart}")

        # Skip this green edge if too far to the left, or if nextRedStart matched 
        # the next greenStart in the previous line
        elif (nextRedStart > nextGreenStart + maxShift
            or (greenEdgeNumber+1 < len(greenStarts) 
            and not (nextGreenJump < maxShift and abs(nextGreenJump - nextRedJump) < 2)
            and nearMatch(nextRedStart, greenStarts[greenEdgeNumber+1], prevLineRedMatches))):

            # NO MATCH FOR GREEN EDGE
            for edgeX in range(nextGreenStart, greenEnds[greenEdgeNumber]):
                rightMatchesImage[y, edgeX, 0] = 255
                rightMatchesImage[y, edgeX, 1] = 255
                rightMatchesImage[y, edgeX, 2] = 255
            
            greenEdgeNumber += 1

            # exrapolatedRedStart = exrapolatedMatch(nextGreenStart, prevLineGreenMatches)
            # if exrapolatedRedStart > 0:
            #     greenStart = nextGreenStart
            #     redStart = exrapolatedRedStart
            #     print(f"Extrapolated match green {greenStart} to red {redStart}")

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

            redEdgeNumber += 1
            greenEdgeNumber += 1

        # Perform shifts, up to redStart and greenStart
        if greenStart > shiftedRedX:
            xStep = (redStart - redX) / (greenStart - shiftedRedX)
            for x in range(shiftedRedX, greenStart):
                rightImage[y, x, 0] = redArray[y, round(redX)]
                redX += xStep
            redX = redStart
            shiftedRedX = greenStart
        
        if redStart > shiftedGreenX:
            xStep = (greenStart - greenX) / (redStart - shiftedGreenX)
            for x in range(shiftedGreenX, redStart):
                leftImage[y, x, 1] = greenArray[y, round(greenX)]
                leftImage[y, x, 2] = blueArray[y, round(greenX)]
                greenX += xStep
            greenX = greenStart
            shiftedGreenX = redStart

    # Now finish line from redX and greenX to limX
    if shiftedRedX < limX:
        xStep = (limX - redX) / (limX - shiftedRedX)
        for x in range(shiftedRedX, limX):
            rightImage[y, x, 0] = redArray[y, min(round(redX), limX-1)]
            redX += xStep

    if shiftedGreenX < limX:
        xStep = (limX - greenX) / (limX - shiftedGreenX)
        for x in range(shiftedGreenX, limX):
            leftImage[y, x, 1] = greenArray[y, min(round(greenX), limX-1)]
            leftImage[y, x, 2] = blueArray[y, min(round(greenX), limX-1)]
            greenX += xStep

    prevLineGreenMatches = thisLineGreenMatches
    prevLineRedMatches = thisLineRedMatches

Image.fromarray(leftMatchesImage).show()
Image.fromarray(rightMatchesImage).show()
 
sideBySideImage = Image.new("RGB", (2 * limX, limY))
sideBySideImage.paste(Image.fromarray(leftImage))
sideBySideImage.paste(Image.fromarray(rightImage), (limX, 0))
sideBySideImage.show()

nameBase, nameExt = os.path.splitext(filename)
sideBySideImage.save(nameBase + "_SBS" + nameExt)
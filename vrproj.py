#! /usr/bin/python

import sys
import math
import os
import fnmatch
from PIL import Image, ImageDraw

# f = 3250 # Moto G7: 3250 pixels.
vertRangeDeg = 60
vrFieldDim = 3000
yCentre = int(vrFieldDim/2)

# Equivalent pixel distance from viewpoint to centre of original image, given image height and arc.
def fPixels(origHeight, vertRangeDeg):
    return origHeight * 0.5 / math.tan(vertRangeDeg * math.pi / 360)

# Project one half of image, centred at xMid, to output spherical projection.
def projectHalf(side, f, xMid, origXmid, maxXdiff, origHeight, origYcentre, inPixels, draw):
    for x in range(xMid, xMid + maxXdiff):
        x2 = xMid - (x - xMid)
        if (x & 15 == 0):
            print(f'{side} image, column {x - x2} of {(maxXdiff + 1) << 1}', end='\r')
        angleX = math.pi * (x - xMid) / vrFieldDim
        horizDist = f / math.cos(angleX)
        maxYtan = origHeight / (2 * horizDist)
        maxYdiff = int(math.atan(maxYtan) * vrFieldDim / math.pi)
        origXdiff = int(f * math.tan(angleX))
        origX = origXmid + origXdiff
        origX2 = origXmid - origXdiff

        # Copy pixels from original image to projection
        for y in range(yCentre, yCentre + maxYdiff):
            angleY = math.pi * (y - yCentre) / vrFieldDim
            origYdiff = int(horizDist * math.tan(angleY))
            origY = origYcentre + origYdiff
            origY2 = origYcentre - origYdiff
            y2 = yCentre - (y - yCentre)
            draw.point([x,y], inPixels[origX, origY])
            if (x2 != x):
                draw.point([x2,y], inPixels[origX2, origY])
            if (y2 != y):
                draw.point([x,y2], inPixels[origX, origY2])
                if (x2 != x):
                    draw.point([x2,y2], inPixels[origX2, origY2])
    
    return

def processFile(filename, vrFilename):
    inImage = Image.open(filename)
    inPixels = inImage.load()

    # Black background image - side by side
    vrImage = Image.new("RGB", (2 * vrFieldDim, vrFieldDim))

    origWidth, origHeight = inImage.size
    origWidth = int(origWidth / 2)

    f = fPixels(origHeight, vertRangeDeg)

    origXcentre = int(origWidth / 2)
    origYcentre = int(origHeight / 2)

    print(f'{filename}: {origWidth} x {origHeight} pixels.')

    maxXtan = origWidth / (2 * f)
    maxXdiff = int(math.atan(maxXtan) * vrFieldDim / math.pi)

    d = ImageDraw.Draw(vrImage)

    xCentre = int(vrFieldDim/2)

    projectHalf("Left", f, xCentre, origXcentre, maxXdiff, origHeight, origYcentre, inPixels, d)
    projectHalf("Right", f, xCentre + vrFieldDim, origXcentre + origWidth, maxXdiff, origHeight, origYcentre, inPixels, d)

    vrImage.save(vrFilename)

################# MAIN BODY #################
vertRangeInput = input("Max vertical size (60 deg): ")
if vertRangeInput != "":
    vertRangeDeg = int(vertRangeInput)

files = os.listdir()

for file in files:
    if fnmatch.fnmatch(file, "*.jpg") and not fnmatch.fnmatch(file, "*_vr.jpg"):
        nameBase, nameExt = os.path.splitext(file)
        vrName = nameBase + "_vr" + nameExt
        if vrName not in files:
            processFile(file, vrName)

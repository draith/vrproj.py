#! /usr/bin/python

import sys
import math
import os
import fnmatch
from PIL import Image, ImageDraw

# f = 3250 # Moto G7: 3250 pixels.
vertRangeDeg = 60 # default vertical range of image (60 degrees)
vrFieldDim = 3000 # pixels per 180 degrees.
yCentre = int(vrFieldDim/2) # centre height (straight ahead)

# Equivalent pixel distance from observer to centre of original image, given image height and arc.
def fPixels(origHeight, vertRangeDeg):
    return origHeight * 0.5 / math.tan(vertRangeDeg * math.pi / 360)

def processFile(filename, vrFilename):
    inImage = Image.open(filename)
    inPixels = inImage.load()

    # Black background image - side by side
    vrImage = Image.new("RGB", (2 * vrFieldDim, vrFieldDim))
    d = ImageDraw.Draw(vrImage)

    origWidth, origHeight = inImage.size

    # origWidth = width of one side of the original stereo pair
    origWidth = int(origWidth / 2)

    f = fPixels(origHeight, vertRangeDeg)

    origXcentre = int(origWidth / 2)
    origYcentre = int(origHeight / 2)

    print(f'{filename}: {origWidth} x {origHeight} pixels.')

    maxXtan = origWidth / (2 * f)
    maxXdiff = int(math.atan(maxXtan) * vrFieldDim / math.pi)

    xCentre = int(vrFieldDim/2)

    for x in range(xCentre, xCentre + maxXdiff):
        # x2: left half of left image
        x2 = xCentre - (x - xCentre)

        # xr & x2r: right and left halves of right image
        xr = x + vrFieldDim
        x2r = x2 + vrFieldDim

        if (x & 15 == 0):
            print(f'Column {x - x2} of {(maxXdiff + 1) << 1}', end='\r')
        
        angleX = math.pi * (x - xCentre) / vrFieldDim
        horizDist = f / math.cos(angleX)
        maxYtan = origHeight / (2 * horizDist)
        maxYdiff = int(math.atan(maxYtan) * vrFieldDim / math.pi)
        origXdiff = int(f * math.tan(angleX))
        origX = origXcentre + origXdiff
        origX2 = origXcentre - origXdiff
        origXr = origX + origWidth
        origX2r = origX2 + origWidth

        # Copy pixels from original image to projection
        for y in range(yCentre, yCentre + maxYdiff):
            angleY = math.pi * (y - yCentre) / vrFieldDim
            origYdiff = int(horizDist * math.tan(angleY))
            origY = origYcentre + origYdiff
            origY2 = origYcentre - origYdiff
            y2 = yCentre - (y - yCentre)
            d.point([x,y], inPixels[origX, origY])
            d.point([xr,y], inPixels[origXr, origY])
            if (x2 != x):
                d.point([x2,y], inPixels[origX2, origY])
                d.point([x2r,y], inPixels[origX2r, origY])
            if (y2 != y):
                d.point([x,y2], inPixels[origX, origY2])
                d.point([xr,y2], inPixels[origXr, origY2])
                if (x2 != x):
                    d.point([x2,y2], inPixels[origX2, origY2])
                    d.point([x2r,y2], inPixels[origX2r, origY2])

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

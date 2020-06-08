#! /usr/bin/python

import sys
import math
import os
import fnmatch
import numpy as np
from PIL import Image, ImageDraw
from skimage.transform import warp

vertRangeDeg = 60 # default vertical range of image (60 degrees)
vrFieldDim = 3000 # pixels per 180 degrees.
vRange = 0
maxAlpha = 0
uRange = 0 # calculated from f and origX
yCentre = int(vrFieldDim/2) # centre height (straight ahead)
maxPhi = 0 # max horizontal angle from centre

# Equivalent pixel distance from observer to centre of original image, given image height and arc.
def fPixels(origHeight, vertRangeDeg):
    return origHeight * 0.5 / math.tan(vertRangeDeg * math.pi / 360)

f = 1
origXcentre, origYcentre = 0, 0

def warpFunction(uv):
    u = uv[:,0]
    v = uv[:,1]

    phi = maxPhi * (2 * u / uRange - 1)         # phi = horiz arc from centre
    x = f * np.tan(phi) + origXcentre           # x = horiz coordinate on original image plane
    d = f / np.cos(phi)                         # d = distance in pixels to centre line at phi

    alpha = maxAlpha * (2 * v / vRange - 1)     # alpha = vertical arc
    y = d * np.tan(alpha) + origYcentre         # y = vertical coordinate on original image plane

    return np.vstack((x, y)).T                  # Combine x & y coordinates for warp function

def warpedImage(orig):
    origData = np.array(orig)
    warpedData = warp(origData, warpFunction, output_shape=(vRange, uRange))
    warpedData = (warpedData * 255).astype(np.uint8)
    return Image.fromarray(warpedData)

def processFile(filename, vrFilename):
    stereoPair = Image.open(filename)

    global origXcentre
    global origYcentre
    origX, origY = stereoPair.size
    origXcentre = round(origX / 4)
    origYcentre = round(origY / 2)

    global f
    f = fPixels(origY, vertRangeDeg)
    global maxPhi
    maxPhi = math.atan(origXcentre/f)
    global uRange
    uRange = round(vrFieldDim * 2 * maxPhi / math.pi)
    uOffset = round((vrFieldDim - uRange) / 2)
    vOffset = round((vrFieldDim - vRange) / 2)

    # Black background
    vrImage = Image.new("RGB", (2 * vrFieldDim, vrFieldDim))

    # Left image
    orig = stereoPair.crop((0, 0, round(origX/2), origY))
    vrImage.paste(warpedImage(orig), (uOffset, vOffset))

    # Right image
    orig = stereoPair.crop((round(origX/2), 0, origX, origY))
    vrImage.paste(warpedImage(orig), (uOffset + vrFieldDim, vOffset))

    vrImage.save(vrFilename)

################# MAIN BODY #################
vertRangeInput = input("Max vertical size (60 deg): ")
if vertRangeInput != "":
    vertRangeDeg = int(vertRangeInput)

vRange = round(vrFieldDim * vertRangeDeg / 180)
maxAlpha = vertRangeDeg * math.pi / 360     # alpha = vertical arc from centre

files = os.listdir()

for file in files:
    if fnmatch.fnmatch(file, "*.jpg") and not fnmatch.fnmatch(file, "*_vr.jpg"):
        nameBase, nameExt = os.path.splitext(file)
        vrName = nameBase + "_vr" + nameExt
        if vrName not in files:
            print("Processing " + file)
            processFile(file, vrName)

#! /usr/bin/python

import sys
import math
import os
import fnmatch
import numpy as np
#from numpy import array
from PIL import Image, ImageDraw
from skimage.transform import warp

# f = 3250 # Moto G7: 3250 pixels.
vertRangeDeg = 60 # default vertical range of image (60 degrees)
vrFieldDim = 3000 # pixels per 180 degrees.
vRange = round(vrFieldDim * vertRangeDeg / 180)
uRange = 0 # calculated from f and origX
yCentre = int(vrFieldDim/2) # centre height (straight ahead)
maxPhi = 0 # max horizontal angle from centre


# Equivalent pixel distance from observer to centre of original image, given image height and arc.
def fPixels(origHeight, vertRangeDeg):
    return origHeight * 0.5 / math.tan(vertRangeDeg * math.pi / 360)

f = 1
origX, origy = 0, 0
origXcentre, origYcentre = 0, 0

def warpFunction(uv):
    u = uv[:,0]
    v = uv[:,1]

    # phi = horiz arc from centre
    phi = maxPhi * (2 * u / uRange - 1)

    # x = horiz coordinate on original image plane
    x = f * np.tan(phi) + origXcentre

    # d = distance in pixels to centre line at phi
    d = f / np.cos(phi)

    # alpha = vertical arc from centre
    maxAlpha = vertRangeDeg * math.pi / 360
    alpha = maxAlpha * (2 * v / vRange - 1)

    # y = vertical coordinate on original image plane
    y = d * np.tan(alpha) + origYcentre

    # Combine x & y coordinates for warp function
    return np.vstack((x, y)).T

############# TESTING ################
orig = Image.open("grid.jpg")

origX, origY = orig.size
origXcentre = origX / 2
origYcentre = origY / 2

f = fPixels(origY, vertRangeDeg)
maxPhi = math.atan(origXcentre/f)
uRange = round(vrFieldDim * 2 * maxPhi / math.pi)
origData = np.array(orig)

warpedData = warp(origData, warpFunction, output_shape=(vRange, uRange))
warpedData = (warpedData * 255).astype(np.uint8)

warped = Image.fromarray(warpedData)

warped.show()

sys.exit()

################# MAIN BODY #################
vertRangeInput = input("Max vertical size (60 deg): ")
if vertRangeInput != "":
    vertRangeDeg = int(vertRangeInput)

files = os.listdir()

for file in files:
    if fnmatch.fnmatch(file, "*.jpg") and not fnmatch.fnmatch(file, "*_vr.jpg"):
        nameBase, nameExt = os.path.splitext(file)
        vrName = nameBase + "_vr" + nameExt
        #if vrName not in files:
        processFile(file, vrName)

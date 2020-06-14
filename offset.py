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

# from skimage.color import rgb2gray
# from skimage.registration import optical_flow_tvl1

orig = Image.open("Alfa3_Marilin.jpg")

red, green, blue = orig.split()

redEdges = canny(np.array(red))
greenEdges = canny(np.array(green))

#red_warp = warp(np.array(red), np.array([row_coords + flowX, col_coords]), mode='nearest')
#Image.fromarray((red_warp * 255).astype(np.uint8)).show()

Image.fromarray((redEdges * 255).astype(np.uint8)).show()
Image.fromarray((greenEdges * 255).astype(np.uint8)).show()

limX, limY = orig.size

maxShift = round(limX / 10)

# Find offset for each point giving max run length at that point
Offsets = np.zeros(redEdges.shape)
for y in range(limY):
    print(f"Line {y+1} of {limY + 1}")
    redLine = redEdges[y]
    greenLine = greenEdges[y]
    maxRuns = np.zeros(limX)
    for offset in range(-maxShift, maxShift):
        # Identify runs of equality between redLine[x] and greenLine[x+delta]
        runStartX = 0
        x = 0
        while x <= limX:
            if x == limX or redLine[x] != greenLine[min(max(0, x+offset), limX-1)]:
                # end of run - record offset where runLength > max
                runLength = x - runStartX
                for runX in range(runStartX, min(x, limX-1)):
                    if runLength > maxRuns[runX]:
                        maxRuns[runX] = runLength
                        Offsets[y][runX] = offset

                # start of next candidate run
                runStartX = x + 1
            x += 1

    # # Display runs
    # runStart = 0
    # runOffset = 0
    # for x in range(limX+1):
    #     if x == limX or Offsets[y][x] != runOffset:
    #         if x > 0:
    #             print(f"{runStart} to {x-1}: {runOffset}")
    #         if x < limX:
    #             runOffset = Offsets[y][x]
    #             runStart = x

Image.fromarray((Offsets + maxShift) * 255/maxShift.astype(np.uint8)).show()

# build an RGB image with the registered sequence
# reg_im = np.zeros((nr, nc, 3))
# reg_im[..., 0] = red_warp
# reg_im[..., 1] = np.array(green)
# reg_im[..., 2] = np.array(blue)
# Image.fromarray(reg_im).show()
# orig.show()

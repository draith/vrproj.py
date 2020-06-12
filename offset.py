#! /usr/bin/python

import sys
import math
import os
import fnmatch
import numpy as np
from PIL import Image
from PIL import ImageFilter
from skimage.transform import warp
from skimage.color import rgb2gray
from skimage.registration import optical_flow_tvl1

orig = Image.open("Alfa3_Marilin.jpg")

red, green, blue = orig.split()
redEdges = red.filter(ImageFilter.FIND_EDGES) #.show()
greenEdges = green.filter(ImageFilter.FIND_EDGES) #.show()


# grey = rgb2gray(orig)
flowX, flowY = optical_flow_tvl1(np.array(redEdges), np.array(greenEdges))

maxFlow = np.max(flowX)
minFlow = np.min(flowX)

flowX = flowX - minFlow

flowX = flowX * 255 / (maxFlow - minFlow)
flowX = flowX.astype(np.uint8)
Image.fromarray(flowX).show()


# --- Use the estimated optical flow for registration
nc, nr = red.size

row_coords, col_coords = np.meshgrid(np.arange(nr), np.arange(nc), indexing='ij')

red_warp = warp(np.array(red), np.array([row_coords + flowX, col_coords]), mode='nearest')

red.show()
Image.fromarray((red_warp * 255).astype(np.uint8)).show()
green.show()

# build an RGB image with the registered sequence
reg_im = np.zeros((nr, nc, 3))
reg_im[..., 0] = red_warp
reg_im[..., 1] = np.array(green)
reg_im[..., 2] = np.array(blue)
Image.fromarray(reg_im).show()
# orig.show()

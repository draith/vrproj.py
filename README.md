# vrproj.py
Converts side-by-side stereoscopic image pairs to 180-degree 3d images for viewing in VR headsets (spherical projection)
Developed for use with Oculus Quest.
Vrproj.py takes as input side-by-side stereo pair images,
and applies a spherical projection so that they can be viewed as 180-degree 3d images on the headset.
All jpg images in the current directory without a _vr suffix in the filename root are processed, with the results
being saved with the suffix.  The user is prompted to enter the maximum vertical arc of the resulting image
(from top to bottom). The output image size (including black background which extends to the
180-degree limits of the VR view) is hard coded at 6k X 3k pixels.

Input image preparation.
-----------------------
For comfortable viewing of the output image, no corresponding points on the left and right images
should be more than half of the total output image width apart.
Therefore, the input images often need to be padded with black surrounds on
the sides to ensure that corresponding points in the input image pair are never
further apart than half the total width of the image pair.
(These would generally be the most distant points from the observer
in the original scene.)
The bars should be added on each side of the image pair, not on each side of each image in the pair.)

# offset.py
This program takes as input a single red/cyan anaglyphic stereographic image, and generates a side-by-side colour image pair from it.
The program uses matching of edges detected using 'canny' edge detection.
The user is first prompted for the maximum shift or offset (in pixels) between the red channel image
(interpreted as the left view) and the cyan channel image (interpreted as the right view).
The detected edge sets are displayed and the user is prompted to adjust the edge detection parameters to obtain
a consistent set of edges for each image, with sufficient detail to 
identify significant areas of depth. The program then reconstructs a full colour stereo pair
by matching pairs of edge points in each row of the red and cyan images (within the offset limit entered by the user)
and shifting the cyan image points to the corresponding positions in the red image for the left image,
and shifting the red image points to the matched cyan image positions for the right image.
Entering a smaller sigma (smoothing) factor results in the detection of more edges.
The remaining parameters for the canny edge detection can also be varied, but experimentation has so far
shown that varying the sigma value is sufficient to optimise the sensitivity of edge detection.
Generally, half of the maximum offset value is a good starting point.

The output image is saved with the chosen sigma value appended to the main part of the filename.

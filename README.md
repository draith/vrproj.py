# vrproj.py
Converts side-by-side stereoscopic image pairs to 180-degree 3d images for viewing in VR headsets (spherical projection)
Developed for use with Oculus Quest.
Vrproj.py takes as input side-by-side stereo pair images,
and applies a spherical projection so that they can be viewed as 180-degree 3d images on the headset.
All images without a _vr suffix in the filename root are processed, with the results
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

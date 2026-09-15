"""Operasi Titik (point operations).

Rudimentary, from-scratch implementations of the point operations covered in
an intro Pengolahan Citra (image processing) course, one technique per
module. Built on top of `imagelib` so there are no third-party runtime
dependencies.
"""

from operasi_titik.brightness import adjust_brightness
from operasi_titik.contrast import enhance_contrast
from operasi_titik.grayscale import to_grayscale_average, to_grayscale_weighted
from operasi_titik.negation import negate
from operasi_titik.thresholding import threshold_double, threshold_single

__all__ = [
	"adjust_brightness",
	"enhance_contrast",
	"negate",
	"to_grayscale_average",
	"to_grayscale_weighted",
	"threshold_single",
	"threshold_double",
]

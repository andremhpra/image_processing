"""Convert an in-memory `imagelib.Image` into something Tkinter can display.

Tk's `PhotoImage` natively reads the PPM (`"P6"`, truecolor) and PGM (`"P5"`,
grayscale) formats, so a tiny hand-written header is enough to hand it pixel
data directly, no GUI imaging library needed. Thumbnailing reuses this
project's own `scale`, so the preview panel is built entirely out of the
same operations the GUI exists to exercise.

Samples are always rescaled to 8-bit here, regardless of the source image's
own bit depth: a 1-bit binary image needs its 0/1 values stretched out to
0/255 to be visible at all, and this sidesteps ever needing to trust a
particular Tk build's support for wider (16-bit) PPM/PGM samples.
"""

import tkinter as tk

from imagelib.image import Coordinate, Image, as_gray, as_rgb
from operasi_geometri.scaling import scale


def to_photo_image(image: Image, max_size: int = 220) -> tk.PhotoImage:
	"""Convert an image to a Tkinter-displayable thumbnail.

	Args:
		image: The image to convert; mode `"L"` or `"RGB"`, at any bit depth.
		max_size: The thumbnail's longer side, in pixels; `image` is
			downscaled (never upscaled) to fit.

	Returns:
		A `tk.PhotoImage` holding the (possibly downscaled) image's pixels,
		rescaled to 8 bits per channel for display.
	"""
	thumbnail = _fit(image, max_size)
	width, height = thumbnail.size
	max_value = thumbnail.max_value
	if thumbnail.mode == "L":
		header = f"P5\n{width} {height}\n255\n".encode("ascii")
		body = bytes(
			_to_byte(as_gray(thumbnail.getpixel(Coordinate(x, y))), max_value)
			for y in range(height)
			for x in range(width)
		)
	else:
		header = f"P6\n{width} {height}\n255\n".encode("ascii")
		body = bytearray()
		for y in range(height):
			for x in range(width):
				r, g, b = as_rgb(thumbnail.getpixel(Coordinate(x, y)))
				body.extend((_to_byte(r, max_value), _to_byte(g, max_value), _to_byte(b, max_value)))
		body = bytes(body)
	return tk.PhotoImage(data=header + body)


def _to_byte(value: int, max_value: int) -> int:
	"""Rescale a channel sample from `image`'s own bit depth to 0-255.

	Args:
		value: The sample value, on the source image's own 0..`max_value` scale.
		max_value: The source image's max channel value.

	Returns:
		`value` linearly rescaled to 0-255.
	"""
	return round(value * 255 / max_value)


def _fit(image: Image, max_size: int) -> Image:
	"""Downscale (never upscale) so the longer side is at most max_size pixels.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		max_size: The longest allowed side length, in pixels.

	Returns:
		`image` unchanged if it already fits, otherwise a downscaled copy.
	"""
	width, height = image.size
	factor = min(1.0, max_size / max(width, height))
	if factor >= 1.0:
		return image
	return scale(image, factor, factor)

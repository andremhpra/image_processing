"""Convert an in-memory `imagelib.Image` into something Tkinter can display.

Tk's `PhotoImage` natively reads the PPM (`"P6"`, truecolor) and PGM (`"P5"`,
grayscale) formats, so a tiny hand-written header is enough to hand it pixel
data directly, no GUI imaging library needed. Thumbnailing reuses this
project's own `scale`, so the preview panel is built entirely out of the
same operations the GUI exists to exercise.
"""

import tkinter as tk

from imagelib.image import Image, as_gray, as_rgb
from operasi_titik_geometri.scaling import scale


def to_photo_image(image: Image, max_size: int = 220) -> tk.PhotoImage:
	"""Convert an image to a Tkinter-displayable thumbnail.

	Args:
		image: The image to convert; mode `"L"` or `"RGB"`.
		max_size: The thumbnail's longer side, in pixels; `image` is
			downscaled (never upscaled) to fit.

	Returns:
		A `tk.PhotoImage` holding the (possibly downscaled) image's pixels.
	"""
	thumbnail = _fit(image, max_size)
	width, height = thumbnail.size
	if thumbnail.mode == "L":
		header = f"P5\n{width} {height}\n255\n".encode("ascii")
		body = bytes(as_gray(thumbnail.getpixel((x, y))) for y in range(height) for x in range(width))
	else:
		header = f"P6\n{width} {height}\n255\n".encode("ascii")
		body = bytearray()
		for y in range(height):
			for x in range(width):
				body.extend(as_rgb(thumbnail.getpixel((x, y))))
		body = bytes(body)
	return tk.PhotoImage(data=header + body)


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

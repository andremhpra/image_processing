"""Rotasi (rotating): quarter turn, half turn, and free-angle rotation."""

import math

from imagelib import Image


def rotate_90_cw(image: Image) -> Image:
	"""Quarter turn clockwise. w' = h, h' = w; x' = w'-1-y, y' = x.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image with width and height swapped, rotated 90 degrees clockwise.
	"""
	width, height = image.size
	new_width, new_height = height, width
	out = Image(image.mode, (new_width, new_height), image.bits_per_channel)
	for y in range(height):
		for x in range(width):
			out.putpixel((new_width - 1 - y, x), image.getpixel((x, y)))
	return out


def rotate_180_cw(image: Image) -> Image:
	"""Half turn. x' = w-1-x, y' = h-1-y (same mapping as `flip_combined`).

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, rotated 180 degrees.
	"""
	width, height = image.size
	out = Image(image.mode, (width, height), image.bits_per_channel)
	for y in range(height):
		for x in range(width):
			out.putpixel((width - 1 - x, height - 1 - y), image.getpixel((x, y)))
	return out


def rotate_free(image: Image, degrees: float) -> Image:
	"""Rotate by an arbitrary angle (degrees, counter-clockwise) around the image center.

	The forward mapping is x'=x*cos+y*sin, y'=-x*sin+y*cos, plus
	w'=|w*cos|+|h*sin|, h'=|w*sin|+|h*cos| for the new canvas size. Walking
	the *source* image and writing to those destination coordinates would
	leave unfilled holes in the output wherever rounding skips a pixel, so
	this instead walks the *destination* canvas and looks up each pixel's
	source position with the inverse of that same rotation, anchored on the
	image's center rather than its corner.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		degrees: The rotation angle, in degrees counter-clockwise.

	Returns:
		A new image, resized to fit the rotated content, with any corner
		gaps left at the mode's background value.
	"""
	width, height = image.size
	theta = math.radians(degrees)
	cos_t, sin_t = math.cos(theta), math.sin(theta)

	new_width = max(round(abs(width * cos_t) + abs(height * sin_t)), 1)
	new_height = max(round(abs(width * sin_t) + abs(height * cos_t)), 1)

	cx, cy = width / 2, height / 2
	ncx, ncy = new_width / 2, new_height / 2

	out = Image(image.mode, (new_width, new_height), image.bits_per_channel)
	for ny in range(new_height):
		for nx in range(new_width):
			dx, dy = nx - ncx, ny - ncy
			source_x = round(dx * cos_t - dy * sin_t + cx)
			source_y = round(dx * sin_t + dy * cos_t + cy)
			if 0 <= source_x < width and 0 <= source_y < height:
				out.putpixel((nx, ny), image.getpixel((source_x, source_y)))
	return out

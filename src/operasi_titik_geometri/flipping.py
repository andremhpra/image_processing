"""Pencerminan (flipping): horizontal, vertical, and combined mirroring."""

from imagelib import Image


def flip_horizontal(image: Image) -> Image:
	"""Mirror across the vertical center line: x' = w-1-x, y' = y.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, mirrored left-to-right.
	"""
	width, height = image.size
	out = Image(image.mode, image.size)
	for y in range(height):
		for x in range(width):
			out.putpixel((width - 1 - x, y), image.getpixel((x, y)))
	return out


def flip_vertical(image: Image) -> Image:
	"""Mirror across the horizontal center line: x' = x, y' = h-1-y.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, mirrored top-to-bottom.
	"""
	width, height = image.size
	out = Image(image.mode, image.size)
	for y in range(height):
		for x in range(width):
			out.putpixel((x, height - 1 - y), image.getpixel((x, y)))
	return out


def flip_combined(image: Image) -> Image:
	"""Both mirrors at once: x' = w-1-x, y' = h-1-y (same result as a 180 degree rotation).

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, mirrored both ways.
	"""
	width, height = image.size
	out = Image(image.mode, image.size)
	for y in range(height):
		for x in range(width):
			out.putpixel((width - 1 - x, height - 1 - y), image.getpixel((x, y)))
	return out

"""Ekualisasi Histogram (Histogram Equalization): spread out a skewed distribution of gray levels.

Ko = round(Ci * (L-1) / (w*h)), where Ci is the cumulative count of gray
levels <= i in the input and L is the number of possible levels (256 for
an 8-bit channel).
"""

from typing import Callable

from imagelib.image import Image, PixelValue, as_gray, as_rgb


def equalize_histogram(image: Image) -> Image:
	"""Flatten the image's gray-level distribution. Applied per channel for RGB images.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, with its gray-level
		(or, for RGB, each channel's) histogram equalized.
	"""
	width, height = image.size
	total_pixels = width * height
	levels = image.levels
	out = Image(image.mode, image.size)

	if image.mode == "L":
		mapping = _build_mapping(image, as_gray, total_pixels, levels)
		for y in range(height):
			for x in range(width):
				out.putpixel((x, y), mapping[as_gray(image.getpixel((x, y)))])
	else:
		mappings = [_build_mapping(image, _channel(c), total_pixels, levels) for c in range(3)]
		for y in range(height):
			for x in range(width):
				r, g, b = as_rgb(image.getpixel((x, y)))
				out.putpixel((x, y), (mappings[0][r], mappings[1][g], mappings[2][b]))
	return out


def _channel(index: int) -> Callable[[PixelValue], int]:
	"""Return an accessor for one RGB component (0=R, 1=G, 2=B) of a pixel.

	Lets `_build_mapping` handle grayscale and per-channel RGB the same
	way, since both just need a Callable[[`PixelValue`], int].

	Args:
		index: The RGB component to extract (0=R, 1=G, 2=B).

	Returns:
		A function that pulls that component out of an RGB pixel value.
	"""
	return lambda pixel: as_rgb(pixel)[index]


def _build_mapping(
	image: Image, channel: Callable[[PixelValue], int], total_pixels: int, levels: int
) -> list[int]:
	"""Build a histogram-equalization lookup table for one channel.

	Args:
		image: The source image.
		channel: A function extracting the relevant channel value from a pixel.
		total_pixels: The image's total pixel count (`width * height`).
		levels: The number of possible gray levels (`image.levels`).

	Returns:
		A `levels`-entry list mapping each input gray level to its equalized output level.
	"""
	width, height = image.size
	counts = [0] * levels
	for y in range(height):
		for x in range(width):
			counts[channel(image.getpixel((x, y)))] += 1

	mapping = [0] * levels
	cumulative = 0
	for level, count in enumerate(counts):
		cumulative += count
		mapping[level] = round(cumulative * (levels - 1) / total_pixels)
	return mapping

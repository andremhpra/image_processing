"""Pemotongan (cropping): keep only a rectangular sub-region of the image."""

from imagelib import Image
from imagelib.image import Coordinate, Size


def crop(image: Image, left: int, top: int, right: int, bottom: int) -> Image:
	"""Keep pixels with xL <= x < xR and yT <= y < yB.

	x' = x - xL, y' = y - yT; the new size is w' = xR-xL, h' = yB-yT.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		left: The `crop` box's left edge (xL), inclusive.
		top: The `crop` box's top edge (yT), inclusive.
		right: The `crop` box's right edge (xR), exclusive.
		bottom: The `crop` box's bottom edge (yB), exclusive.

	Returns:
		A new image containing just the cropped region.

	Raises:
		ValueError: If the `crop` box is empty or falls outside `image`'s bounds.
	"""
	width, height = image.size
	if not (0 <= left < right <= width and 0 <= top < bottom <= height):
		raise ValueError(f"crop box ({left}, {top}, {right}, {bottom}) is out of bounds for a {width}x{height} image")

	new_width, new_height = right - left, bottom - top
	out = Image(image.mode, Size(new_width, new_height), image.bits_per_channel)
	for y in range(top, bottom):
		for x in range(left, right):
			out.putpixel(Coordinate(x - left, y - top), image.getpixel(Coordinate(x, y)))
	return out

"""Pengambangan (thresholding): turn a grayscale image into a binary one."""

from typing import Callable

from imagelib import Image
from imagelib.image import as_gray

from operasi_titik_geometri.grayscale import to_grayscale_weighted


def threshold_single(image: Image, ambang: int) -> Image:
	"""0 (black) where Ki < ambang, 255 (white) where Ki >= ambang.

	The assignment spec encodes the binary result as 0/1; here it's scaled to 0/255 so
	the result is an image that can actually be displayed.

	Args:
		image: The source image; converted to grayscale first if not mode `"L"`.
		ambang: The threshold gray level.

	Returns:
		A new mode `"L"` image, same size as `image`, containing only 0 and 255.
	"""
	return _map(image, lambda k: 255 if k >= ambang else 0)


def threshold_double(image: Image, ambang_bawah: int, ambang_atas: int) -> Image:
	"""0 (black) where ambang_bawah <= Ki <= ambang_atas, 255 (white) otherwise.

	Highlights every pixel outside a chosen band of gray levels.

	Args:
		image: The source image; converted to grayscale first if not mode `"L"`.
		ambang_bawah: The band's lower gray-level bound, inclusive.
		ambang_atas: The band's upper gray-level bound, inclusive.

	Returns:
		A new mode `"L"` image, same size as `image`, containing only 0 and 255.
	"""
	return _map(image, lambda k: 0 if ambang_bawah <= k <= ambang_atas else 255)


def _map(image: Image, fn: Callable[[int], int]) -> Image:
	"""Convert `image` to grayscale if needed, then map every gray level through `fn`.

	Args:
		image: The source image; converted to grayscale first if not mode `"L"`.
		fn: A function mapping one input gray level to an output gray level.

	Returns:
		A new mode `"L"` image, same size as `image`.
	"""
	if image.mode != "L":
		image = to_grayscale_weighted(image)
	out = Image("L", image.size)
	width, height = image.size
	for y in range(height):
		for x in range(width):
			out.putpixel((x, y), fn(as_gray(image.getpixel((x, y)))))
	return out

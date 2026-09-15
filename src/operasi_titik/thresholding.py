"""Pengambangan (thresholding): turn a grayscale image into a binary one."""

from typing import Callable

from imagelib import Image
from imagelib.image import Coordinate, as_gray

from operasi_titik.grayscale import to_grayscale_weighted


def threshold_single(image: Image, ambang: int) -> Image:
	"""0 (black) where Ki < ambang, 1 (white) where Ki >= ambang.

	`ambang` is a gray level on `image`'s own scale (e.g. 0-255 for an 8-bit
	source, 0-65535 for a 16-bit one), but the output is always genuinely
	binary: a 1-bit image, matching the assignment spec's 0/1 encoding
	exactly, rather than an 8-bit image merely restricted to two values.

	Args:
		image: The source image; converted to grayscale first if not mode `"L"`.
		ambang: The threshold gray level, on `image`'s own scale.

	Returns:
		A new 1-bit mode `"L"` image, same size as `image`, containing only 0 and 1.
	"""
	return _map(image, lambda k: 1 if k >= ambang else 0)


def threshold_double(image: Image, ambang_bawah: int, ambang_atas: int) -> Image:
	"""0 (black) where ambang_bawah <= Ki <= ambang_atas, 1 (white) otherwise.

	Highlights every pixel outside a chosen band of gray levels. Both bounds
	are gray levels on `image`'s own scale (see `threshold_single`).

	Args:
		image: The source image; converted to grayscale first if not mode `"L"`.
		ambang_bawah: The band's lower gray-level bound, inclusive.
		ambang_atas: The band's upper gray-level bound, inclusive.

	Returns:
		A new 1-bit mode `"L"` image, same size as `image`, containing only 0 and 1.
	"""
	return _map(image, lambda k: 0 if ambang_bawah <= k <= ambang_atas else 1)


def _map(image: Image, fn: Callable[[int], int]) -> Image:
	"""Convert `image` to grayscale if needed, then map every gray level through `fn`.

	Args:
		image: The source image; converted to grayscale first if not mode `"L"`.
		fn: Takes in the grayscale pixel from `image`, which should return `1` or `0` based on the thresholding method.

	Returns:
		A new 1-bit mode `"L"` image, same size as `image`.
	"""
	if image.mode != "L":
		image = to_grayscale_weighted(image)
	out = Image("L", image.size, 1)
	width, height = image.size
	for y in range(height):
		for x in range(width):
			out.putpixel(Coordinate(x, y), fn(as_gray(image.getpixel(Coordinate(x, y)))))
	return out

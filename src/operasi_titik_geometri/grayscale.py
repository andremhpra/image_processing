"""Konversi citra true color menjadi citra keabuan (RGB -> grayscale)."""

from typing import Callable

from imagelib import Image
from imagelib.image import as_rgb


def to_grayscale_average(image: Image) -> Image:
	"""Ko = (R + G + B) / 3, treats all three channels equally.

	Args:
		image: The source image; must be mode `"RGB"`.

	Returns:
		A new mode `"L"` image, same size as `image`.

	Raises:
		ValueError: If `image` isn't mode `"RGB"`.
	"""
	return _convert(image, lambda r, g, b: (r + g + b) / 3)


def to_grayscale_weighted(image: Image, wr: float = 0.299, wg: float = 0.587, wb: float = 0.114) -> Image:
	"""Ko = wr*R + wg*G + wb*B.

	Weights follow the NTSC luma formula: the human eye is most sensitive to
	green, then red, then blue. Note: the assignment spec lists wb as 0.144,
	which doesn't sum to 1 with the other two weights and looks like a
	transcription error, so the standard NTSC value 0.114 is used here.

	Args:
		image: The source image; must be mode `"RGB"`.
		wr: Weight applied to the red channel.
		wg: Weight applied to the green channel.
		wb: Weight applied to the blue channel.

	Returns:
		A new mode `"L"` image, same size as `image`.

	Raises:
		ValueError: If `image` isn't mode `"RGB"`.
	"""
	return _convert(image, lambda r, g, b: wr * r + wg * g + wb * b)


def _convert(image: Image, fn: Callable[[int, int, int], float]) -> Image:
	"""Map every RGB pixel of `image` to a single gray level via `fn`.

	Args:
		image: The source image; must be mode `"RGB"`.
		fn: A function mapping a pixel's (R, G, B) channels to a gray level
			(not necessarily clipped to the output's valid range; this
			function clips it).

	Returns:
		A new mode `"L"` image, same size as `image`.

	Raises:
		ValueError: If `image` isn't mode `"RGB"`.
	"""
	if image.mode != "RGB":
		raise ValueError(f"expected an RGB image, got mode {image.mode!r}")
	out = Image("L", image.size)
	max_value = out.max_value
	width, height = image.size
	for y in range(height):
		for x in range(width):
			r, g, b = as_rgb(image.getpixel((x, y)))
			out.putpixel((x, y), max(0, min(max_value, round(fn(r, g, b)))))
	return out

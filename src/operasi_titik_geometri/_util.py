"""Shared helper for the operasi titik (point operation) techniques."""

from typing import Callable

from imagelib import Image
from imagelib.image import as_gray, as_rgb


def clamp(value: float, low: int, high: int) -> int:
	"""Clip a computed channel value back into a valid range.

	Args:
		value: The computed value to clip and round.
		low: The minimum allowed output value.
		high: The maximum allowed output value.

	Returns:
		`value`, rounded to the nearest int and clipped to [low, high].
	"""
	return max(low, min(high, round(value)))


def apply_point_op(image: Image, fn: Callable[[int], float]) -> Image:
	"""Apply a gray-scale-transform (GST) function to every pixel.

	Mirrors Ko = f(Ki). For `"RGB"` images the same function is
	applied independently to each channel (Ro=fR(Ri), Go=fG(Gi), Bo=fB(Bi)).

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		fn: A function mapping one input channel value to an output value
			(not necessarily clipped to the image's valid range; this
			function clips it).

	Returns:
		A new image, same mode and size as `image`, with `fn` applied to
		every channel of every pixel.
	"""
	out = Image(image.mode, image.size)
	max_value = image.max_value
	width, height = image.size
	for y in range(height):
		for x in range(width):
			value = image.getpixel((x, y))
			if image.mode == "L":
				out.putpixel((x, y), clamp(fn(as_gray(value)), 0, max_value))
			else:
				r, g, b = as_rgb(value)
				out.putpixel(
					(x, y),
					(clamp(fn(r), 0, max_value), clamp(fn(g), 0, max_value), clamp(fn(b), 0, max_value)),
				)
	return out

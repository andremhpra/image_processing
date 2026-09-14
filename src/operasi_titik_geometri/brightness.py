"""Modifikasi Kecemerlangan (brightness modification): Ko = Ki + C."""

from imagelib import Image

from operasi_titik_geometri._util import apply_point_op


def adjust_brightness(image: Image, c: int) -> Image:
	"""Add a constant C to every pixel. C > 0 brightens, C < 0 darkens.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		c: The offset to add to every channel value.

	Returns:
		A new image, same mode and size as `image`, with `c` added to every
		channel of every pixel (clipped to 0..255).
	"""
	return apply_point_op(image, lambda k: k + c)

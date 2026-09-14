"""Negasi (negation): Ko = Kmax - Ki, the digital equivalent of a photo negative."""

from imagelib import Image

from operasi_titik_geometri._util import apply_point_op


def negate(image: Image, kmax: int = 255) -> Image:
	"""Ko = Kmax - Ki, the digital equivalent of a photo negative.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		kmax: The maximum gray level to `negate` against.

	Returns:
		A new image, same mode and size as `image`, with every channel negated.
	"""
	return apply_point_op(image, lambda k: kmax - k)

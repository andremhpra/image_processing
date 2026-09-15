"""Negasi (negation): Ko = Kmax - Ki, the digital equivalent of a photo negative."""

from typing import Optional

from imagelib import Image

from operasi_titik_geometri._util import apply_point_op


def negate(image: Image) -> Image:
	"""Ko = Kmax - Ki, the digital equivalent of a photo negative.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		kmax: The maximum gray level to `negate` against. Defaults to
			`image`'s max channel value (e.g. 255 for an 8-bit channel).

	Returns:
		A new image, same mode and size as `image`, with every channel negated.
	"""
	kmax = image.max_value
	return apply_point_op(image, lambda k: kmax - k)

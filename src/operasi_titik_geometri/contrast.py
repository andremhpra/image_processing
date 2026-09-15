"""Peningkatan Kontras (contrast enhancement): Ko = G * (Ki - P) + P."""

from imagelib import Image

from operasi_titik_geometri._util import apply_point_op


def enhance_contrast(image: Image, gain: float, pivot: int = 127) -> Image:
	"""Stretch values away from (gain > 1) or squeeze them toward (0 < gain < 1) the pivot P.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		gain: The multiplier G applied to each channel's distance from `pivot`.
		pivot: The pivot P that stays fixed under the transform.

	Returns:
		A new image, same mode and size as `image`, with the contrast
		transform applied to every channel of every pixel (clipped to the
		image's valid range).
	"""
	return apply_point_op(image, lambda k: gain * (k - pivot) + pivot)

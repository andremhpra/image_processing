"""Penggabungan Citra (image blending / overlay): C = wa*A + wb*B, wa + wb = 1."""

from typing import Optional

from imagelib.image import RGB, Coordinate, Image, PixelValue, as_gray, as_rgb
from operasi_multi_citra._util import center_offsets, pixel_or


def blend(image_a: Image, image_b: Image, weight_a: float = 0.5) -> Image:
	"""Overlay image_b onto image_a using a weighted sum.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it: the
	weighted mix only applies where the two overlap, and the bigger image's
	pixels show through everywhere else.

	Args:
		image_a: The first image; same mode and bit depth as `image_b`.
		image_b: The second image; same mode and bit depth as `image_a`.
		weight_a: image_a's weight `wa`; image_b's weight is `wb = 1 - wa`.

	Returns:
		A new image, same mode and bit depth as the inputs and sized to the
		larger input, with each overlapping pixel set to `wa*A + wb*B`
		(clipped to the images' valid range), and each non-overlapping pixel
		copied from whichever image covers it.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode or bit depth.
	"""
	if image_a.mode != image_b.mode:
		raise ValueError(f"images must be the same mode to blend, got {image_a.mode!r} and {image_b.mode!r}")
	if image_a.bits_per_channel != image_b.bits_per_channel:
		raise ValueError(
			f"images must be the same bit depth to blend, got {image_a.bits_per_channel} and "
			f"{image_b.bits_per_channel} bits per channel"
		)

	weight_b = 1 - weight_a
	layout = center_offsets(image_a, image_b)

	out = Image(image_a.mode, layout.canvas_size, image_a.bits_per_channel)
	max_value = image_a.max_value
	width, height = layout.canvas_size
	for y in range(height):
		for x in range(width):
			a = pixel_or(image_a, Coordinate(x - layout.offset_a.x, y - layout.offset_a.y))
			b = pixel_or(image_b, Coordinate(x - layout.offset_b.x, y - layout.offset_b.y))
			xy = Coordinate(x, y)
			if a is not None and b is not None:
				out.putpixel(xy, _blend_pixel(image_a.mode, a, b, weight_a, weight_b, max_value))
			elif a is not None:
				out.putpixel(xy, a)
			elif b is not None:
				out.putpixel(xy, b)
	return out


def describe_size_mismatch(image_a: Image, image_b: Image) -> Optional[str]:
	"""Describe, for a warning dialog, how `blend` will reconcile differently-sized images.

	Args:
		image_a: The first image.
		image_b: The second image.

	Returns:
		A human-readable explanation of the centering `blend` will apply,
		or `None` if the two are already the same size.
	"""
	if image_a.size == image_b.size:
		return None
	canvas_width, canvas_height = center_offsets(image_a, image_b).canvas_size
	return (
		f"Image A is {image_a.width}x{image_a.height} and Image B is {image_b.width}x{image_b.height}.\n\n"
		f"The smaller image will be centered on a canvas the size of the larger ({canvas_width}x{canvas_height}); "
		"the weighted mix only applies where the two overlap, and the bigger image's pixels show through "
		"everywhere else."
	)


def _blend_pixel(
	mode: str, a: PixelValue, b: PixelValue, weight_a: float, weight_b: float, max_value: int
) -> PixelValue:
	"""Mix one pair of same-mode pixel values.

	Args:
		mode: The pixels' shared image mode, `"L"` or `"RGB"`.
		a: The first pixel's value.
		b: The second pixel's value.
		weight_a: The weight applied to `a`.
		weight_b: The weight applied to `b`.
		max_value: The largest valid value for one channel sample.

	Returns:
		The mixed pixel value, in the same mode.
	"""
	if mode == "L":
		return _mix(as_gray(a), as_gray(b), weight_a, weight_b, max_value)
	ar, ag, ab = as_rgb(a)
	br, bg, bb = as_rgb(b)
	return RGB(
		_mix(ar, br, weight_a, weight_b, max_value),
		_mix(ag, bg, weight_a, weight_b, max_value),
		_mix(ab, bb, weight_a, weight_b, max_value),
	)


def _mix(a: int, b: int, weight_a: float, weight_b: float, max_value: int) -> int:
	"""Blend one pair of channel values and clip the result to a valid range.

	Args:
		a: The first channel value.
		b: The second channel value.
		weight_a: The weight applied to `a`.
		weight_b: The weight applied to `b`.
		max_value: The largest valid value for one channel sample.

	Returns:
		`round(a * weight_a + b * weight_b)`, clipped to [0, max_value].
	"""
	return max(0, min(max_value, round(a * weight_a + b * weight_b)))

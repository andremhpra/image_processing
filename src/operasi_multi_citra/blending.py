"""Penggabungan Citra (image blending / overlay): C = wa*A + wb*B, wa + wb = 1."""

from typing import Optional

from imagelib.image import Coordinate, Image, PixelValue, as_gray, as_rgb


def blend(image_a: Image, image_b: Image, weight_a: float = 0.5) -> Image:
	"""Overlay image_b onto image_a using a weighted sum.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it: the
	weighted mix only applies where the two overlap, and the bigger image's
	pixels show through everywhere else.

	Args:
		image_a: The first image; same mode as `image_b`.
		image_b: The second image; same mode as `image_a`.
		weight_a: image_a's weight `wa`; image_b's weight is `wb = 1 - wa`.

	Returns:
		A new image, same mode as the inputs and sized to the larger input,
		with each overlapping pixel set to `wa*A + wb*B` (clipped to the
		images' valid range), and each non-overlapping pixel copied from
		whichever image covers it.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode.
	"""
	if image_a.mode != image_b.mode:
		raise ValueError(f"images must be the same mode to blend, got {image_a.mode!r} and {image_b.mode!r}")

	weight_b = 1 - weight_a
	if image_a.size == image_b.size:
		canvas_size = image_a.size
		offset_a: Coordinate = (0, 0)
		offset_b: Coordinate = (0, 0)
	elif image_a.width * image_a.height >= image_b.width * image_b.height:
		canvas_size = image_a.size
		offset_a = (0, 0)
		offset_b = ((image_a.width - image_b.width) // 2, (image_a.height - image_b.height) // 2)
	else:
		canvas_size = image_b.size
		offset_b = (0, 0)
		offset_a = ((image_b.width - image_a.width) // 2, (image_b.height - image_a.height) // 2)

	out = Image(image_a.mode, canvas_size)
	max_value = image_a.max_value
	width, height = canvas_size
	for y in range(height):
		for x in range(width):
			a = _pixel_or_none(image_a, (x - offset_a[0], y - offset_a[1]))
			b = _pixel_or_none(image_b, (x - offset_b[0], y - offset_b[1]))
			if a is not None and b is not None:
				out.putpixel((x, y), _blend_pixel(image_a.mode, a, b, weight_a, weight_b, max_value))
			elif a is not None:
				out.putpixel((x, y), a)
			elif b is not None:
				out.putpixel((x, y), b)
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
	if image_a.width * image_a.height >= image_b.width * image_b.height:
		canvas_width, canvas_height = image_a.size
	else:
		canvas_width, canvas_height = image_b.size
	return (
		f"Image A is {image_a.width}x{image_a.height} and Image B is {image_b.width}x{image_b.height}.\n\n"
		f"The smaller image will be centered on a canvas the size of the larger ({canvas_width}x{canvas_height}); "
		"the weighted mix only applies where the two overlap, and the bigger image's pixels show through "
		"everywhere else."
	)


def _pixel_or_none(image: Image, xy: Coordinate) -> Optional[PixelValue]:
	"""Read a pixel, or `None` if `xy` falls outside `image`'s bounds.

	Args:
		image: The image to read from.
		xy: Pixel coordinate as an (x, y) tuple, possibly out of bounds.

	Returns:
		`image.getpixel(xy)`, or `None` if `xy` is outside `image`.
	"""
	x, y = xy
	width, height = image.size
	if 0 <= x < width and 0 <= y < height:
		return image.getpixel((x, y))
	return None


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
	return (
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

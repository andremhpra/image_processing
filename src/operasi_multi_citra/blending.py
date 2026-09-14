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
		with each overlapping pixel set to `wa*A + wb*B` (clipped to
		0..255), and each non-overlapping pixel copied from whichever image
		covers it.

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
	width, height = canvas_size
	for y in range(height):
		for x in range(width):
			a = _pixel_or_none(image_a, (x - offset_a[0], y - offset_a[1]))
			b = _pixel_or_none(image_b, (x - offset_b[0], y - offset_b[1]))
			if a is not None and b is not None:
				out.putpixel((x, y), _blend_pixel(image_a.mode, a, b, weight_a, weight_b))
			elif a is not None:
				out.putpixel((x, y), a)
			elif b is not None:
				out.putpixel((x, y), b)
	return out


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


def _blend_pixel(mode: str, a: PixelValue, b: PixelValue, weight_a: float, weight_b: float) -> PixelValue:
	"""Mix one pair of same-mode pixel values.

	Args:
		mode: The pixels' shared image mode, `"L"` or `"RGB"`.
		a: The first pixel's value.
		b: The second pixel's value.
		weight_a: The weight applied to `a`.
		weight_b: The weight applied to `b`.

	Returns:
		The mixed pixel value, in the same mode.
	"""
	if mode == "L":
		return _mix(as_gray(a), as_gray(b), weight_a, weight_b)
	ar, ag, ab = as_rgb(a)
	br, bg, bb = as_rgb(b)
	return (
		_mix(ar, br, weight_a, weight_b),
		_mix(ag, bg, weight_a, weight_b),
		_mix(ab, bb, weight_a, weight_b),
	)


def _mix(a: int, b: int, weight_a: float, weight_b: float) -> int:
	"""Blend one pair of channel values and clip the result to 0..255.

	Args:
		a: The first channel value.
		b: The second channel value.
		weight_a: The weight applied to `a`.
		weight_b: The weight applied to `b`.

	Returns:
		`round(a * weight_a + b * weight_b)`, clipped to [0, 255].
	"""
	return max(0, min(255, round(a * weight_a + b * weight_b)))

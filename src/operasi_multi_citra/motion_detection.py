"""Deteksi Gerakan (motion detection): C = |A - B| between two successive frames."""

from typing import Optional

from imagelib.image import RGB, Coordinate, Image, Size, as_gray, as_rgb


def detect_motion(image_a: Image, image_b: Image) -> Image:
	"""Unmoved pixels go to 0 (black); pixels that changed between the two frames stand out.

	If the frames differ in size, both are center-cropped down to their
	common width and height (the smaller of each, between the two) before
	diffing, so the result is sized to fit inside the smaller frame.

	Args:
		image_a: The first (earlier) frame; same mode and bit depth as `image_b`.
		image_b: The second (later) frame; same mode and bit depth as `image_a`.

	Returns:
		A new image, same mode and bit depth as the inputs and sized to the
		smaller input, with C = |A - B|.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode or bit depth.
	"""
	if image_a.mode != image_b.mode:
		raise ValueError(f"images must be the same mode, got {image_a.mode!r} and {image_b.mode!r}")
	if image_a.bits_per_channel != image_b.bits_per_channel:
		raise ValueError(
			f"images must be the same bit depth, got {image_a.bits_per_channel} and "
			f"{image_b.bits_per_channel} bits per channel"
		)

	canvas_size = _min_size(image_a, image_b)
	offset_a = _center_offset(image_a, canvas_size)
	offset_b = _center_offset(image_b, canvas_size)

	out = Image(image_a.mode, canvas_size, image_a.bits_per_channel)
	width, height = canvas_size
	for y in range(height):
		for x in range(width):
			a = image_a.getpixel(Coordinate(x + offset_a.x, y + offset_a.y))
			b = image_b.getpixel(Coordinate(x + offset_b.x, y + offset_b.y))
			xy = Coordinate(x, y)
			if image_a.mode == "L":
				out.putpixel(xy, abs(as_gray(a) - as_gray(b)))
			else:
				ar, ag, ab = as_rgb(a)
				br, bg, bb = as_rgb(b)
				out.putpixel(xy, RGB(abs(ar - br), abs(ag - bg), abs(ab - bb)))
	return out


def describe_size_mismatch(image_a: Image, image_b: Image) -> Optional[str]:
	"""Describe, for a warning dialog, how `detect_motion` will reconcile differently-sized frames.

	Args:
		image_a: The first (earlier) frame.
		image_b: The second (later) frame.

	Returns:
		A human-readable explanation of the center-crop `detect_motion` will
		apply, or `None` if the two are already the same size.
	"""
	if image_a.size == image_b.size:
		return None
	canvas_width, canvas_height = _min_size(image_a, image_b)
	return (
		f"Image A is {image_a.width}x{image_a.height} and Image B is {image_b.width}x{image_b.height}.\n\n"
		f"Both will be center-cropped to {canvas_width}x{canvas_height} (the smaller width and the smaller "
		"height, between the two) before taking the difference."
	)


def _min_size(image_a: Image, image_b: Image) -> Size:
	"""The largest size that fits inside both images, width and height independently.

	Args:
		image_a: The first image.
		image_b: The second image.

	Returns:
		`(min(widths), min(heights))`.
	"""
	return Size(min(image_a.width, image_b.width), min(image_a.height, image_b.height))


def _center_offset(image: Image, size: Size) -> Coordinate:
	"""The top-left offset that centers a `size`-sized crop within `image`.

	Args:
		image: The image being cropped; must be at least as large as `size`
			in both dimensions.
		size: The (width, height) of the crop.

	Returns:
		The (x, y) offset, into `image`, of the centered crop's top-left corner.
	"""
	return Coordinate((image.width - size.width) // 2, (image.height - size.height) // 2)

"""Operasi Logika (logic operations): bitwise AND/OR/XOR/NOT plus a clamped SUB, applied per pixel."""

from typing import Callable, Optional

from imagelib.image import Coordinate, Image, PixelValue, Size, as_gray, as_rgb


def logic_and(image_a: Image, image_b: Image) -> Image:
	"""Bitwise AND of each corresponding pair of 8-bit channel values.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it;
	pixels outside the smaller image's footprint are treated as 0 (black)
	for the AND.

	Args:
		image_a: The first image; same mode as `image_b`.
		image_b: The second image; same mode as `image_a`.

	Returns:
		A new image, same mode as the inputs and sized to the larger input,
		with C = A AND B.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a & b)


def logic_or(image_a: Image, image_b: Image) -> Image:
	"""Bitwise OR of each corresponding pair of 8-bit channel values.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it;
	pixels outside the smaller image's footprint are treated as 0 (black)
	for the OR.

	Args:
		image_a: The first image; same mode as `image_b`.
		image_b: The second image; same mode as `image_a`.

	Returns:
		A new image, same mode as the inputs and sized to the larger input,
		with C = A OR B.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a | b)


def logic_xor(image_a: Image, image_b: Image) -> Image:
	"""Bitwise XOR of each corresponding pair of 8-bit channel values.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it;
	pixels outside the smaller image's footprint are treated as 0 (black)
	for the XOR.

	Args:
		image_a: The first image; same mode as `image_b`.
		image_b: The second image; same mode as `image_a`.

	Returns:
		A new image, same mode as the inputs and sized to the larger input,
		with C = A XOR B.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a ^ b)


def logic_sub(image_a: Image, image_b: Image) -> Image:
	"""A - B where A >= B, 0 otherwise (the assignment's SUB operator, unlike plain subtraction).

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it;
	pixels outside the smaller image's footprint are treated as 0 (black)
	for the subtraction.

	Args:
		image_a: The first image; same mode as `image_b`.
		image_b: The second image; same mode as `image_a`.

	Returns:
		A new image, same mode as the inputs and sized to the larger input,
		with C = A - B (or 0).

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a - b if a >= b else 0)


def logic_not(image: Image) -> Image:
	"""Bitwise complement of each channel value.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, with C = NOT A
		(`image.max_value` - A).
	"""
	out = Image(image.mode, image.size)
	max_value = image.max_value
	width, height = image.size
	for y in range(height):
		for x in range(width):
			value = image.getpixel((x, y))
			if image.mode == "L":
				out.putpixel((x, y), max_value - as_gray(value))
			else:
				r, g, b = as_rgb(value)
				out.putpixel((x, y), (max_value - r, max_value - g, max_value - b))
	return out


def describe_size_mismatch(image_a: Image, image_b: Image) -> Optional[str]:
	"""Describe, for a warning dialog, how the logic operations will reconcile differently-sized images.

	Args:
		image_a: The first image.
		image_b: The second image.

	Returns:
		A human-readable explanation of the centering `_combine` will apply,
		or `None` if the two are already the same size.
	"""
	if image_a.size == image_b.size:
		return None
	canvas_width, canvas_height = _max_size(image_a, image_b)
	return (
		f"Image A is {image_a.width}x{image_a.height} and Image B is {image_b.width}x{image_b.height}.\n\n"
		f"The smaller image will be centered on a canvas the size of the larger ({canvas_width}x{canvas_height}); "
		"pixels outside the smaller image's footprint are treated as 0 (black) before combining."
	)


def _combine(image_a: Image, image_b: Image, op: Callable[[int, int], int]) -> Image:
	"""Apply a binary per-channel operator to each corresponding pair of pixels.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it:
	`op` is applied everywhere on the canvas, with whichever image doesn't
	cover a given pixel contributing 0 (black) there.

	Args:
		image_a: The first image; same mode as `image_b`.
		image_b: The second image; same mode as `image_a`.
		op: A function combining one channel value from each image into
			an output channel value (assumed already in 0..255).

	Returns:
		A new image, same mode as the inputs and sized to the larger input.

	Raises:
		ValueError: If `image_a` and `image_b` differ in mode.
	"""
	if image_a.mode != image_b.mode:
		raise ValueError(f"images must be the same mode, got {image_a.mode!r} and {image_b.mode!r}")

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
			a = _pixel_or_blank(image_a, (x - offset_a[0], y - offset_a[1]))
			b = _pixel_or_blank(image_b, (x - offset_b[0], y - offset_b[1]))
			if image_a.mode == "L":
				out.putpixel((x, y), op(as_gray(a), as_gray(b)))
			else:
				ar, ag, ab = as_rgb(a)
				br, bg, bb = as_rgb(b)
				out.putpixel((x, y), (op(ar, br), op(ag, bg), op(ab, bb)))
	return out


def _max_size(image_a: Image, image_b: Image) -> Size:
	"""The larger of the two images' sizes, by pixel area.

	Args:
		image_a: The first image.
		image_b: The second image.

	Returns:
		`image_a.size` if it has at least as many pixels as `image_b`, else `image_b.size`.
	"""
	if image_a.width * image_a.height >= image_b.width * image_b.height:
		return image_a.size
	return image_b.size


def _pixel_or_blank(image: Image, xy: Coordinate) -> PixelValue:
	"""Read a pixel, or a black (0) value of `image`'s mode if `xy` falls outside `image`.

	Args:
		image: The image to read from.
		xy: Pixel coordinate as an (x, y) tuple, possibly out of bounds.

	Returns:
		`image.getpixel(xy)`, or `0`/`(0, 0, 0)` (matching `image.mode`) if `xy` is outside `image`.
	"""
	x, y = xy
	width, height = image.size
	if 0 <= x < width and 0 <= y < height:
		return image.getpixel((x, y))
	return 0 if image.mode == "L" else (0, 0, 0)

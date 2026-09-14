"""Operasi Logika (logic operations): bitwise AND/OR/XOR/NOT plus a clamped SUB, applied per pixel."""

from typing import Callable

from imagelib.image import Image, as_gray, as_rgb


def logic_and(image_a: Image, image_b: Image) -> Image:
	"""Bitwise AND of each corresponding pair of 8-bit channel values.

	Args:
		image_a: The first image; same size and mode as `image_b`.
		image_b: The second image; same size and mode as `image_a`.

	Returns:
		A new image, same mode and size as the inputs, with C = A AND B.

	Raises:
		ValueError: If `image_a` and `image_b` differ in size or mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a & b)


def logic_or(image_a: Image, image_b: Image) -> Image:
	"""Bitwise OR of each corresponding pair of 8-bit channel values.

	Args:
		image_a: The first image; same size and mode as `image_b`.
		image_b: The second image; same size and mode as `image_a`.

	Returns:
		A new image, same mode and size as the inputs, with C = A OR B.

	Raises:
		ValueError: If `image_a` and `image_b` differ in size or mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a | b)


def logic_xor(image_a: Image, image_b: Image) -> Image:
	"""Bitwise XOR of each corresponding pair of 8-bit channel values.

	Args:
		image_a: The first image; same size and mode as `image_b`.
		image_b: The second image; same size and mode as `image_a`.

	Returns:
		A new image, same mode and size as the inputs, with C = A XOR B.

	Raises:
		ValueError: If `image_a` and `image_b` differ in size or mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a ^ b)


def logic_sub(image_a: Image, image_b: Image) -> Image:
	"""A - B where A >= B, 0 otherwise (the assignment's SUB operator, unlike plain subtraction).

	Args:
		image_a: The first image; same size and mode as `image_b`.
		image_b: The second image; same size and mode as `image_a`.

	Returns:
		A new image, same mode and size as the inputs, with C = A - B (or 0).

	Raises:
		ValueError: If `image_a` and `image_b` differ in size or mode.
	"""
	return _combine(image_a, image_b, lambda a, b: a - b if a >= b else 0)


def logic_not(image: Image) -> Image:
	"""Bitwise complement of each 8-bit channel value.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.

	Returns:
		A new image, same mode and size as `image`, with C = NOT A (255 - A).
	"""
	out = Image(image.mode, image.size)
	width, height = image.size
	for y in range(height):
		for x in range(width):
			value = image.getpixel((x, y))
			if image.mode == "L":
				out.putpixel((x, y), 255 - as_gray(value))
			else:
				r, g, b = as_rgb(value)
				out.putpixel((x, y), (255 - r, 255 - g, 255 - b))
	return out


def _combine(image_a: Image, image_b: Image, op: Callable[[int, int], int]) -> Image:
	"""Apply a binary per-channel operator to each corresponding pair of pixels.

	Args:
		image_a: The first image; same size and mode as `image_b`.
		image_b: The second image; same size and mode as `image_a`.
		op: A function combining one channel value from each image into
			an output channel value (assumed already in 0..255).

	Returns:
		A new image, same mode and size as the inputs.

	Raises:
		ValueError: If `image_a` and `image_b` differ in size or mode.
	"""
	if image_a.size != image_b.size:
		raise ValueError(f"images must be the same size, got {image_a.size} and {image_b.size}")
	if image_a.mode != image_b.mode:
		raise ValueError(f"images must be the same mode, got {image_a.mode!r} and {image_b.mode!r}")

	out = Image(image_a.mode, image_a.size)
	width, height = image_a.size
	for y in range(height):
		for x in range(width):
			a = image_a.getpixel((x, y))
			b = image_b.getpixel((x, y))
			if image_a.mode == "L":
				out.putpixel((x, y), op(as_gray(a), as_gray(b)))
			else:
				ar, ag, ab = as_rgb(a)
				br, bg, bb = as_rgb(b)
				out.putpixel((x, y), (op(ar, br), op(ag, bg), op(ab, bb)))
	return out

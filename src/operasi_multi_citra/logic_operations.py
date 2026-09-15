"""Operasi Logika (logic operations): bitwise AND/OR/XOR/NOT plus a clamped SUB.

Each input is binarized first - converted to grayscale (if not already) and
thresholded to black/white - so every one of these operations always
produces a genuinely 1-bit image: every output pixel is either 0 (black) or
1 (white), never something in between, and regardless of what mode or bit
depth the inputs were.
"""

from typing import Callable, Optional

from imagelib.image import Coordinate, Image, as_gray
from operasi_multi_citra._util import center_offsets, pixel_or
from operasi_titik.thresholding import threshold_single


def logic_and(image_a: Image, image_b: Image) -> Image:
	"""Logical AND of two images, each binarized first.

	If the (binarized) images differ in size, the result takes the size of
	the bigger one (by pixel area) and the smaller image is centered on top
	of it; pixels outside the smaller image's footprint are treated as 0
	(black) for the AND.

	Args:
		image_a: The first image; any mode.
		image_b: The second image; any mode.

	Returns:
		A new 1-bit mode `"L"` image, sized to the larger input, containing
		only 0 and 1, with C = A AND B.
	"""
	return _combine(image_a, image_b, lambda a, b: a & b)


def logic_or(image_a: Image, image_b: Image) -> Image:
	"""Logical OR of two images, each binarized first.

	If the (binarized) images differ in size, the result takes the size of
	the bigger one (by pixel area) and the smaller image is centered on top
	of it; pixels outside the smaller image's footprint are treated as 0
	(black) for the OR.

	Args:
		image_a: The first image; any mode.
		image_b: The second image; any mode.

	Returns:
		A new 1-bit mode `"L"` image, sized to the larger input, containing
		only 0 and 1, with C = A OR B.
	"""
	return _combine(image_a, image_b, lambda a, b: a | b)


def logic_xor(image_a: Image, image_b: Image) -> Image:
	"""Logical XOR of two images, each binarized first.

	If the (binarized) images differ in size, the result takes the size of
	the bigger one (by pixel area) and the smaller image is centered on top
	of it; pixels outside the smaller image's footprint are treated as 0
	(black) for the XOR.

	Args:
		image_a: The first image; any mode.
		image_b: The second image; any mode.

	Returns:
		A new 1-bit mode `"L"` image, sized to the larger input, containing
		only 0 and 1, with C = A XOR B.
	"""
	return _combine(image_a, image_b, lambda a, b: a ^ b)


def logic_sub(image_a: Image, image_b: Image) -> Image:
	"""A AND (NOT B): image_a's binarized white region minus image_b's.

	Computed as `A - B` where `A >= B`, `0` otherwise (the assignment's SUB
	operator, unlike plain subtraction); on binarized 0/1 inputs this is
	equivalent to "A's white region with B's white region removed".

	If the (binarized) images differ in size, the result takes the size of
	the bigger one (by pixel area) and the smaller image is centered on top
	of it; pixels outside the smaller image's footprint are treated as 0
	(black) for the subtraction.

	Args:
		image_a: The first image; any mode.
		image_b: The second image; any mode.

	Returns:
		A new 1-bit mode `"L"` image, sized to the larger input, containing
		only 0 and 1, with C = A - B (or 0).
	"""
	return _combine(image_a, image_b, lambda a, b: a - b if a >= b else 0)


def logic_not(image: Image) -> Image:
	"""Logical NOT of a binarized image.

	Args:
		image: The source image; any mode.

	Returns:
		A new 1-bit mode `"L"` image, same size as `image`, containing only 0
		and 1, with C = NOT A.
	"""
	binary = threshold_single(image, image.levels // 2)
	out = Image("L", binary.size, binary.bits_per_channel)
	max_value = binary.max_value
	width, height = binary.size
	for y in range(height):
		for x in range(width):
			out.putpixel(Coordinate(x, y), max_value - as_gray(binary.getpixel(Coordinate(x, y))))
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
	canvas_width, canvas_height = center_offsets(image_a, image_b).canvas_size
	return (
		f"Image A is {image_a.width}x{image_a.height} and Image B is {image_b.width}x{image_b.height}.\n\n"
		f"The smaller image will be centered on a canvas the size of the larger ({canvas_width}x{canvas_height}); "
		"pixels outside the smaller image's footprint are treated as 0 (black) before combining."
	)

def _combine(image_a: Image, image_b: Image, op: Callable[[int, int], int]) -> Image:
	"""Binarize both images, then apply a binary operator to each corresponding pair of pixels.

	If the images differ in size, the result takes the size of the bigger
	one (by pixel area) and the smaller image is centered on top of it:
	`op` is applied everywhere on the canvas, with whichever image doesn't
	cover a given pixel contributing 0 (black) there.

	Args:
		image_a: The first image; any mode.
		image_b: The second image; any mode.
		op: A function combining one binarized channel value from each image
			(each already 0 or 1) into an output value.

	Returns:
		A new 1-bit mode `"L"` image, sized to the larger input.
	"""
	binary_a = threshold_single(image_a, image_a.levels // 2)
	binary_b = threshold_single(image_b, image_b.levels // 2)

	layout = center_offsets(binary_a, binary_b)

	out = Image("L", layout.canvas_size, binary_a.bits_per_channel)
	width, height = layout.canvas_size
	for y in range(height):
		for x in range(width):
			a = as_gray(pixel_or(binary_a, Coordinate(x - layout.offset_a.x, y - layout.offset_a.y), 0))
			b = as_gray(pixel_or(binary_b, Coordinate(x - layout.offset_b.x, y - layout.offset_b.y), 0))
			out.putpixel(Coordinate(x, y), op(a, b))
	return out

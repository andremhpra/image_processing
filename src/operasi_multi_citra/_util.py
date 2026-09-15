"""Shared helpers for the operasi multi citra (multi-image operation) techniques."""

from typing import Optional, TypeVar, Union, overload

from imagelib.image import Coordinate, Image, PixelValue, Size

T = TypeVar("T")


def center_offsets(image_a: Image, image_b: Image) -> tuple[Size, Coordinate, Coordinate]:
	"""Work out the shared canvas and per-image offsets to center the smaller image on the larger.

	Args:
		image_a: The first image.
		image_b: The second image.

	Returns:
		A `(canvas_size, offset_a, offset_b)` tuple: `canvas_size` is whichever
		of the two images has more pixels (by area, ties going to `image_a`);
		`offset_a` and `offset_b` are the (x, y) offsets, within the canvas, of
		each image's top-left corner once centered (the larger image's own
		offset is always `(0, 0)`).
	"""
	if image_a.width * image_a.height >= image_b.width * image_b.height:
		offset_b = ((image_a.width - image_b.width) // 2, (image_a.height - image_b.height) // 2)
		return image_a.size, (0, 0), offset_b
	offset_a = ((image_b.width - image_a.width) // 2, (image_b.height - image_a.height) // 2)
	return image_b.size, offset_a, (0, 0)


@overload
def pixel_or(image: Image, xy: Coordinate) -> Optional[PixelValue]: ...
@overload
def pixel_or(image: Image, xy: Coordinate, alternative: T) -> Union[PixelValue, T]: ...
def pixel_or(image: Image, xy: Coordinate, alternative: Optional[T] = None) -> Union[PixelValue, Optional[T]]:
	"""Read a pixel, or an alternative value if `xy` falls outside `image`'s bounds.

	Args:
		image: The image to read from.
		xy: Pixel coordinate as an (x, y) tuple, possibly out of bounds.
		alternative: The value to return if `xy` is outside `image`; `None` if omitted.

	Returns:
		`image.getpixel(xy)`, or `alternative` if `xy` is outside `image`.
	"""
	x, y = xy
	width, height = image.size
	if 0 <= x < width and 0 <= y < height:
		return image.getpixel((x, y))
	return alternative

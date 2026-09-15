"""Shared helpers for the operasi multi citra (multi-image operation) techniques."""

from dataclasses import dataclass
from typing import Optional, TypeVar, Union, overload

from imagelib.image import Coordinate, Image, PixelValue, Size

T = TypeVar("T")


@dataclass(frozen=True)
class CenterLayout:
	"""Where a shared canvas and two images' top-left corners sit once the smaller is centered on the larger."""

	canvas_size: Size
	"""Whichever of the two images' sizes has more pixels by area."""
	offset_a: Coordinate
	"""`image_a`'s top-left corner within the canvas, once centered; `(0, 0)` if `image_a` is the larger one."""
	offset_b: Coordinate
	"""`image_b`'s top-left corner within the canvas, once centered; `(0, 0)` if `image_b` is the larger one."""


def center_offsets(image_a: Image, image_b: Image) -> CenterLayout:
	"""Work out the shared canvas and per-image offsets to center the smaller image on the larger.

	Args:
		image_a: The first image.
		image_b: The second image.

	Returns:
		The shared canvas size and each image's centering offset within it.
	"""
	if image_a.width * image_a.height >= image_b.width * image_b.height:
		offset_b = Coordinate((image_a.width - image_b.width) // 2, (image_a.height - image_b.height) // 2)
		return CenterLayout(image_a.size, Coordinate(0, 0), offset_b)
	offset_a = Coordinate((image_b.width - image_a.width) // 2, (image_b.height - image_a.height) // 2)
	return CenterLayout(image_b.size, offset_a, Coordinate(0, 0))


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
		return image.getpixel(xy)
	return alternative

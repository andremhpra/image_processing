"""A minimal, format-agnostic in-memory pixel grid."""

from pathlib import Path
from typing import Iterable, Literal, Union

Mode = Literal["L", "RGB"]
PixelValue = Union[int, tuple[int, int, int]]
Size = tuple[int, int]
Coordinate = tuple[int, int]

_BLANK: dict[Mode, PixelValue] = {"L": 0, "RGB": (0, 0, 0)}
MODE_BITS: dict[Mode, int] = {"L": 8, "RGB": 24}


class Image:
	"""Pixel grid held in memory. Enough of PIL's Image API to be a drop-in for simple use."""

	mode: Mode
	size: Size
	_pixels: list[PixelValue]  # flat, row-major backing store of pixel values

	def __init__(self, mode: Mode, size: Size) -> None:
		"""Create a blank image filled with the mode's background value.

		Args:
			mode: Pixel format, either `"L"` (8-bit grayscale) or `"RGB"` (24-bit truecolor).
			size: Image dimensions as an (width, height) tuple, in pixels.

		Raises:
			ValueError: If `mode` is not one of the supported modes.
		"""
		if mode not in _BLANK:
			raise ValueError(f"unsupported mode: {mode!r} (expected one of {sorted(_BLANK)})")
		self.mode: Mode = mode
		self.size: Size = size
		width, height = size
		self._pixels: list[PixelValue] = [_BLANK[mode]] * (width * height)

	@property
	def width(self) -> int:
		"""int: The image's width, in pixels."""
		return self.size[0]

	@property
	def height(self) -> int:
		"""int: The image's height, in pixels."""
		return self.size[1]

	@property
	def bits_per_pixel(self) -> int:
		"""int: The number of bits used to store one pixel in this image's mode."""
		return MODE_BITS[self.mode]

	def _index(self, xy: Coordinate) -> int:
		"""Convert an (x, y) coordinate into an offset into the flat pixel list.

		Args:
			xy: Pixel coordinate as an (x, y) tuple.

		Returns:
			The corresponding index into `self._pixels`.

		Raises:
			IndexError: If `xy` falls outside the image's bounds.
		"""
		x, y = xy
		width, height = self.size
		if not (0 <= x < width and 0 <= y < height):
			raise IndexError(f"pixel {xy} out of bounds for {width}x{height} image")
		return y * width + x

	def getpixel(self, xy: Coordinate) -> PixelValue:
		"""Read the value of a single pixel.

		Args:
			xy: Pixel coordinate as an (x, y) tuple.

		Returns:
			The pixel's value: an int for `"L"` images, an (R, G, B) tuple for `"RGB"` images.

		Raises:
			IndexError: If `xy` falls outside the image's bounds.
		"""
		return self._pixels[self._index(xy)]

	def putpixel(self, xy: Coordinate, value: PixelValue) -> None:
		"""Overwrite the value of a single pixel.

		Args:
			xy: Pixel coordinate as an (x, y) tuple.
			value: The new pixel value, matching this image's mode.

		Raises:
			IndexError: If `xy` falls outside the image's bounds.
		"""
		self._pixels[self._index(xy)] = value

	def putdata(self, values: Iterable[PixelValue]) -> None:
		"""Replace the whole pixel grid, in row-major (left-to-right, top-to-bottom) order.

		Args:
			values: Replacement pixel values, one per pixel, in row-major order.

		Raises:
			ValueError: If `values` doesn't contain exactly `width * height` items.
		"""
		values = list(values)
		if len(values) != len(self._pixels):
			raise ValueError(f"expected {len(self._pixels)} values, got {len(values)}")
		self._pixels = values

	def save(self, path: Union[str, Path]) -> None:
		"""Write this image to disk. Format is chosen by the path's file extension.

		Args:
			path: Destination file path; must end in `".bmp"` or `".png"`.

		Raises:
			ValueError: If the path's extension isn't a supported image format.
		"""
		ext = Path(path).suffix.lower()
		if ext == ".bmp":
			from imagelib import bmp

			bmp.write(self, path)
		elif ext == ".png":
			from imagelib import png

			png.write(self, path)
		else:
			raise ValueError(f"unsupported image format: {ext!r}")


def as_gray(value: PixelValue) -> int:
	"""Narrow a pixel value known (by its image's mode) to be a grayscale sample.

	Args:
		value: A pixel value read from an `"L"`-mode image.

	Returns:
		`value`, typed (and asserted) as a plain int.
	"""
	assert isinstance(value, int), f"expected a grayscale pixel value, got {value!r}"
	return value


def as_rgb(value: PixelValue) -> tuple[int, int, int]:
	"""Narrow a pixel value known (by its image's mode) to be an RGB triple.

	Args:
		value: A pixel value read from an `"RGB"`-mode image.

	Returns:
		`value`, typed (and asserted) as an (R, G, B) tuple.
	"""
	assert isinstance(value, tuple), f"expected an RGB pixel value, got {value!r}"
	return value

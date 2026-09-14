"""Minimal, dependency-free image I/O. Currently supports BMP."""

from pathlib import Path
from typing import Union

from imagelib import bmp, png
from imagelib.image import Image, Mode, Size, as_gray, as_rgb


def open(path: Union[str, Path]) -> Image:
	"""Read an image file into memory. Format is chosen by file extension.

	Args:
		path: Path to a `".bmp"` or `".png"` file.

	Returns:
		The decoded image.

	Raises:
		ValueError: If the path's extension isn't a supported image format.
	"""
	ext = Path(path).suffix.lower()
	if ext == ".bmp":
		return bmp.read(path)
	if ext == ".png":
		return png.read(path)
	raise ValueError(f"unsupported image format: {ext!r}")


def peek_size(path: Union[str, Path]) -> Size:
	"""Read an image file's dimensions without decoding its pixel data.

	Cheap even for a huge file, since it only reads the file's header. Useful
	to warn about a large image before `open`'s pure-Python, per-pixel
	decoder runs on it.

	Args:
		path: Path to a `".bmp"` or `".png"` file.

	Returns:
		The image's (width, height), in pixels.

	Raises:
		ValueError: If the path's extension isn't a supported image format.
	"""
	ext = Path(path).suffix.lower()
	if ext == ".bmp":
		return bmp.peek_size(path)
	if ext == ".png":
		return png.peek_size(path)
	raise ValueError(f"unsupported image format: {ext!r}")


def new(mode: Mode, size: Size) -> Image:
	"""Create a blank image, mirroring PIL's Image.new.

	Args:
		mode: Pixel format, either `"L"` (8-bit grayscale) or `"RGB"` (24-bit truecolor).
		size: Image dimensions as an (width, height) tuple, in pixels.

	Returns:
		A new image filled with the mode's background value (black).
	"""
	return Image(mode, size)


__all__ = ["Image", "open", "new", "peek_size", "as_gray", "as_rgb"]

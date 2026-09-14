"""Pure-Python PNG encode/decode: chunk framing and scanline filtering are
hand-written, with the actual DEFLATE compression delegated to the standard
library's `zlib` module (part of CPython itself, not a third-party package).

Writing always produces the simplest valid PNG: 8-bit, filter type 0 (None)
on every scanline, color type 0 (grayscale, mode `"L"`) or 2 (truecolor, mode
`"RGB"`). Reading is more permissive, since it has to cope with PNGs produced
by other tools: all five filter types, plus color types 0/2/3/4/6 (grayscale,
truecolor, palette, grayscale+alpha, truecolor+alpha) at 8 bits per channel.
Interlaced PNGs and bit depths other than 8 are not supported.
"""

import struct
import zlib
from pathlib import Path
from typing import Optional, Union

from imagelib.image import Image, Mode, PixelValue, Size, as_gray, as_rgb

_SIGNATURE = b"\x89PNG\r\n\x1a\n"

_GRAYSCALE = 0
_RGB = 2
_PALETTE = 3
_GRAYSCALE_ALPHA = 4
_RGBA = 6

_CHANNELS: dict[int, int] = {_GRAYSCALE: 1, _RGB: 3, _PALETTE: 1, _GRAYSCALE_ALPHA: 2, _RGBA: 4}


def peek_size(path: Union[str, Path]) -> Size:
	"""Read a PNG file's dimensions from its IHDR chunk, without decoding pixels.

	Only the first 24 bytes (signature + IHDR's length/type/width/height) are
	read, so this stays cheap even for a huge file.

	Args:
		path: Path to the PNG file.

	Returns:
		The image's (width, height), in pixels.

	Raises:
		ValueError: If the file isn't a PNG, or is missing its IHDR chunk.
	"""
	with open(path, "rb") as f:
		header = f.read(24)
	if header[:8] != _SIGNATURE:
		raise ValueError(f"{path}: not a PNG file")
	if header[12:16] != b"IHDR":
		raise ValueError(f"{path}: missing IHDR chunk")
	width, height = struct.unpack_from(">II", header, 16)
	return (width, height)


def write(image: Image, path: Union[str, Path]) -> None:
	"""Encode an image as a PNG (8-bit, filter type 0) and write it to disk.

	Args:
		image: The image to encode; mode `"L"` is written as grayscale, `"RGB"` as truecolor.
		path: Destination file path.
	"""
	width, height = image.size
	color_type = _GRAYSCALE if image.mode == "L" else _RGB

	ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)

	raw = bytearray()
	for y in range(height):
		raw.append(0)  # filter type 0 (None), simplest to produce correctly
		for x in range(width):
			value = image.getpixel((x, y))
			if image.mode == "L":
				raw.append(as_gray(value))
			else:
				raw.extend(as_rgb(value))

	body = bytearray(_SIGNATURE)
	body += _chunk(b"IHDR", ihdr)
	body += _chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
	body += _chunk(b"IEND", b"")
	Path(path).write_bytes(bytes(body))


def read(path: Union[str, Path]) -> Image:
	"""Decode a non-interlaced, 8-bit-per-channel PNG file into an in-memory image.

	Args:
		path: Path to the PNG file to read.

	Returns:
		The decoded image, in mode `"L"` (grayscale) or `"RGB"` (truecolor); any
		alpha channel is flattened onto a white background.

	Raises:
		ValueError: If the file isn't a PNG, is missing its IHDR chunk, is
			interlaced, or uses an unsupported bit depth or color type.
	"""
	data = Path(path).read_bytes()
	if data[:8] != _SIGNATURE:
		raise ValueError(f"{path}: not a PNG file")

	width: Optional[int] = None
	height: Optional[int] = None
	bit_depth: Optional[int] = None
	color_type: Optional[int] = None
	interlace: Optional[int] = None
	palette: list[tuple[int, int, int]] = []
	idat = bytearray()

	offset = 8
	while offset < len(data):
		(length,) = struct.unpack_from(">I", data, offset)
		tag = data[offset + 4 : offset + 8]
		chunk_data = data[offset + 8 : offset + 8 + length]
		offset += 8 + length + 4  # skip the trailing CRC, we trust our own reads

		if tag == b"IHDR":
			width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
				">IIBBBBB", chunk_data
			)
		elif tag == b"PLTE":
			palette = [(chunk_data[i], chunk_data[i + 1], chunk_data[i + 2]) for i in range(0, len(chunk_data), 3)]
		elif tag == b"IDAT":
			idat.extend(chunk_data)
		elif tag == b"IEND":
			break

	if width is None or height is None or bit_depth is None or color_type is None or interlace is None:
		raise ValueError(f"{path}: missing IHDR chunk")
	if bit_depth != 8:
		raise ValueError(f"{path}: unsupported PNG bit depth {bit_depth} (only 8-bit is supported)")
	if interlace:
		raise ValueError(f"{path}: interlaced PNGs are not supported, re-export without interlacing")
	if color_type not in _CHANNELS:
		raise ValueError(f"{path}: unsupported PNG color type {color_type}")

	channels = _CHANNELS[color_type]
	scanline_bytes = width * channels
	raw = zlib.decompress(bytes(idat))

	mode: Mode = "L" if color_type in (_GRAYSCALE, _GRAYSCALE_ALPHA) else "RGB"
	image = Image(mode, (width, height))

	previous = bytearray(scanline_bytes)
	pos = 0
	for y in range(height):
		filter_type = raw[pos]
		pos += 1
		line = bytearray(raw[pos : pos + scanline_bytes])
		pos += scanline_bytes
		_unfilter(filter_type, line, previous, channels)
		for x in range(width):
			image.putpixel((x, y), _decode_pixel(line, x, channels, color_type, palette))
		previous = line

	return image


def _chunk(tag: bytes, chunk_data: bytes) -> bytes:
	"""Frame a chunk's payload with its length prefix, type tag, and CRC32 trailer.

	Args:
		tag: The 4-byte chunk type, e.g. `b"IHDR"`.
		chunk_data: The chunk's raw payload bytes.

	Returns:
		The complete, ready-to-write chunk: length + tag + data + CRC32.
	"""
	return struct.pack(">I", len(chunk_data)) + tag + chunk_data + struct.pack(">I", zlib.crc32(tag + chunk_data))


def _unfilter(filter_type: int, line: bytearray, previous: bytearray, channels: int) -> None:
	"""Reverse the PNG scanline filter in place (see the PNG spec, section 9).

	Args:
		filter_type: The scanline's filter type byte (0-4: None/Sub/Up/Average/Paeth).
		line: The filtered scanline bytes; unfiltered in place.
		previous: The previous (already-unfiltered) scanline, for Up/Average/Paeth.
		channels: Number of color channels per pixel, used to find each byte's
			same-channel predecessor in the current row.

	Raises:
		ValueError: If `filter_type` isn't one of the five PNG filter types.
	"""
	for i in range(len(line)):
		a = line[i - channels] if i >= channels else 0
		b = previous[i]
		c = previous[i - channels] if i >= channels else 0
		if filter_type == 0:  # None
			pass
		elif filter_type == 1:  # Sub
			line[i] = (line[i] + a) & 0xFF
		elif filter_type == 2:  # Up
			line[i] = (line[i] + b) & 0xFF
		elif filter_type == 3:  # Average
			line[i] = (line[i] + (a + b) // 2) & 0xFF
		elif filter_type == 4:  # Paeth
			line[i] = (line[i] + _paeth_predictor(a, b, c)) & 0xFF
		else:
			raise ValueError(f"unsupported PNG scanline filter type {filter_type}")


def _paeth_predictor(a: int, b: int, c: int) -> int:
	"""Pick whichever of the left, above, or upper-left neighbor best predicts a byte.

	Implements the PNG spec's Paeth predictor function (section 9.4).

	Args:
		a: The byte immediately to the left (0 if none).
		b: The byte immediately above (0 if none).
		c: The byte above and to the left (0 if none).

	Returns:
		Whichever of `a`, `b`, or `c` is closest to `a + b - c`.
	"""
	p = a + b - c
	pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
	if pa <= pb and pa <= pc:
		return a
	if pb <= pc:
		return b
	return c


def _decode_pixel(
	line: bytearray, x: int, channels: int, color_type: int, palette: list[tuple[int, int, int]]
) -> PixelValue:
	"""Decode one pixel's samples from an unfiltered scanline into a `PixelValue`.

	Args:
		line: The unfiltered scanline bytes.
		x: The pixel's column index within the scanline.
		channels: Number of color channels per pixel for `color_type`.
		color_type: The PNG color type (0/2/3/4/6: grayscale/RGB/palette/
			grayscale+alpha/RGBA).
		palette: The PLTE chunk's colors, indexed by palette color type.

	Returns:
		An int for grayscale/palette pixels, or an (R, G, B) tuple for
		truecolor pixels; alpha channels are flattened onto white.

	Raises:
		ValueError: If `color_type` isn't a supported PNG color type.
	"""
	base = x * channels
	if color_type == _GRAYSCALE:
		return line[base]
	if color_type == _RGB:
		return (line[base], line[base + 1], line[base + 2])
	if color_type == _PALETTE:
		return palette[line[base]]
	if color_type == _GRAYSCALE_ALPHA:
		return _over_white(line[base], line[base + 1])
	if color_type == _RGBA:
		alpha = line[base + 3]
		return (
			_over_white(line[base], alpha),
			_over_white(line[base + 1], alpha),
			_over_white(line[base + 2], alpha),
		)
	raise ValueError(f"unsupported PNG color type {color_type}")


def _over_white(value: int, alpha: int) -> int:
	"""Flatten a semi-transparent sample onto a white background.

	There's no alpha channel to preserve it in, since `imagelib`'s Image only
	models opaque `"L"`/`"RGB"` pixels.

	Args:
		value: The sample's color value (0-255).
		alpha: The sample's alpha value (0-255, 0 fully transparent).

	Returns:
		The color value as it would appear composited over white.
	"""
	return round(value * alpha / 255 + 255 * (1 - alpha / 255))

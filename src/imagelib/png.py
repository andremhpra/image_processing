"""Pure-Python PNG encode/decode: chunk framing and scanline filtering are
hand-written, with the actual DEFLATE compression delegated to the standard
library's `zlib` module (part of CPython itself, not a third-party package).

Writing emits a single IDAT, filter type 0 (None) on every scanline, color
type 0 (grayscale, mode `"L"`) or 2 (truecolor, mode `"RGB"`), at the source
image's own bit depth (1/2/4/8/16 for `"L"`, 8/16 for `"RGB"`). Reading is
more permissive, since it has to cope with PNGs produced by other tools: all
five filter types, every bit depth each color type allows, and color types
0/2/3/4/6 (grayscale, truecolor, palette, grayscale+alpha, truecolor+alpha).
Interlaced PNGs are not supported.
"""

import struct
import zlib
from pathlib import Path
from typing import Optional, Union

from imagelib.image import RGB, Coordinate, Image, Mode, PixelValue, Size, as_gray, as_rgb

_SIGNATURE = b"\x89PNG\r\n\x1a\n"

_GRAYSCALE = 0
_RGB = 2
_PALETTE = 3
_GRAYSCALE_ALPHA = 4
_RGBA = 6

_CHANNELS: dict[int, int] = {_GRAYSCALE: 1, _RGB: 3, _PALETTE: 1, _GRAYSCALE_ALPHA: 2, _RGBA: 4}
_ALLOWED_DEPTHS: dict[int, tuple[int, ...]] = {
	_GRAYSCALE: (1, 2, 4, 8, 16),
	_RGB: (8, 16),
	_PALETTE: (1, 2, 4, 8),
	_GRAYSCALE_ALPHA: (8, 16),
	_RGBA: (8, 16),
}


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
	return Size(width, height)


def write(image: Image, path: Union[str, Path]) -> None:
	"""Encode an image as a PNG (filter type 0) and write it to disk.

	Args:
		image: The image to encode, at its own bit depth; mode `"L"` is
			written as grayscale, `"RGB"` as truecolor.
		path: Destination file path.
	"""
	width, height = image.size
	color_type = _GRAYSCALE if image.mode == "L" else _RGB
	bit_depth = image.bits_per_channel

	ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)

	raw = bytearray()
	for y in range(height):
		raw.append(0)  # filter type 0 (None), simplest to produce correctly
		samples: list[int] = []
		for x in range(width):
			value = image.getpixel(Coordinate(x, y))
			if image.mode == "L":
				samples.append(as_gray(value))
			else:
				samples.extend(as_rgb(value))
		raw += _pack_samples(samples, bit_depth)

	body = bytearray(_SIGNATURE)
	body += _chunk(b"IHDR", ihdr)
	body += _chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
	body += _chunk(b"IEND", b"")
	Path(path).write_bytes(bytes(body))


def read(path: Union[str, Path]) -> Image:
	"""Decode a non-interlaced PNG file into an in-memory image.

	Args:
		path: Path to the PNG file to read.

	Returns:
		The decoded image, in mode `"L"` (grayscale) or `"RGB"` (truecolor),
		at whichever bit depth the file itself uses (palette-indexed files
		decode to 8-bit `"RGB"`, since a palette entry is always an 8-bit
		RGB triple regardless of the index's own bit depth); any alpha
		channel is flattened onto a white background.

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
	palette: list[RGB] = []
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
			palette = [RGB(chunk_data[i], chunk_data[i + 1], chunk_data[i + 2]) for i in range(0, len(chunk_data), 3)]
		elif tag == b"IDAT":
			idat.extend(chunk_data)
		elif tag == b"IEND":
			break

	if width is None or height is None or bit_depth is None or color_type is None or interlace is None:
		raise ValueError(f"{path}: missing IHDR chunk")
	if interlace:
		raise ValueError(f"{path}: interlaced PNGs are not supported, re-export without interlacing")
	if bit_depth not in _ALLOWED_DEPTHS.get(color_type, ()):
		raise ValueError(f"{path}: unsupported bit depth {bit_depth} for PNG color type {color_type}")

	channels = _CHANNELS[color_type]
	scanline_bytes = (width * channels * bit_depth + 7) // 8
	bpp = max(1, (channels * bit_depth + 7) // 8)
	raw = zlib.decompress(bytes(idat))

	mode: Mode = "L" if color_type in (_GRAYSCALE, _GRAYSCALE_ALPHA) else "RGB"
	out_bit_depth = 8 if color_type == _PALETTE else bit_depth
	image = Image(mode, Size(width, height), out_bit_depth)
	max_value = image.max_value

	previous = bytearray(scanline_bytes)
	pos = 0
	for y in range(height):
		filter_type = raw[pos]
		pos += 1
		line = bytearray(raw[pos : pos + scanline_bytes])
		pos += scanline_bytes
		_unfilter(filter_type, line, previous, bpp)
		row_samples = _unpack_samples(bytes(line), bit_depth, channels, width)
		for x in range(width):
			image.putpixel(Coordinate(x, y), _decode_pixel(row_samples[x], color_type, palette, max_value))
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


def _unfilter(filter_type: int, line: bytearray, previous: bytearray, bpp: int) -> None:
	"""Reverse the PNG scanline filter in place (see the PNG spec, section 9).

	Args:
		filter_type: The scanline's filter type byte (0-4: None/Sub/Up/Average/Paeth).
		line: The filtered scanline bytes; unfiltered in place.
		previous: The previous (already-unfiltered) scanline, for Up/Average/Paeth.
		bpp: Bytes per complete pixel (at least 1), used to find each byte's
			same-channel predecessor in the current row; for bit depths under
			8 this is 1, since several pixels then share a byte.

	Raises:
		ValueError: If `filter_type` isn't one of the five PNG filter types.
	"""
	for i in range(len(line)):
		a = line[i - bpp] if i >= bpp else 0
		b = previous[i]
		c = previous[i - bpp] if i >= bpp else 0
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


def _unpack_samples(line: bytes, bit_depth: int, channels: int, width: int) -> list[list[int]]:
	"""Split one already-unfiltered scanline into each pixel's raw channel samples.

	Args:
		line: The unfiltered scanline bytes.
		bit_depth: Bits per sample (1, 2, 4, 8, or 16).
		channels: Number of channel samples per pixel, for this color type.
		width: The scanline's pixel count.

	Returns:
		A `width`-long list, each entry a `channels`-long list of raw sample
		ints (0..`2**bit_depth - 1`), in the pixel's channel order.
	"""
	count = width * channels
	if bit_depth == 8:
		flat = list(line[:count])
	elif bit_depth == 16:
		flat = [(line[2 * i] << 8) | line[2 * i + 1] for i in range(count)]
	else:
		mask = (1 << bit_depth) - 1
		per_byte = 8 // bit_depth
		flat = []
		for i in range(count):
			byte = line[i // per_byte]
			shift = 8 - bit_depth - (i % per_byte) * bit_depth
			flat.append((byte >> shift) & mask)
	return [flat[i * channels : (i + 1) * channels] for i in range(width)]


def _pack_samples(values: list[int], bit_depth: int) -> bytes:
	"""Pack a flat list of channel samples into one scanline's worth of bytes.

	Args:
		values: Sample values (0..`2**bit_depth - 1`), in row-major, per-pixel
			channel order.
		bit_depth: Bits per sample (1, 2, 4, 8, or 16).

	Returns:
		The packed scanline bytes: one byte per sample at 8-bit, two
		big-endian bytes per sample at 16-bit, or several samples packed
		MSB-first per byte (padded with zero bits at the row's end) below 8-bit.
	"""
	if bit_depth == 8:
		return bytes(values)
	if bit_depth == 16:
		out = bytearray()
		for v in values:
			out.append((v >> 8) & 0xFF)
			out.append(v & 0xFF)
		return bytes(out)

	per_byte = 8 // bit_depth
	out = bytearray()
	current = 0
	filled = 0
	for v in values:
		current = (current << bit_depth) | (v & ((1 << bit_depth) - 1))
		filled += 1
		if filled == per_byte:
			out.append(current)
			current = 0
			filled = 0
	if filled:
		current <<= (per_byte - filled) * bit_depth
		out.append(current)
	return bytes(out)


def _decode_pixel(sample: list[int], color_type: int, palette: list[RGB], max_value: int) -> PixelValue:
	"""Decode one pixel's raw channel samples into a `PixelValue`.

	Args:
		sample: The pixel's raw channel samples, in PNG channel order.
		color_type: The PNG color type (0/2/3/4/6: grayscale/RGB/palette/
			grayscale+alpha/RGBA).
		palette: The PLTE chunk's colors, for `color_type` 3.
		max_value: The output image's max channel value, used to flatten alpha.

	Returns:
		An int for grayscale/palette pixels, or an (R, G, B) tuple for
		truecolor pixels; alpha channels are flattened onto white.

	Raises:
		ValueError: If `color_type` isn't a supported PNG color type.
	"""
	if color_type == _GRAYSCALE:
		return sample[0]
	if color_type == _RGB:
		return RGB(sample[0], sample[1], sample[2])
	if color_type == _PALETTE:
		return palette[sample[0]]
	if color_type == _GRAYSCALE_ALPHA:
		return _over_white(sample[0], sample[1], max_value)
	if color_type == _RGBA:
		alpha = sample[3]
		return RGB(
			_over_white(sample[0], alpha, max_value),
			_over_white(sample[1], alpha, max_value),
			_over_white(sample[2], alpha, max_value),
		)
	raise ValueError(f"unsupported PNG color type {color_type}")


def _over_white(value: int, alpha: int, max_value: int) -> int:
	"""Flatten a semi-transparent sample onto a white background.

	There's no alpha channel to preserve it in, since `imagelib`'s Image only
	models opaque `"L"`/`"RGB"` pixels.

	Args:
		value: The sample's color value (0..`max_value`).
		alpha: The sample's alpha value (0..`max_value`, 0 fully transparent).
		max_value: The largest value either sample can take.

	Returns:
		The color value as it would appear composited over white.
	"""
	return round(value * alpha / max_value + max_value * (1 - alpha / max_value))

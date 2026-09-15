"""Pure-Python BMP encode/decode (uncompressed BITMAPINFOHEADER format).

Supports the color depths BMP's palette format can actually express:
- 1-bit, 4-bit, or 8-bit, palette-indexed grayscale (mode `"L"`)
- 24-bit, RGB truecolor (mode `"RGB"`)

There's no standard BMP encoding for 16-bit-per-channel images (`"L"` at
16 bits, or `"RGB"` at 16 bits per channel), so writing one raises `ValueError`
- save as PNG instead, which supports both natively.
"""

import struct
from pathlib import Path
from typing import Union

from imagelib.image import RGB, Coordinate, Image, Mode, Size, as_gray, as_rgb

FILE_HEADER = "<2sIHHI"       # signature, file size, reserved x2, pixel data offset
INFO_HEADER = "<IiiHHIIiiII"  # BITMAPINFOHEADER (40 bytes)

_L_BITCOUNTS = (1, 4, 8)
BITCOUNT_MODE: dict[int, Mode] = {1: "L", 4: "L", 8: "L", 24: "RGB"}
BITCOUNT_BITS_PER_CHANNEL: dict[int, int] = {1: 1, 4: 4, 8: 8, 24: 8}


def peek_size(path: Union[str, Path]) -> Size:
	"""Read a BMP file's dimensions without decoding any pixel data.

	Only the first 26 bytes (file header + the info header's size fields)
	are read, so this stays cheap even for a huge file.

	Args:
		path: Path to the BMP file.

	Returns:
		The image's (width, height), in pixels.

	Raises:
		ValueError: If the file isn't a BMP.
	"""
	with open(path, "rb") as f:
		header = f.read(26)
	if header[:2] != b"BM":
		raise ValueError(f"{path}: not a BMP file")
	width, raw_height = struct.unpack_from("<ii", header, 18)
	return Size(width, abs(raw_height))


def read(path: Union[str, Path]) -> Image:
	"""Decode an uncompressed 1/4/8-bit or 24-bit BMP file into an in-memory image.

	Args:
		path: Path to the BMP file to read.

	Returns:
		The decoded image, in mode `"L"` (1/4/8-bit) or `"RGB"` (24-bit).

	Raises:
		ValueError: If the file isn't a BMP, or uses an unsupported color depth.
	"""
	data = Path(path).read_bytes()

	signature, _file_size, _reserved1, _reserved2, pixel_offset = struct.unpack_from(FILE_HEADER, data, 0)
	if signature != b"BM":
		raise ValueError(f"{path}: not a BMP file")

	(header_size, width, raw_height, _planes, bitcount, _compression,
	 _image_size, _xppm, _yppm, colors_used, _colors_important) = struct.unpack_from(INFO_HEADER, data, 14)

	if bitcount not in BITCOUNT_MODE:
		raise ValueError(f"{path}: unsupported color depth ({bitcount}-bit)")

	top_down = raw_height < 0
	height = abs(raw_height)

	palette: list[RGB] = []
	if bitcount in _L_BITCOUNTS:
		palette_offset = 14 + header_size
		num_colors = colors_used if colors_used else (1 << bitcount)
		for i in range(num_colors):
			b, g, r, _reserved = struct.unpack_from("<4B", data, palette_offset + i * 4)
			palette.append(RGB(r, g, b))

	row_size = _row_size(bitcount, width)

	image = Image(BITCOUNT_MODE[bitcount], Size(width, height), BITCOUNT_BITS_PER_CHANNEL[bitcount])
	max_value = image.max_value
	for file_row in range(height):
		y = file_row if top_down else height - 1 - file_row
		row_offset = pixel_offset + file_row * row_size
		if bitcount == 24:
			for x in range(width):
				b, g, r = struct.unpack_from("<3B", data, row_offset + x * 3)
				image.putpixel(Coordinate(x, y), RGB(r, g, b))
		else:
			indices = _unpack_indices(data[row_offset : row_offset + row_size], bitcount, width)
			for x in range(width):
				r, g, _b = palette[indices[x]]
				image.putpixel(Coordinate(x, y), round(r * max_value / 255))

	return image


def write(image: Image, path: Union[str, Path]) -> None:
	"""Encode an image as an uncompressed BMP and write it to disk.

	Grayscale (`"L"`) images are written 1/4/8-bit (matching `image`'s own
	depth) with a linear gray palette; `"RGB"` images are written 24-bit
	truecolor.

	Args:
		image: The image to encode; `"L"` at 1, 4, or 8 bits per channel, or
			`"RGB"` at 8 bits per channel.
		path: Destination file path.

	Raises:
		ValueError: If `image`'s mode/bit-depth combination has no BMP
			encoding (i.e. isn't `"L"` at 1/4/8 bits, or `"RGB"` at 8 bits).
	"""
	if image.mode == "L" and image.bits_per_channel in _L_BITCOUNTS:
		bitcount = image.bits_per_channel
	elif image.mode == "RGB" and image.bits_per_channel == 8:
		bitcount = 24
	else:
		raise ValueError(
			f"cannot write {image.bits_per_channel}-bit-per-channel mode {image.mode!r} as BMP "
			"(BMP only supports 1/4/8-bit grayscale or 8-bit-per-channel RGB)"
		)
	width, height = image.size
	row_size = _row_size(bitcount, width)

	if bitcount == 24:
		palette = b""
	else:
		max_value = image.max_value
		palette = b"".join(
			struct.pack("<4B", *(3 * (round(i * 255 / max_value),) + (0,))) for i in range(1 << bitcount)
		)
	pixel_offset = 14 + 40 + len(palette)
	pixel_data_size = row_size * height
	file_size = pixel_offset + pixel_data_size

	file_header = struct.pack(FILE_HEADER, b"BM", file_size, 0, 0, pixel_offset)
	info_header = struct.pack(
		INFO_HEADER,
		40, width, height, 1, bitcount, 0, pixel_data_size, 2835, 2835,
		(1 << bitcount) if bitcount != 24 else 0, 0,
	)

	rows = bytearray()
	for file_row in range(height):
		y = height - 1 - file_row  # BMP stores rows bottom-up
		if bitcount == 24:
			row = bytearray()
			for x in range(width):
				r, g, b = as_rgb(image.getpixel(Coordinate(x, y)))
				row += bytes((b, g, r))
		else:
			indices = [as_gray(image.getpixel(Coordinate(x, y))) for x in range(width)]
			row = bytearray(_pack_indices(indices, bitcount))
		row += b"\x00" * (row_size - len(row))
		rows += row

	Path(path).write_bytes(file_header + info_header + palette + bytes(rows))


def _row_size(bitcount: int, width: int) -> int:
	"""Compute a BMP scanline's byte length, padded up to a multiple of 4 bytes.

	Args:
		bitcount: Bits per pixel (1, 4, 8, or 24).
		width: Image width, in pixels.

	Returns:
		The padded row size, in bytes.
	"""
	return ((bitcount * width + 31) // 32) * 4


def _unpack_indices(row: bytes, bitcount: int, width: int) -> list[int]:
	"""Split one (already row-padded) BMP scanline into its palette indices.

	Args:
		row: The scanline's raw bytes, at least `_row_size(bitcount, width)` long.
		bitcount: Bits per palette index (1, 4, or 8).
		width: The scanline's pixel count.

	Returns:
		A `width`-long list of palette indices (0..`2**bitcount - 1`).
	"""
	if bitcount == 8:
		return list(row[:width])
	mask = (1 << bitcount) - 1
	per_byte = 8 // bitcount
	indices = []
	for x in range(width):
		byte = row[x // per_byte]
		shift = 8 - bitcount - (x % per_byte) * bitcount
		indices.append((byte >> shift) & mask)
	return indices


def _pack_indices(indices: list[int], bitcount: int) -> bytes:
	"""Pack one scanline's palette indices into bytes (unpadded).

	Args:
		indices: Palette indices (0..`2**bitcount - 1`), one per pixel.
		bitcount: Bits per palette index (1, 4, or 8).

	Returns:
		The packed scanline bytes, several indices MSB-first per byte below
		8-bit (padded with zero bits at the row's end); the caller still pads
		the result up to `_row_size`.
	"""
	if bitcount == 8:
		return bytes(indices)
	per_byte = 8 // bitcount
	out = bytearray()
	current = 0
	filled = 0
	for v in indices:
		current = (current << bitcount) | (v & ((1 << bitcount) - 1))
		filled += 1
		if filled == per_byte:
			out.append(current)
			current = 0
			filled = 0
	if filled:
		current <<= (per_byte - filled) * bitcount
		out.append(current)
	return bytes(out)

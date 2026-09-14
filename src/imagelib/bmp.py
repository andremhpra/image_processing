"""Pure-Python BMP encode/decode (uncompressed BITMAPINFOHEADER format).

Supports the two color depths this project cares about:
- 8-bit, palette-indexed grayscale (mode `"L"`)
- 24-bit, RGB truecolor (mode `"RGB"`)
"""

import struct
from pathlib import Path
from typing import Union

from imagelib.image import Image, Mode, Size, as_gray, as_rgb

FILE_HEADER = "<2sIHHI"       # signature, file size, reserved x2, pixel data offset
INFO_HEADER = "<IiiHHIIiiII"  # BITMAPINFOHEADER (40 bytes)

MODE_BITCOUNT: dict[Mode, int] = {"L": 8, "RGB": 24}
BITCOUNT_MODE: dict[int, Mode] = {v: k for k, v in MODE_BITCOUNT.items()}


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
	return (width, abs(raw_height))


def read(path: Union[str, Path]) -> Image:
	"""Decode an uncompressed 8-bit or 24-bit BMP file into an in-memory image.

	Args:
		path: Path to the BMP file to read.

	Returns:
		The decoded image, in mode `"L"` (8-bit) or `"RGB"` (24-bit).

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

	palette: list[tuple[int, int, int]] = []
	if bitcount == 8:
		palette_offset = 14 + header_size
		num_colors = colors_used if colors_used else 256
		for i in range(num_colors):
			b, g, r, _reserved = struct.unpack_from("<4B", data, palette_offset + i * 4)
			palette.append((r, g, b))

	row_size = _row_size(bitcount, width)

	image = Image(BITCOUNT_MODE[bitcount], (width, height))
	for file_row in range(height):
		y = file_row if top_down else height - 1 - file_row
		row_offset = pixel_offset + file_row * row_size
		for x in range(width):
			if bitcount == 24:
				b, g, r = struct.unpack_from("<3B", data, row_offset + x * 3)
				image.putpixel((x, y), (r, g, b))
			else:
				index = data[row_offset + x]
				r, g, _b = palette[index]
				image.putpixel((x, y), r)

	return image


def write(image: Image, path: Union[str, Path]) -> None:
	"""Encode an image as an uncompressed BMP and write it to disk.

	Grayscale (`"L"`) images are written 8-bit with an identity (gray) palette;
	`"RGB"` images are written 24-bit truecolor.

	Args:
		image: The image to encode.
		path: Destination file path.

	Raises:
		ValueError: If `image.mode` has no BMP encoding (i.e. isn't `"L"` or `"RGB"`).
	"""
	if image.mode not in MODE_BITCOUNT:
		raise ValueError(f"cannot write mode {image.mode!r} as BMP")
	bitcount = MODE_BITCOUNT[image.mode]
	width, height = image.size
	row_size = _row_size(bitcount, width)

	palette = b"".join(struct.pack("<4B", i, i, i, 0) for i in range(256)) if bitcount == 8 else b""
	pixel_offset = 14 + 40 + len(palette)
	pixel_data_size = row_size * height
	file_size = pixel_offset + pixel_data_size

	file_header = struct.pack(FILE_HEADER, b"BM", file_size, 0, 0, pixel_offset)
	info_header = struct.pack(
		INFO_HEADER,
		40, width, height, 1, bitcount, 0, pixel_data_size, 2835, 2835,
		256 if bitcount == 8 else 0, 0,
	)

	rows = bytearray()
	for file_row in range(height):
		y = height - 1 - file_row  # BMP stores rows bottom-up
		row = bytearray()
		for x in range(width):
			value = image.getpixel((x, y))
			if bitcount == 8:
				row.append(as_gray(value))
			else:
				r, g, b = as_rgb(value)
				row += bytes((b, g, r))
		row += b"\x00" * (row_size - len(row))
		rows += row

	Path(path).write_bytes(file_header + info_header + palette + bytes(rows))


def _row_size(bitcount: int, width: int) -> int:
	"""Compute a BMP scanline's byte length, padded up to a multiple of 4 bytes.

	Args:
		bitcount: Bits per pixel (8 or 24).
		width: Image width, in pixels.

	Returns:
		The padded row size, in bytes.
	"""
	return ((bitcount * width + 31) // 32) * 4

"""Penskalaan (scaling): zoom in (factor > 1) or zoom out (factor < 1) an image."""

from imagelib import Image


def scale(image: Image, sh: float, sv: float) -> Image:
	"""x' = Sh*x, y' = Sv*y; the new size is w' = Sh*w, h' = Sv*h.

	Forward-mapping every source pixel to x'/y' would leave gaps in the
	output whenever Sh/Sv aren't whole numbers, so this instead walks the
	*destination* image and pulls the nearest source pixel for each spot.
	For a whole-number zoom-in factor that reduces to exactly the expected
	result: every source pixel copied into an Sh x Sv block.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		sh: Horizontal scale factor (> 1 zooms in, < 1 zooms out).
		sv: Vertical scale factor (> 1 zooms in, < 1 zooms out).

	Returns:
		A new image, same mode as `image`, resized to (round(w*sh), round(h*sv)).
	"""
	width, height = image.size
	new_width = max(round(width * sh), 1)
	new_height = max(round(height * sv), 1)

	out = Image(image.mode, (new_width, new_height), image.bits_per_channel)
	for ny in range(new_height):
		source_y = min(height - 1, int(ny / sv))
		for nx in range(new_width):
			source_x = min(width - 1, int(nx / sh))
			out.putpixel((nx, ny), image.getpixel((source_x, source_y)))
	return out

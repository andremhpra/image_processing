# Given a grayscale/rgb image (max 100*100 pixels resolution), report:
# - Color depth in bits
# - Size resolution
# - Each pixel's value as `(x, y) = <values>`

from imagelib.image import Image


def describe_image(image: Image) -> str:
	"""Return an image's color depth, resolution, and per-pixel values as text.

	Args:
		image: The image to describe.

	Returns:
		A multi-line report: color depth, resolution, then one
		"(x, y) = <value>" line per pixel in row-major order.
	"""
	width, height = image.size
	lines = [
		f"Color depth: {image.bits_per_pixel} bits",
		f"Size resolution: {width} x {height}",
	]
	for y in range(height):
		for x in range(width):
			lines.append(f"({x}, {y}) = {image.getpixel((x, y))}")
	return "\n".join(lines)

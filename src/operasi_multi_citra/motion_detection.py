"""Deteksi Gerakan (motion detection): C = |A - B| between two successive frames."""

from imagelib.image import Image, as_gray, as_rgb


def detect_motion(image_a: Image, image_b: Image) -> Image:
	"""Unmoved pixels go to 0 (black); pixels that changed between the two frames stand out.

	Args:
		image_a: The first (earlier) frame; same size and mode as `image_b`.
		image_b: The second (later) frame; same size and mode as `image_a`.

	Returns:
		A new image, same mode and size as the inputs, with C = |A - B|.

	Raises:
		ValueError: If `image_a` and `image_b` differ in size or mode.
	"""
	if image_a.size != image_b.size:
		raise ValueError(f"images must be the same size, got {image_a.size} and {image_b.size}")
	if image_a.mode != image_b.mode:
		raise ValueError(f"images must be the same mode, got {image_a.mode!r} and {image_b.mode!r}")

	out = Image(image_a.mode, image_a.size)
	width, height = image_a.size
	for y in range(height):
		for x in range(width):
			a = image_a.getpixel((x, y))
			b = image_b.getpixel((x, y))
			if image_a.mode == "L":
				out.putpixel((x, y), abs(as_gray(a) - as_gray(b)))
			else:
				ar, ag, ab = as_rgb(a)
				br, bg, bb = as_rgb(b)
				out.putpixel((x, y), (abs(ar - br), abs(ag - bg), abs(ab - bb)))
	return out

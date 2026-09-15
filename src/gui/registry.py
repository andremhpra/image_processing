"""Every image operation the GUI can run, described declaratively.

The GUI never hardcodes "brightness needs a C" or "blending needs two
images", it reads `num_inputs` to decide how many `"Load..."` slots to draw
and `params` to decide which fields to show, for whichever `Operation` is
selected. That's what makes it extensible: a technique that needs two (or
more) images, like the blending/overlay example below, is a plain registry
entry, not a special case wired into the UI.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, Union

from imagelib.image import Image
from operasi_geometri import (
	crop,
	flip_combined,
	flip_horizontal,
	flip_vertical,
	rotate_90_cw,
	rotate_180_cw,
	rotate_free,
	scale,
)
from operasi_global import equalize_histogram
from operasi_multi_citra import (
	blend,
	describe_blend_size_mismatch,
	describe_logic_size_mismatch,
	describe_motion_size_mismatch,
	detect_motion,
	logic_and,
	logic_not,
	logic_or,
	logic_sub,
	logic_xor,
)
from operasi_titik import (
	adjust_brightness,
	enhance_contrast,
	negate,
	threshold_double,
	threshold_single,
	to_grayscale_average,
	to_grayscale_weighted,
)

ParamKind = str  # "int" | "float" | "choice"


@dataclass(frozen=True)
class Param:
	"""One configurable input field for an `Operation`."""

	name: str
	"""The parameter's key; also the keyword argument name passed to `run`."""
	label: str
	"""The human-readable label shown next to the input field."""
	kind: ParamKind
	"""The input widget kind: `"int"`, `"float"`, or `"choice"`."""
	default: Union[int, float, str, Callable[[Image], Union[int, float, str]]]
	"""The value the input field is pre-filled with, or - for a default that
	depends on the loaded image, like a threshold set relative to the
	image's own bit depth rather than a fixed 0-255 assumption - a callable
	that computes it from the operation's first input image. Resolved
	against that image once it's loaded (and re-resolved whenever it's
	reloaded); before that, against a default 8-bit image."""
	choices: Sequence[str] = field(default_factory=tuple)
	"""The selectable values, used only when `kind` is `"choice"`."""


@dataclass(frozen=True)
class Operation:
	"""One image operation the GUI can run, and everything needed to drive its UI."""

	key: str
	"""Stable identifier for this operation, used to look it up in `OPERATIONS`."""
	label: str
	"""The human-readable name (with formula) shown in the operation dropdown."""
	category: str
	"""The technique category this operation belongs to, e.g. "Operasi Titik"."""
	num_inputs: int
	"""How many input image slots the GUI should draw (1 or 2)."""
	run: Callable[..., Image]
	"""The function to call with the input image(s) and collected params."""
	params: Sequence[Param] = field(default_factory=tuple)
	"""The extra (non-image) parameters this operation takes, if any."""
	describe_size_mismatch: Optional[Callable[[Image, Image], Optional[str]]] = None
	"""For a 2-input operation that tolerates differently sized inputs: given
	the two loaded images, returns a warning message describing how they'll
	be reconciled, or None if they're already the same size. The GUI shows
	this (if non-None) before running. Operations that require same-sized
	inputs leave this unset."""


_FLIPS: dict[str, Callable[[Image], Image]] = {
	"horizontal": flip_horizontal,
	"vertical": flip_vertical,
	"combined": flip_combined,
}


def _flip(image: Image, direction: str) -> Image:
	"""Dispatch to the flip function named by `direction`.

	Args:
		image: The source image; mode `"L"` or `"RGB"`.
		direction: One of `"horizontal"`, `"vertical"`, or `"combined"`.

	Returns:
		The flipped image, as produced by the matching `flip_*` function.

	Raises:
		KeyError: If `direction` isn't one of the supported flip directions.
	"""
	return _FLIPS[direction](image)


def _blend(image_a: Image, image_b: Image, wa: float) -> Image:
	"""Adapt `blend` to the GUI's param name: `blend`'s own parameter is named
	`weight_a`, but the GUI's param key is `"wa"`.

	Args:
		image_a: The first image; same size and mode as `image_b`.
		image_b: The second image; same size and mode as `image_a`.
		wa: `image_a`'s weight, forwarded to `blend` as `weight_a`.

	Returns:
		The blended image, as produced by `blend`.
	"""
	return blend(image_a, image_b, wa)


OPERATIONS: list[Operation] = [
	Operation(
		"brightness",
		"Brightness modification  (Ko = Ki + C)",
		"Operasi Titik",
		1,
		adjust_brightness,
		[Param("c", "C (offset)", "int", 30)],
	),
	Operation(
		"contrast",
		"Contrast enhancement  (Ko = G*(Ki-P)+P)",
		"Operasi Titik",
		1,
		enhance_contrast,
		[Param("gain", "Gain (G)", "float", 1.5), Param("pivot", "Pivot (P)", "int", lambda image: image.levels // 2)],
	),
	Operation(
		"negation",
		"Negation  (Ko = Kmax - Ki)",
		"Operasi Titik",
		1,
		negate,
	),
	Operation(
		"grayscale_average",
		"Grayscale conversion, average",
		"Operasi Titik",
		1,
		to_grayscale_average,
	),
	Operation(
		"grayscale_weighted",
		"Grayscale conversion, NTSC weighted",
		"Operasi Titik",
		1,
		to_grayscale_weighted,
	),
	Operation(
		"threshold_single",
		"Thresholding, single (binary)",
		"Operasi Titik",
		1,
		threshold_single,
		[Param("ambang", "Ambang (threshold)", "int", lambda image: image.levels // 2)],
	),
	Operation(
		"threshold_double",
		"Thresholding, double (band)",
		"Operasi Titik",
		1,
		threshold_double,
		[
			Param("ambang_bawah", "Ambang bawah", "int", lambda image: image.levels // 4),
			Param("ambang_atas", "Ambang atas", "int", lambda image: image.levels * 3 // 4),
		],
	),
	Operation(
		"flip",
		"Flipping",
		"Operasi Geometri",
		1,
		_flip,
		[Param("direction", "Direction", "choice", "horizontal", ("horizontal", "vertical", "combined"))],
	),
	Operation(
		"rotate_90",
		"Rotate 90 deg clockwise",
		"Operasi Geometri",
		1,
		rotate_90_cw,
	),
	Operation(
		"rotate_180",
		"Rotate 180 deg",
		"Operasi Geometri",
		1,
		rotate_180_cw,
	),
	Operation(
		"rotate_free",
		"Rotate, free angle",
		"Operasi Geometri",
		1,
		rotate_free,
		[Param("degrees", "Degrees (CCW)", "float", 25)],
	),
	Operation(
		"crop",
		"Cropping",
		"Operasi Geometri",
		1,
		crop,
		[
			Param("left", "Left", "int", 0),
			Param("top", "Top", "int", 0),
			Param("right", "Right", "int", 4),
			Param("bottom", "Bottom", "int", 4),
		],
	),
	Operation(
		"scale",
		"Scaling (zoom in/out)",
		"Operasi Geometri",
		1,
		scale,
		[Param("sh", "Horizontal factor", "float", 2.0), Param("sv", "Vertical factor", "float", 2.0)],
	),
	Operation(
		"blend",
		"Blending / overlay  (C = wa*A + wb*B)",
		"Operasi Multi Citra",
		2,
		_blend,
		[Param("wa", "Weight for image A", "float", 0.5)],
		describe_size_mismatch=describe_blend_size_mismatch,
	),
	Operation(
		"motion_detection",
		"Motion detection  (C = |A - B|)",
		"Operasi Multi Citra",
		2,
		detect_motion,
		describe_size_mismatch=describe_motion_size_mismatch,
	),
	Operation(
		"logic_and",
		"Logic AND  (C = A AND B)",
		"Operasi Multi Citra",
		2,
		logic_and,
		describe_size_mismatch=describe_logic_size_mismatch,
	),
	Operation(
		"logic_or",
		"Logic OR  (C = A OR B)",
		"Operasi Multi Citra",
		2,
		logic_or,
		describe_size_mismatch=describe_logic_size_mismatch,
	),
	Operation(
		"logic_xor",
		"Logic XOR  (C = A XOR B)",
		"Operasi Multi Citra",
		2,
		logic_xor,
		describe_size_mismatch=describe_logic_size_mismatch,
	),
	Operation(
		"logic_sub",
		"Logic SUB  (C = A - B if A >= B, else 0)",
		"Operasi Multi Citra",
		2,
		logic_sub,
		describe_size_mismatch=describe_logic_size_mismatch,
	),
	Operation(
		"logic_not",
		"Logic NOT  (C = NOT A)",
		"Operasi Multi Citra",
		1,
		logic_not,
	),
	Operation(
		"histogram_equalization",
		"Histogram equalization",
		"Operasi Global",
		1,
		equalize_histogram,
	),
]

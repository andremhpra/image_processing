"""Operasi Berbasis Bingkai / Multi Image, operations that combine two or more images.

Point and geometric operations only ever look at one image at a time; this
category instead combines images pixel by pixel: blending (overlay), motion
detection (frame differencing), and logic operations (AND/OR/XOR/SUB/NOT on
auto-binarized inputs). All three tolerate differently sized inputs (see
their own docstrings for how).
"""

from operasi_multi_citra.blending import blend
from operasi_multi_citra.blending import describe_size_mismatch as describe_blend_size_mismatch
from operasi_multi_citra.logic_operations import describe_size_mismatch as describe_logic_size_mismatch
from operasi_multi_citra.logic_operations import logic_and, logic_not, logic_or, logic_sub, logic_xor
from operasi_multi_citra.motion_detection import describe_size_mismatch as describe_motion_size_mismatch
from operasi_multi_citra.motion_detection import detect_motion

__all__ = [
	"blend",
	"describe_blend_size_mismatch",
	"detect_motion",
	"describe_motion_size_mismatch",
	"describe_logic_size_mismatch",
	"logic_and",
	"logic_or",
	"logic_xor",
	"logic_sub",
	"logic_not",
]

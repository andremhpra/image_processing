"""Operasi Berbasis Bingkai / Multi Image, operations that combine two or more images.

Point and geometric operations only ever look at one image at a time; this
category instead combines same-sized images pixel by pixel: blending
(overlay), motion detection (frame differencing), and bitwise logic
operations (AND/OR/XOR/SUB/NOT).
"""

from operasi_multi_citra.blending import blend
from operasi_multi_citra.logic_operations import logic_and, logic_not, logic_or, logic_sub, logic_xor
from operasi_multi_citra.motion_detection import detect_motion

__all__ = ["blend", "detect_motion", "logic_and", "logic_or", "logic_xor", "logic_sub", "logic_not"]

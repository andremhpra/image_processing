"""Operasi Global: operations whose output for each pixel depends on the
whole image's statistics (its histogram), unlike operasi titik where each
output pixel depends only on the corresponding input pixel.
"""

from operasi_global.histogram_equalization import equalize_histogram

__all__ = ["equalize_histogram"]

"""
Gunakan filter median, lalu penajaman.
"""

from citra_io import baca, tulis
from bmp_io import (
    CitraGrayscale,
    konversi_citra_grayscale,
)


def kernel_median(r: int) -> list[list[int]]:
    kernel = []
    for _ in range(2 * r + 1):
        kernel.append([1] * (2 * r + 1))
    return kernel


MEDIAN = kernel_median(5)


def filter_median(abu: list[list[int]], kernel: list[list[int]]) -> list[list[int]]:
    h, w = len(abu), len(abu[0])
    ry = (len(kernel) - 1) // 2
    rx = (len(kernel[0]) - 1) // 2
    hasil = []
    for _ in range(h):
        hasil.append([0] * w)
    for y in range(h):
        for x in range(w):
            tetangga = []
            for j in range(len(kernel)):
                y_asal = y + j - ry
                if y_asal < 0:
                    y_asal = 0
                elif y_asal > h - 1:
                    y_asal = h - 1
                for i in range(len(kernel[j])):
                    if kernel[j][i] == 0:
                        continue
                    x_asal = x + i - rx
                    if x_asal < 0:
                        x_asal = 0
                    elif x_asal > w - 1:
                        x_asal = w - 1
                    tetangga.append(abu[y_asal][x_asal])
            tetangga.sort()
            hasil[y][x] = tetangga[len(tetangga) // 2]
    return hasil


citra = baca("2_noisy.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)

hasil = filter_median(abu, MEDIAN)

citra_hasil = CitraGrayscale(w, h, hasil, maks)
tulis("2_noisy.bmp", citra_hasil)

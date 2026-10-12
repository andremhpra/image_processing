"""
Gunakan ekualisasi histogram.
"""

from citra_io import baca, simpan
from bmp_io import (
    CitraRGB,
    ambil_warna,
    gabung_warna,
    CitraGrayscale,
)


def ekualisasi(kanal: list[list[int]], w: int, h: int, maks: int) -> list[list[int]]:
    hist = [0] * (maks + 1)
    for y in range(h):
        for x in range(w):
            hist[kanal[y][x]] += 1

    kumulatif = [0] * (maks + 1)
    total = 0
    for i in range(maks + 1):
        total += hist[i]
        kumulatif[i] = total

    pemetaan = []
    for i in range(maks + 1):
        pemetaan.append(round(kumulatif[i] * maks / (w * h)))

    hasil = []
    for _ in range(h):
        hasil.append([0] * w)
    for y in range(h):
        for x in range(w):
            hasil[y][x] = pemetaan[kanal[y][x]]
    return hasil


citra = baca("3_contrast.bmp")
w, h, maks = citra.w, citra.h, citra.maks

if citra.mode == "grayscale":
    citra_hasil = CitraGrayscale(w, h, ekualisasi(citra.pixels, w, h, maks), maks)
else:
    # lakukan ekualisasi di setiap warna (red, green, blue).
    r = ekualisasi(ambil_warna(citra.pixels, w, h, 0), w, h, maks)
    g = ekualisasi(ambil_warna(citra.pixels, w, h, 1), w, h, maks)
    b = ekualisasi(ambil_warna(citra.pixels, w, h, 2), w, h, maks)
    citra_hasil = CitraRGB(w, h, gabung_warna(r, g, b, w, h), maks)

simpan("3_contrast.bmp", citra, citra_hasil)

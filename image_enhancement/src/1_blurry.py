from citra_io import baca, tulis
from bmp_io import (
    CitraGrayscale,
    konversi_citra_grayscale,
    clamp,
    konvolusi,
    histogram,
    gambar_histogram,
)

ALPHA = 1.0
KERNEL = [
    [-ALPHA, -ALPHA, -ALPHA],
    [-ALPHA, 1 + 8 * ALPHA, -ALPHA],
    [-ALPHA, -ALPHA, -ALPHA],
]

citra = baca("1_blurry.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)

k = konvolusi(abu, KERNEL)
hasil = []
for y in range(h):
    baris = []
    for x in range(w):
        baris.append(clamp(k[y][x], maks))
    hasil.append(baris)

citra_hasil = CitraGrayscale(w, h, hasil, maks)
tulis("1_blurry.bmp", citra_hasil)

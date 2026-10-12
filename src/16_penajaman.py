from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    konversi_citra_grayscale,
    clamp,
    konvolusi,
    histogram,
    gambar_histogram,
)

ALPHA = 1.0
KERNEL = [[0, -ALPHA, 0], [-ALPHA, 1 + 4 * ALPHA, -ALPHA], [0, -ALPHA, 0]]

citra = baca_bmp("sample.bmp")
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
tulis_bmp("16_penajaman.bmp", citra_hasil)
gambar_histogram(histogram(citra_hasil), "16_penajaman.bmp")

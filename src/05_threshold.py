from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    gray,
    histogram,
    gambar_histogram,
)

AMBANG = 130
BAWAH = 100
ATAS = 180

w, h, pixels, maks, _ = baca_bmp("sample.bmp")
tunggal = []
for _ in range(h):
    tunggal.append([0] * w)
ganda = []
for _ in range(h):
    ganda.append([0] * w)
for y in range(h):
    for x in range(w):
        v = gray(pixels[y][x], maks)
        tunggal[y][x] = maks if v >= AMBANG else 0
        ganda[y][x] = maks if BAWAH <= v <= ATAS else 0

citra_tunggal = CitraGrayscale(w, h, tunggal, maks)
tulis_bmp("05_threshold_tunggal.bmp", citra_tunggal)
citra_ganda = CitraGrayscale(w, h, ganda, maks)
tulis_bmp("05_threshold_ganda.bmp", citra_ganda)
gambar_histogram(histogram(citra_tunggal), "05_threshold_tunggal.bmp")
gambar_histogram(histogram(citra_ganda), "05_threshold_ganda.bmp")

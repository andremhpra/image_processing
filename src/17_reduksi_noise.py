from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    konversi_citra_grayscale,
    clamp,
    konvolusi,
    jendela,
    histogram,
    gambar_histogram,
)

MEAN = [[1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9]]
GAUSSIAN = [
    [1 / 16, 2 / 16, 1 / 16],
    [2 / 16, 4 / 16, 2 / 16],
    [1 / 16, 2 / 16, 1 / 16],
]

citra = baca_bmp("noisy.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)


k_mean = konvolusi(abu, MEAN)
mean = []
for y in range(h):
    baris = []
    for x in range(w):
        baris.append(clamp(k_mean[y][x], maks))
    mean.append(baris)


k_gaussian = konvolusi(abu, GAUSSIAN)
gaussian = []
for y in range(h):
    baris = []
    for x in range(w):
        baris.append(clamp(k_gaussian[y][x], maks))
    gaussian.append(baris)


median, mid_point = [], []
for _ in range(h):
    median.append([0] * w)
    mid_point.append([0] * w)
for y in range(h):
    for x in range(w):
        tetangga = sorted(jendela(abu, x, y, 1))
        median[y][x] = tetangga[len(tetangga) // 2]
        mid_point[y][x] = clamp((tetangga[0] + tetangga[-1]) / 2, maks)


for nama, hasil in (
    ("noisy", abu),
    ("mean", mean),
    ("median", median),
    ("mid_point", mid_point),
    ("gaussian", gaussian),
):
    citra_hasil = CitraGrayscale(w, h, hasil, maks)
    tulis_bmp(f"17_reduksi_{nama}.bmp", citra_hasil)
    gambar_histogram(histogram(citra_hasil), f"17_reduksi_{nama}.bmp")

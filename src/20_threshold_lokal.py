import math

from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    konversi_citra_grayscale,
    konvolusi,
    simpan_hasil,
)

# ukuran tetangga (ganjil) dan konstanta pengurang threshold
UKURAN_BLOK = 11
C = 2


def kernel_mean(n: int) -> list[list[float]]:
    kernel = []
    for _ in range(n):
        kernel.append([1 / (n * n)] * n)
    return kernel


def kernel_gaussian(n: int) -> list[list[float]]:
    # sigma mengikuti ukuran blok (rumus yang sama dengan OpenCV)
    sigma = 0.3 * ((n - 1) * 0.5 - 1) + 0.8
    r = n // 2
    kernel = []
    total = 0.0
    for j in range(-r, r + 1):
        baris = []
        for i in range(-r, r + 1):
            nilai = math.exp(-(i * i + j * j) / (2 * sigma * sigma))
            baris.append(nilai)
            total += nilai
        kernel.append(baris)
    # normalisasi agar jumlah bobot = 1
    for j in range(n):
        for i in range(n):
            kernel[j][i] /= total
    return kernel


def threshold_adaptif(
    abu: list[list[int]], kernel: list[list[float]], w: int, h: int, maks: int
) -> list[list[int]]:
    # T(x, y) = rata-rata (berbobot) tetangga - C, dihitung untuk tiap piksel
    rata = konvolusi(abu, kernel)
    hasil = []
    for y in range(h):
        baris = []
        for x in range(w):
            baris.append(maks if abu[y][x] > rata[y][x] - C else 0)
        hasil.append(baris)
    return hasil


citra = baca_bmp("sample.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)
citra_abu = CitraGrayscale(w, h, abu, maks)

sesudah = []
for nama, kernel in (
    ("adaptive mean", kernel_mean(UKURAN_BLOK)),
    ("adaptive gaussian", kernel_gaussian(UKURAN_BLOK)),
):
    citra_hasil = CitraGrayscale(w, h, threshold_adaptif(abu, kernel, w, h, maks), maks)
    sesudah.append((f"{nama} (blok {UKURAN_BLOK}, C = {C})", citra_hasil))

simpan_hasil([("sample.bmp", citra), ("grayscale", citra_abu)], sesudah)

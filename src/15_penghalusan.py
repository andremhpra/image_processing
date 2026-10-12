from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    konversi_citra_grayscale,
    clamp,
    konvolusi,
    simpan_hasil,
)

KERNEL = [[0, 1 / 5, 0], [1 / 5, 1 / 5, 1 / 5], [0, 1 / 5, 0]]

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
simpan_hasil([("sample.bmp", citra)], [("penghalusan", citra_hasil)])

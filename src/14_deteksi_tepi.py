from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    konversi_citra_grayscale,
    clamp,
    konvolusi,
    simpan_hasil,
)

ROBERT_1 = [[1.0, 0], [0, -1.0]]
ROBERT_2 = [[0, 1.0], [-1.0, 0]]

citra = baca_bmp("sample.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)

k1 = konvolusi(abu, ROBERT_1)
k2 = konvolusi(abu, ROBERT_2)
hasil = []
for y in range(h):
    baris = []
    for x in range(w):
        baris.append(clamp(abs(k1[y][x]) + abs(k2[y][x]), maks))
    hasil.append(baris)

citra_hasil = CitraGrayscale(w, h, hasil, maks)
simpan_hasil([("sample.bmp", citra)], [("tepi robert", citra_hasil)])

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


def tepi_robert(abu: list[list[int]], w: int, h: int, maks: int) -> list[list[int]]:
    k1 = konvolusi(abu, ROBERT_1)
    k2 = konvolusi(abu, ROBERT_2)
    hasil = []
    for y in range(h):
        baris = []
        for x in range(w):
            baris.append(clamp(abs(k1[y][x]) + abs(k2[y][x]), maks))
        hasil.append(baris)
    return hasil


citra = baca_bmp("sample.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)

# threshold di tengah level (128 untuk 8 bit): piksel >= tengah jadi putih, sisanya hitam
tengah = (maks + 1) // 2
biner = []
for y in range(h):
    baris = []
    for x in range(w):
        baris.append(maks if abu[y][x] >= tengah else 0)
    biner.append(baris)

citra_tepi_abu = CitraGrayscale(w, h, tepi_robert(abu, w, h, maks), maks)
citra_tepi_biner = CitraGrayscale(w, h, tepi_robert(biner, w, h, maks), maks)
simpan_hasil(
    [("sample.bmp", citra)],
    [
        ("tepi robert grayscale", citra_tepi_abu),
        (f"tepi robert threshold {tengah}", citra_tepi_biner),
    ],
)

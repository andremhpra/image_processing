from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    gray,
    histogram,
    gambar_histogram,
)

wa, ha, A, maks, _ = baca_bmp("frame_A.bmp")
wb, hb, B, maks_b, _ = baca_bmp("frame_B.bmp")
if (wa, ha) != (wb, hb):
    raise SystemExit("Ukuran kedua citra harus sama")
if maks != maks_b:
    raise SystemExit("Kedalaman warna kedua citra harus sama")

hasil = []
for _ in range(ha):
    hasil.append([0] * wa)
for y in range(ha):
    for x in range(wa):
        hasil[y][x] = abs(gray(A[y][x], maks) - gray(B[y][x], maks))

citra_hasil = CitraGrayscale(wa, ha, hasil, maks)
tulis_bmp("11_deteksi_gerakan.bmp", citra_hasil)

gambar_histogram(histogram(citra_hasil), "11_deteksi_gerakan.bmp")

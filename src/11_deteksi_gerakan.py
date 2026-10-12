from bmp_io import CitraGrayscale, baca_bmp, gray, simpan_hasil

citra_a = baca_bmp("frame_A.bmp")
citra_b = baca_bmp("frame_B.bmp")
wa, ha, A, maks, _ = citra_a
wb, hb, B, maks_b, _ = citra_b
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

simpan_hasil(
    [("frame_A.bmp", citra_a), ("frame_B.bmp", citra_b)],
    [("deteksi gerakan", citra_hasil)],
)

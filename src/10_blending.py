from bmp_io import CitraRGB, baca_bmp, tulis_bmp, clamp, histogram, gambar_histogram

citra_a = baca_bmp("kotak_A.bmp")
citra_b = baca_bmp("kotak_B.bmp")
if citra_a.mode != "rgb" or citra_b.mode != "rgb":
    raise SystemExit("Kedua citra harus RGB")
wa, ha, A, maks, _ = citra_a
wb, hb, B, maks_b, _ = citra_b
if (wa, ha) != (wb, hb):
    raise SystemExit("Ukuran kedua citra harus sama")
if maks != maks_b:
    raise SystemExit("Kedalaman warna kedua citra harus sama")

hasil = []
for _ in range(ha):
    hasil.append([(0, 0, 0)] * wa)
for y in range(ha):
    for x in range(wa):
        pa = A[y][x]
        pb = B[y][x]
        hasil[y][x] = (
            clamp(pa[0] + pb[0], maks),
            clamp(pa[1] + pb[1], maks),
            clamp(pa[2] + pb[2], maks),
        )

citra_hasil = CitraRGB(wa, ha, hasil, maks)
tulis_bmp("10_blend.bmp", citra_hasil)

gambar_histogram(histogram(citra_hasil), "10_blend.bmp")

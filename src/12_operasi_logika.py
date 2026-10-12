from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    gray,
    histogram,
    gambar_histogram,
)

wa, ha, A, maks, _ = baca_bmp("kotak_A.bmp")
wb, hb, B, maks_b, _ = baca_bmp("kotak_B.bmp")
if (wa, ha) != (wb, hb):
    raise SystemExit("Ukuran kedua citra harus sama")
if maks != maks_b:
    raise SystemExit("Kedalaman warna kedua citra harus sama")
tengah = (maks + 1) // 2

for op in ("AND", "OR", "XOR", "SUB", "NOT"):
    hasil = []
    for _ in range(ha):
        hasil.append([0] * wa)
    for y in range(ha):
        for x in range(wa):
            a = 1 if gray(A[y][x], maks) >= tengah else 0
            b = 1 if gray(B[y][x], maks) >= tengah else 0
            if op == "AND":
                out = a and b
            elif op == "OR":
                out = a or b
            elif op == "XOR":
                out = a != b
            elif op == "SUB":
                out = a - b > 0
            else:
                out = 1 - a
            hasil[y][x] = maks if out else 0

    citra_hasil = CitraGrayscale(wa, ha, hasil, maks)
    tulis_bmp("12_logika_" + op + ".bmp", citra_hasil)

    gambar_histogram(histogram(citra_hasil), "12_logika_" + op + ".bmp")

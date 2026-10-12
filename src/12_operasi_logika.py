from bmp_io import Citra, CitraGrayscale, baca_bmp, gray, simpan_hasil

citra_a = baca_bmp("kotak_A.bmp")
citra_b = baca_bmp("kotak_B.bmp")
wa, ha, A, maks, _ = citra_a
wb, hb, B, maks_b, _ = citra_b
if (wa, ha) != (wb, hb):
    raise SystemExit("Ukuran kedua citra harus sama")
if maks != maks_b:
    raise SystemExit("Kedalaman warna kedua citra harus sama")
tengah = (maks + 1) // 2

sesudah: list[tuple[str, Citra]] = []
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

    sesudah.append((op, CitraGrayscale(wa, ha, hasil, maks)))

simpan_hasil([("kotak_A.bmp", citra_a), ("kotak_B.bmp", citra_b)], sesudah)

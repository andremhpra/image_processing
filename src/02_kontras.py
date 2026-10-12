from bmp_io import CitraRGB, baca_bmp, tulis_bmp, clamp, histogram, gambar_histogram

G = 1.8

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra
P = (maks + 1) // 2
hasil = []
for _ in range(h):
    hasil.append([(0, 0, 0)] * w)
for y in range(h):
    for x in range(w):
        r, g, b = pixels[y][x]
        hasil[y][x] = (
            clamp(G * (r - P) + P, maks),
            clamp(G * (g - P) + P, maks),
            clamp(G * (b - P) + P, maks),
        )
citra_hasil = CitraRGB(w, h, hasil, maks)
tulis_bmp("02_kontras.bmp", citra_hasil)
gambar_histogram(histogram(citra_hasil), "02_kontras.bmp")

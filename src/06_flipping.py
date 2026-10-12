from bmp_io import CitraRGB, baca_bmp, tulis_bmp, histogram, gambar_histogram

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra
horizontal = []
for _ in range(h):
    horizontal.append([(0, 0, 0)] * w)
vertikal = []
for _ in range(h):
    vertikal.append([(0, 0, 0)] * w)
kombinasi = []
for _ in range(h):
    kombinasi.append([(0, 0, 0)] * w)
for y in range(h):
    for x in range(w):
        p = pixels[y][x]
        horizontal[y][w - 1 - x] = p
        vertikal[h - 1 - y][x] = p
        kombinasi[h - 1 - y][w - 1 - x] = p

citra_horizontal = CitraRGB(w, h, horizontal, maks)
tulis_bmp("06_flip_h.bmp", citra_horizontal)
citra_vertikal = CitraRGB(w, h, vertikal, maks)
tulis_bmp("06_flip_v.bmp", citra_vertikal)
citra_kombinasi = CitraRGB(w, h, kombinasi, maks)
tulis_bmp("06_flip_kombinasi.bmp", citra_kombinasi)

gambar_histogram(histogram(citra_horizontal), "06_flip_h.bmp")
gambar_histogram(histogram(citra_vertikal), "06_flip_v.bmp")
gambar_histogram(histogram(citra_kombinasi), "06_flip_kombinasi.bmp")

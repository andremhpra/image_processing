from bmp_io import CitraRGB, baca_bmp, simpan_hasil

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
citra_vertikal = CitraRGB(w, h, vertikal, maks)
citra_kombinasi = CitraRGB(w, h, kombinasi, maks)

simpan_hasil(
    [("sample.bmp", citra)],
    [
        ("flip horizontal", citra_horizontal),
        ("flip vertikal", citra_vertikal),
        ("flip kombinasi", citra_kombinasi),
    ],
)

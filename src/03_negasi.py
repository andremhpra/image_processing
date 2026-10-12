from bmp_io import CitraRGB, baca_bmp, simpan_hasil

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra
hasil = []
for _ in range(h):
    hasil.append([(0, 0, 0)] * w)
for y in range(h):
    for x in range(w):
        r, g, b = pixels[y][x]
        hasil[y][x] = (maks - r, maks - g, maks - b)
citra_hasil = CitraRGB(w, h, hasil, maks)
simpan_hasil([("sample.bmp", citra)], [("negasi", citra_hasil)])

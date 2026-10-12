from bmp_io import CitraRGB, baca_bmp, clamp, simpan_hasil

C = 60

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
        hasil[y][x] = (clamp(r + C, maks), clamp(g + C, maks), clamp(b + C, maks))
citra_hasil = CitraRGB(w, h, hasil, maks)
simpan_hasil([("sample.bmp", citra)], [("brightness", citra_hasil)])

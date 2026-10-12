from bmp_io import CitraRGB, baca_bmp, simpan_hasil

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra
xl, yt, xr, yb = w // 4, h // 4, w * 3 // 4, h * 3 // 4

wb = xr - xl
hb = yb - yt
hasil = []
for _ in range(hb):
    hasil.append([(0, 0, 0)] * wb)
for y in range(hb):
    for x in range(wb):
        hasil[y][x] = pixels[y + yt][x + xl]

citra_hasil = CitraRGB(wb, hb, hasil, maks)

simpan_hasil([("sample.bmp", citra)], [("crop", citra_hasil)])

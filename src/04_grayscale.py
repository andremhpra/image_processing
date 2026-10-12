from bmp_io import CitraGrayscale, baca_bmp, clamp, simpan_hasil

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra
rata = []
for _ in range(h):
    rata.append([0] * w)
berbobot = []
for _ in range(h):
    berbobot.append([0] * w)
for y in range(h):
    for x in range(w):
        r, g, b = pixels[y][x]
        rata[y][x] = clamp((r + g + b) / 3, maks)
        berbobot[y][x] = clamp(0.299 * r + 0.587 * g + 0.144 * b, maks)
citra_rata = CitraGrayscale(w, h, rata, maks)
citra_berbobot = CitraGrayscale(w, h, berbobot, maks)
simpan_hasil(
    [("sample.bmp", citra)],
    [("gray rata-rata", citra_rata), ("gray berbobot", citra_berbobot)],
)

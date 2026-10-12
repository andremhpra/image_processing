from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    clamp,
    histogram,
    gambar_histogram,
)

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
tulis_bmp("04_gray_rata.bmp", citra_rata)
citra_berbobot = CitraGrayscale(w, h, berbobot, maks)
tulis_bmp("04_gray_berbobot.bmp", citra_berbobot)
gambar_histogram(histogram(citra_rata), "04_gray_rata.bmp")
gambar_histogram(histogram(citra_berbobot), "04_gray_berbobot.bmp")

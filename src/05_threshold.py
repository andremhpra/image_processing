from bmp_io import CitraGrayscale, baca_bmp, gray, simpan_hasil

AMBANG = 130
BAWAH = 100
ATAS = 180

citra = baca_bmp("sample.bmp")
w, h, pixels, maks, _ = citra
tunggal = []
for _ in range(h):
    tunggal.append([0] * w)
ganda = []
for _ in range(h):
    ganda.append([0] * w)
for y in range(h):
    for x in range(w):
        v = gray(pixels[y][x], maks)
        tunggal[y][x] = maks if v >= AMBANG else 0
        ganda[y][x] = maks if BAWAH <= v <= ATAS else 0

citra_tunggal = CitraGrayscale(w, h, tunggal, maks)
citra_ganda = CitraGrayscale(w, h, ganda, maks)
simpan_hasil(
    [("sample.bmp", citra)],
    [("threshold tunggal", citra_tunggal), ("threshold ganda", citra_ganda)],
)

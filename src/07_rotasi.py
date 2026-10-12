import math
from bmp_io import CitraRGB, baca_bmp, simpan_hasil

SUDUT = 30

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra

r90 = []
for _ in range(w):
    r90.append([(0, 0, 0)] * h)
r180 = []
for _ in range(h):
    r180.append([(0, 0, 0)] * w)
for y in range(h):
    for x in range(w):
        r90[x][h - 1 - y] = pixels[y][x]
        r180[h - 1 - y][w - 1 - x] = pixels[y][x]

citra_r90 = CitraRGB(h, w, r90, maks)
citra_r180 = CitraRGB(w, h, r180, maks)

t = math.radians(SUDUT)
c = math.cos(t)
s = math.sin(t)
wb = round(abs(w * c) + abs(h * s))
hb = round(abs(w * s) + abs(h * c))
bebas = []
for _ in range(hb):
    bebas.append([(0, 0, 0)] * wb)

for y in range(h):
    for x in range(w):
        dx = x - (w - 1) / 2
        dy = y - (h - 1) / 2
        xb = round(dx * c + dy * s + (wb - 1) / 2)
        yb = round(-dx * s + dy * c + (hb - 1) / 2)
        if 0 <= xb < wb and 0 <= yb < hb:
            bebas[yb][xb] = pixels[y][x]

citra_bebas = CitraRGB(wb, hb, bebas, maks)

simpan_hasil(
    [("sample.bmp", citra)],
    [
        ("rotasi 90", citra_r90),
        ("rotasi 180", citra_r180),
        (f"rotasi {SUDUT}", citra_bebas),
    ],
)

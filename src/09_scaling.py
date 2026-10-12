from bmp_io import Citra, CitraRGB, baca_bmp, simpan_hasil

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra

sesudah: list[tuple[str, Citra]] = []
for nama, skala in (("zoom in", 2), ("zoom out", 0.5)):
    wb = max(1, round(w * skala))
    hb = max(1, round(h * skala))
    hasil = []
    for _ in range(hb):
        hasil.append([(0, 0, 0)] * wb)
    for y in range(hb):
        for x in range(wb):
            y_asal = int(y / skala)
            x_asal = int(x / skala)
            if y_asal > h - 1:
                y_asal = h - 1
            if x_asal > w - 1:
                x_asal = w - 1
            hasil[y][x] = pixels[y_asal][x_asal]

    sesudah.append((nama, CitraRGB(wb, hb, hasil, maks)))

simpan_hasil([("sample.bmp", citra)], sesudah)

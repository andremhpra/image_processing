from bmp_io import CitraRGB, baca_bmp, tulis_bmp, histogram, gambar_histogram

citra = baca_bmp("sample.bmp")
if citra.mode != "rgb":
    raise SystemExit("Citra harus RGB")
w, h, pixels, maks, _ = citra

for nama, skala in (("09_zoom_in.bmp", 2), ("09_zoom_out.bmp", 0.5)):
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

    citra_hasil = CitraRGB(wb, hb, hasil, maks)
    tulis_bmp(nama, citra_hasil)

    gambar_histogram(histogram(citra_hasil), nama)

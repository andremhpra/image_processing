from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    tulis_bmp,
    konversi_citra_grayscale,
    clamp,
    konvolusi,
    histogram,
    gambar_histogram,
)

BETA = 2.0
KERNEL_ARAH_KIRI = [[-BETA, 0, BETA], [-BETA, 1.0, BETA], [-BETA, 0, BETA]]
KERNEL_ARAH_KANAN = [[0, -BETA, -BETA], [BETA, 1.0, -BETA], [BETA, BETA, 0]]

citra = baca_bmp("sample.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)

k_kiri = konvolusi(abu, KERNEL_ARAH_KIRI)
k_kanan = konvolusi(abu, KERNEL_ARAH_KANAN)

hasil_kiri, hasil_kanan = [], []
for y in range(h):
    baris_kiri, baris_kanan = [], []
    for x in range(w):
        baris_kiri.append(clamp(k_kiri[y][x], maks))
        baris_kanan.append(clamp(k_kanan[y][x], maks))
    hasil_kiri.append(baris_kiri)
    hasil_kanan.append(baris_kanan)

citra_hasil_kiri = CitraGrayscale(w, h, hasil_kiri, maks)
citra_hasil_kanan = CitraGrayscale(w, h, hasil_kanan, maks)


tulis_bmp("18_emboss_kiri.bmp", citra_hasil_kiri)
tulis_bmp("18_emboss_kanan.bmp", citra_hasil_kanan)

gambar_histogram(histogram(citra_hasil_kiri), "18_emboss_kiri.bmp")
gambar_histogram(histogram(citra_hasil_kanan), "18_emboss_kanan.bmp")

from bmp_io import (
    Citra,
    CitraGrayscale,
    CitraRGB,
    baca_bmp,
    histogram,
    ambil_warna,
    gabung_warna,
    simpan_hasil,
)

N = 16


def kelompok_histogram(hist: list[int], n: int) -> list[list[int]]:
    rata = sum(hist) / n
    kelompok: list[list[int]] = [[]]
    jumlah = 0
    for k in range(len(hist)):
        if (
            len(kelompok) < n
            and jumlah > 0
            and abs(jumlah + hist[k] - rata) > abs(jumlah - rata)
        ):
            kelompok.append([])
            jumlah = 0
        kelompok[-1].append(k)
        jumlah += hist[k]
    return kelompok


def kuantisasi(
    kanal: list[list[int]], kelompok: list[list[int]], w: int, h: int, maks: int
) -> list[list[int]]:
    baru = [0] * (maks + 1)
    for i in range(len(kelompok)):
        for k in kelompok[i]:
            baru[k] = i
    hasil = []
    for y in range(h):
        baris = []
        for x in range(w):
            baris.append(baru[kanal[y][x]])
        hasil.append(baris)
    return hasil


def kompresi_kanal(
    nama: str, kanal: list[list[int]], hist: list[int], w: int, h: int, maks: int
) -> tuple[list[list[int]], int]:
    kelompok = kelompok_histogram(hist, N)

    for i in range(len(kelompok)):
        jumlah = 0
        for k in kelompok[i]:
            jumlah += hist[k]
        lama = f"{kelompok[i][0]} - {kelompok[i][-1]}"

    return kuantisasi(kanal, kelompok, w, h, maks), len(kelompok)


citra = baca_bmp("sample.bmp")
w, h, maks = citra.w, citra.h, citra.maks
hist = histogram(citra)

if citra.mode == "grayscale":
    daftar_kanal = [("abu", citra.pixels)]
else:
    daftar_kanal = [
        ("merah", ambil_warna(citra.pixels, w, h, 0)),
        ("hijau", ambil_warna(citra.pixels, w, h, 1)),
        ("biru", ambil_warna(citra.pixels, w, h, 2)),
    ]


hasil_kanal = []
bit_lama = 0
bit_baru = 0
maks_baru = 0
for i, (nama, kanal) in enumerate(daftar_kanal):
    hasil, jumlah_kelompok = kompresi_kanal(nama, kanal, hist[i], w, h, maks)
    hasil_kanal.append(hasil)
    bit_lama += maks.bit_length()
    bit_baru += max(1, (jumlah_kelompok - 1).bit_length())
    maks_baru = max(maks_baru, jumlah_kelompok - 1)

ukuran_sebelum = w * h * bit_lama
ukuran_sesudah = w * h * bit_baru
rasio = 100 - ukuran_sesudah / ukuran_sebelum * 100

citra_hasil: Citra
if citra.mode == "grayscale":
    citra_hasil = CitraGrayscale(w, h, hasil_kanal[0], maks_baru)
else:
    r, g, b = hasil_kanal
    citra_hasil = CitraRGB(w, h, gabung_warna(r, g, b, w, h), maks_baru)

simpan_hasil(
    [("sample.bmp", citra)],
    [(f"kuantisasi (rasio = {rasio:.2f}%)", citra_hasil)],
)

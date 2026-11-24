from bmp_io import (
    Citra,
    CitraGrayscale,
    CitraRGB,
    baca_bmp,
    ambil_warna,
    gabung_warna,
    simpan_hasil,
)


def baris_run(kanal: list[list[int]]) -> list[int]:
    barisan = []
    for baris in kanal:
        for p in baris:
            barisan.append(p)
    return barisan


def run_length(barisan: list[int]) -> list[tuple[int, int]]:
    run = []
    nilai, jumlah = barisan[0], 0
    for p in barisan:
        if p == nilai:
            jumlah += 1
        else:
            run.append((nilai, jumlah))
            nilai, jumlah = p, 1
    run.append((nilai, jumlah))
    return run


def kompresi(run: list[tuple[int, int]]) -> list[int]:
    kode = []
    for nilai, jumlah in run:
        kode.append(nilai)
        kode.append(jumlah)
    return kode


def dekompresi(kode: list[int], w: int, h: int) -> list[list[int]]:
    barisan = []
    for i in range(0, len(kode), 2):
        barisan += [kode[i]] * kode[i + 1]
    hasil = []
    for y in range(h):
        hasil.append(barisan[y * w : (y + 1) * w])
    return hasil


def rle(
    nama: str, kanal: list[list[int]], w: int, h: int
) -> tuple[list[list[int]], int, int]:
    barisan = baris_run(kanal)
    run = run_length(barisan)
    kode = kompresi(run)

    hasil = dekompresi(kode, w, h)
    if hasil != kanal:
        raise SystemExit(
            f"Hasil dekompresi kanal {nama} tidak sama dengan citra semula"
        )
    return hasil, len(barisan), len(kode)


citra = baca_bmp("kotak_A.bmp")
w, h, maks = citra.w, citra.h, citra.maks

if citra.mode == "grayscale":
    daftar_kanal = [("abu", citra.pixels)]
else:
    daftar_kanal = [
        ("merah", ambil_warna(citra.pixels, w, h, 0)),
        ("hijau", ambil_warna(citra.pixels, w, h, 1)),
        ("biru", ambil_warna(citra.pixels, w, h, 2)),
    ]

hasil_kanal = []
ukuran_sebelum = 0
ukuran_sesudah = 0
for nama, kanal in daftar_kanal:
    hasil, sebelum, sesudah = rle(nama, kanal, w, h)
    hasil_kanal.append(hasil)
    ukuran_sebelum += sebelum
    ukuran_sesudah += sesudah

rasio = 100 - ukuran_sesudah / ukuran_sebelum * 100

citra_hasil: Citra
if citra.mode == "grayscale":
    citra_hasil = CitraGrayscale(w, h, hasil_kanal[0], maks)
else:
    r, g, b = hasil_kanal
    citra_hasil = CitraRGB(w, h, gabung_warna(r, g, b, w, h), maks)

simpan_hasil(
    [("kotak_A.bmp", citra)],
    [(f"dekompresi run length (rasio = {rasio:.2f}%)", citra_hasil)],
)

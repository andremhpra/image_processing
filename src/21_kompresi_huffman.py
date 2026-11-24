from typing import NamedTuple, Optional

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


class Node(NamedTuple):
    frekuensi: int
    value: int
    kiri: Optional["Node"]
    kanan: Optional["Node"]


def huffman_tree(hist: list[int]) -> Node:
    tree = []
    for k in range(len(hist)):
        if hist[k] > 0:
            tree.append(Node(hist[k], k, None, None))
    tree.sort(key=lambda s: s.frekuensi)

    while len(tree) > 1:
        kiri, kanan = tree[0], tree[1]
        akar = Node(kiri.frekuensi + kanan.frekuensi, -1, kiri, kanan)
        tree = [akar] + tree[2:]
        tree.sort(key=lambda s: s.frekuensi)
    return tree[0]


def kode_huffman(node: Node, kode: str, tabel: dict[int, str]) -> None:
    if node.kiri is None or node.kanan is None:
        tabel[node.value] = kode if kode else "0"
        return
    kode_huffman(node.kiri, kode + "0", tabel)
    kode_huffman(node.kanan, kode + "1", tabel)


def kompresi(kanal: list[list[int]], tabel: dict[int, str]) -> str:
    bit = []
    for baris in kanal:
        for p in baris:
            bit.append(tabel[p])
    return "".join(bit)


def dekompresi(bit: str, akar: Node, w: int, h: int) -> list[list[int]]:
    nilai = []
    node = akar
    for b in bit:
        if node.kiri is not None and node.kanan is not None:
            node = node.kiri if b == "0" else node.kanan
        if node.kiri is None:
            nilai.append(node.value)
            node = akar
    hasil = []
    for y in range(h):
        hasil.append(nilai[y * w : (y + 1) * w])
    return hasil


def huffman(
    nama: str, kanal: list[list[int]], hist: list[int], w: int, h: int
) -> tuple[list[list[int]], int]:
    akar = huffman_tree(hist)
    tabel: dict[int, str] = {}
    kode_huffman(akar, "", tabel)

    bit = kompresi(kanal, tabel)

    hasil = dekompresi(bit, akar, w, h)
    if hasil != kanal:
        raise SystemExit(
            f"Hasil dekompresi kanal {nama} tidak sama dengan citra semula"
        )
    return hasil, len(bit)


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
ukuran_sesudah = 0
for i, (nama, kanal) in enumerate(daftar_kanal):
    hasil, ukuran = huffman(nama, kanal, hist[i], w, h)
    hasil_kanal.append(hasil)
    ukuran_sesudah += ukuran

bit_piksel = maks.bit_length() * len(daftar_kanal)
ukuran_sebelum = w * h * bit_piksel
rasio = 100 - ukuran_sesudah / ukuran_sebelum * 100

citra_hasil: Citra
if citra.mode == "grayscale":
    citra_hasil = CitraGrayscale(w, h, hasil_kanal[0], maks)
else:
    r, g, b = hasil_kanal
    citra_hasil = CitraRGB(w, h, gabung_warna(r, g, b, w, h), maks)

simpan_hasil(
    [("sample.bmp", citra)],
    [(f"dekompresi huffman (rasio = {rasio:.2f}%)", citra_hasil)],
)

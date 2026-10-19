from bmp_io import (
    CitraGrayscale,
    baca_bmp,
    konversi_citra_grayscale,
    histogram,
    simpan_hasil,
)

T_MANUAL = 128
# jari-jari perataan histogram untuk analisis histogram (jendela 2 * R + 1)
R_PERATAAN = 2


def biner(abu: list[list[int]], t: int, w: int, h: int, maks: int) -> list[list[int]]:
    # T adalah level gelap terakhir: piksel di atas T jadi putih, sisanya hitam
    hasil = []
    for y in range(h):
        baris = []
        for x in range(w):
            baris.append(maks if abu[y][x] > t else 0)
        hasil.append(baris)
    return hasil


def threshold_analisis_histogram(hist: list[int]) -> int:
    n = len(hist)
    # ratakan histogram supaya tonjolan kecil tidak dianggap puncak
    rata = []
    for i in range(n):
        total = 0
        jumlah = 0
        for j in range(i - R_PERATAAN, i + R_PERATAAN + 1):
            if 0 <= j < n:
                total += hist[j]
                jumlah += 1
        rata.append(total / jumlah)

    # puncak pertama: level dengan jumlah piksel terbanyak
    p1 = 0
    for i in range(n):
        if rata[i] > rata[p1]:
            p1 = i
    # puncak kedua: tinggi sekaligus jauh dari puncak pertama (jumlah * jarak^2)
    p2 = p1
    skor_maks = 0.0
    for i in range(n):
        skor = rata[i] * (i - p1) ** 2
        if skor > skor_maks:
            skor_maks = skor
            p2 = i
    bawah, atas = min(p1, p2), max(p1, p2)

    # threshold = lembah (nilai terkecil) di antara kedua puncak; jika lembahnya
    # datar, ambil tengah-tengah dataran tersebut
    minimum = min(rata[bawah : atas + 1])
    lembah = []
    for i in range(bawah, atas + 1):
        if rata[i] == minimum:
            lembah.append(i)
    return lembah[len(lembah) // 2]


def threshold_otsu(hist: list[int]) -> int:
    total = sum(hist)
    jumlah_semua = 0
    for i in range(len(hist)):
        jumlah_semua += i * hist[i]

    # cari T yang memaksimalkan varian antar kelas: w0 * w1 * (m0 - m1)^2
    w0 = 0
    jumlah0 = 0
    terbaik = 0
    varian_maks = -1.0
    for t in range(len(hist)):
        w0 += hist[t]
        jumlah0 += t * hist[t]
        w1 = total - w0
        if w0 == 0:
            continue
        if w1 == 0:
            break
        m0 = jumlah0 / w0
        m1 = (jumlah_semua - jumlah0) / w1
        varian = w0 * w1 * (m0 - m1) ** 2
        if varian > varian_maks:
            varian_maks = varian
            terbaik = t
    return terbaik


citra = baca_bmp("sample.bmp")
w, h, maks = citra.w, citra.h, citra.maks
abu = konversi_citra_grayscale(citra)
citra_abu = CitraGrayscale(w, h, abu, maks)
hist = histogram(citra_abu)[0]

sesudah = []
for nama, t in (
    ("manual", T_MANUAL),
    ("analisis histogram", threshold_analisis_histogram(hist)),
    ("otsu", threshold_otsu(hist)),
):
    citra_hasil = CitraGrayscale(w, h, biner(abu, t, w, h, maks), maks)
    sesudah.append((f"{nama} (T = {t})", citra_hasil))

simpan_hasil([("sample.bmp", citra), ("grayscale", citra_abu)], sesudah)

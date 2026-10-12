import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, NamedTuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator, StrMethodFormatter

ROOT = Path(__file__).resolve().parent.parent
FOLDER_SAMPLE = ROOT / "sample"
FOLDER_RESULT = ROOT / "result"

PikselRGB = tuple[int, int, int]


class CitraGrayscale(NamedTuple):
    w: int
    h: int
    pixels: list[list[int]]
    maks: int
    mode: Literal["grayscale"] = "grayscale"


class CitraRGB(NamedTuple):
    w: int
    h: int
    pixels: list[list[PikselRGB]]
    maks: int
    mode: Literal["rgb"] = "rgb"


Citra = CitraGrayscale | CitraRGB


def clamp(n: float, maks: int) -> int:
    n = int(n + 0.5)
    if n < 0:
        return 0
    if n > maks:
        return maks
    return n


def gray(p: int | PikselRGB, maks: int) -> int:
    if isinstance(p, int):
        return p
    return clamp(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2], maks)


def konversi_citra_grayscale(citra: Citra) -> list[list[int]]:
    abu = []
    for y in range(citra.h):
        baris = []
        for x in range(citra.w):
            baris.append(gray(citra.pixels[y][x], citra.maks))
        abu.append(baris)
    return abu


def ambil_warna(
    pixels: list[list[PikselRGB]], w: int, h: int, k: int
) -> list[list[int]]:
    kanal = []
    for y in range(h):
        baris = []
        for x in range(w):
            baris.append(pixels[y][x][k])
        kanal.append(baris)
    return kanal


def gabung_warna(
    r: list[list[int]], g: list[list[int]], b: list[list[int]], w: int, h: int
) -> list[list[PikselRGB]]:
    hasil = []
    for y in range(h):
        baris = []
        for x in range(w):
            baris.append((r[y][x], g[y][x], b[y][x]))
        hasil.append(baris)
    return hasil


def jendela(abu: list[list[int]], x: int, y: int, r: int) -> list[int]:
    h, w = len(abu), len(abu[0])
    hasil = []
    for j in range(-r, r + 1):
        y_asal = y + j
        if y_asal < 0:
            y_asal = 0
        elif y_asal > h - 1:
            y_asal = h - 1
        for i in range(-r, r + 1):
            x_asal = x + i
            if x_asal < 0:
                x_asal = 0
            elif x_asal > w - 1:
                x_asal = w - 1
            hasil.append(abu[y_asal][x_asal])
    return hasil


def histogram(citra: Citra) -> list[list[int]]:
    if citra.mode == "grayscale":
        hist = [0] * (citra.maks + 1)
        for baris in citra.pixels:
            for p in baris:
                hist[p] += 1
        return [hist]
    hist_rgb = []
    for _ in range(3):
        hist_rgb.append([0] * (citra.maks + 1))
    for baris in citra.pixels:
        for p in baris:
            for k in range(3):
                hist_rgb[k][p[k]] += 1
    return hist_rgb


def konvolusi(
    abu: Sequence[Sequence[float]], kernel: Sequence[Sequence[float]]
) -> list[list[float]]:
    h, w = len(abu), len(abu[0])
    # jari-jari kernel ke atas/bawah dan ke kiri/kanan (boleh beda, mis. kernel 1 x 9)
    ry = (len(kernel) - 1) // 2
    rx = (len(kernel[0]) - 1) // 2
    hasil = []
    for _ in range(h):
        hasil.append([0.0] * w)
    for y in range(h):
        for x in range(w):
            total = 0.0
            for j, baris in enumerate(kernel):
                y_asal = y + j - ry
                if y_asal < 0:
                    y_asal = 0
                elif y_asal > h - 1:
                    y_asal = h - 1
                for i, k in enumerate(baris):
                    x_asal = x + i - rx
                    if x_asal < 0:
                        x_asal = 0
                    elif x_asal > w - 1:
                        x_asal = w - 1
                    total += k * abu[y_asal][x_asal]
            hasil[y][x] = total
    return hasil


# merah, hijau, biru
WARNA_KANAL = ("#d62728", "#2ca02c", "#1f77b4")
WARNA_ABU = ("#555555",)


def gambar_citra(ax: Axes, citra: Citra) -> None:
    if citra.mode == "grayscale":
        ax.imshow(citra.pixels, cmap="gray", vmin=0, vmax=citra.maks)
    else:
        # imshow menerima RGB float 0..1, jadi normalisasi terhadap maks
        img = []
        for baris in citra.pixels:
            baris_img = []
            for r, g, b in baris:
                baris_img.append((r / citra.maks, g / citra.maks, b / citra.maks))
            img.append(baris_img)
        ax.imshow(img)
    ax.axis("off")


def gambar_histogram(ax: Axes, citra: Citra) -> None:
    hist = histogram(citra)
    nilai = list(range(citra.maks + 1))
    warna_kanal = WARNA_ABU if citra.mode == "grayscale" else WARNA_KANAL
    # isi transparan + garis tepi tegas: ketiga kanal tetap terlihat saat bertumpuk
    for warna, h in zip(warna_kanal, hist):
        ax.fill_between(nilai, h, step="mid", color=warna, alpha=0.2, linewidth=0)
        ax.step(nilai, h, where="mid", color=warna, linewidth=1.2)
    # beri ruang di kiri/kanan dan atas agar batang di 0, maks, dan puncak tidak tertutup bingkai
    tepi = max(2, citra.maks * 0.02)
    ax.set_xlim(-tepi, citra.maks + tepi)
    ax.margins(y=0.05)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MultipleLocator(25 if citra.maks >= 25 else 1))
    ax.set_xlabel("Intensitas")
    ax.set_ylabel("Jumlah piksel")
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.8)
    ax.set_axisbelow(True)


def simpan_gambar(daftar: list[tuple[str, Citra]], judul: str, path: Path) -> None:
    fig, axes = plt.subplots(
        len(daftar),
        2,
        figsize=(13, 4.5 * len(daftar)),
        width_ratios=(1, 1.6),
        squeeze=False,
    )
    for (nama, citra), (ax_citra, ax_hist) in zip(daftar, axes):
        gambar_citra(ax_citra, citra)
        ax_citra.set_title(f"{nama} ({citra.w} x {citra.h})")
        gambar_histogram(ax_hist, citra)
        ax_hist.set_title(f"Histogram {nama}")
    fig.suptitle(judul, fontsize=16, fontweight="bold")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def simpan_hasil(
    sebelum: list[tuple[str, Citra]],
    sesudah: list[tuple[str, Citra]],
    folder: Path = FOLDER_RESULT,
) -> None:
    # folder hasil dinamai sesuai nama program, mis. result/01_brightness/
    nama_program = Path(sys.argv[0]).stem
    folder_program = folder / nama_program
    # nama proses dari nama program, mis. "11_deteksi_gerakan" -> "Deteksi Gerakan"
    proses = nama_program.split("_", 1)[-1].replace("_", " ").title()
    simpan_gambar(sebelum, f"Sebelum {proses}", folder_program / "sebelum.png")
    simpan_gambar(sesudah, f"Sesudah {proses}", folder_program / "sesudah.png")


def geseran_topeng(topeng: int) -> int:
    geser = 0
    while topeng != 0 and topeng & 1 == 0:
        topeng >>= 1
        geser += 1
    return geser


def baca_bmp(path: str, folder: Path = FOLDER_SAMPLE) -> Citra:
    with open(folder / path, "rb") as f:
        data = f.read()
    offset = int.from_bytes(data[10:14], "little")
    ukuran_header = int.from_bytes(data[14:18], "little")
    w = int.from_bytes(data[18:22], "little", signed=True)
    h = int.from_bytes(data[22:26], "little", signed=True)
    bit = int.from_bytes(data[28:30], "little")
    kompresi = int.from_bytes(data[30:34], "little")
    jumlah_warna = int.from_bytes(data[46:50], "little")
    if bit not in (1, 4, 8, 24, 32) or not (
        kompresi == 0 or (bit == 32 and kompresi == 3)
    ):
        raise ValueError(f"{path}: hanya mendukung BMP 1/4/8/24/32 bit tanpa kompresi")

    # 32 bit: posisi R, G, B di tiap piksel ditentukan oleh topeng (bitfield)
    topeng_r, topeng_g, topeng_b = 0xFF0000, 0x00FF00, 0x0000FF
    if bit == 32 and kompresi == 3:
        topeng_r = int.from_bytes(data[54:58], "little")
        topeng_g = int.from_bytes(data[58:62], "little")
        topeng_b = int.from_bytes(data[62:66], "little")
    geser_r = geseran_topeng(topeng_r)
    geser_g = geseran_topeng(topeng_g)
    geser_b = geseran_topeng(topeng_b)

    palet: list[PikselRGB] = []
    if bit <= 8:
        awal_palet = 14 + ukuran_header
        for i in range(jumlah_warna or 1 << bit):
            j = awal_palet + i * 4
            palet.append((data[j + 2], data[j + 1], data[j]))

    atas_bawah = h < 0
    h = abs(h)
    baris_byte = (w * bit + 31) // 32 * 4
    topeng = (1 << bit) - 1
    pixels: list[list[PikselRGB]] = []
    for y in range(h):
        baris_file = y if atas_bawah else h - 1 - y
        awal = offset + baris_file * baris_byte
        baris = []
        for x in range(w):
            if bit == 24:
                i = awal + x * 3
                baris.append((data[i + 2], data[i + 1], data[i]))
            elif bit == 32:
                i = awal + x * 4
                nilai = int.from_bytes(data[i : i + 4], "little")
                baris.append(
                    (
                        (nilai & topeng_r) >> geser_r,
                        (nilai & topeng_g) >> geser_g,
                        (nilai & topeng_b) >> geser_b,
                    )
                )
            else:
                posisi = x * bit
                geser = 8 - bit - posisi % 8
                baris.append(palet[(data[awal + posisi // 8] >> geser) & topeng])
        pixels.append(baris)

    if bit == 24:
        return CitraRGB(w, h, pixels, (1 << (bit // 3)) - 1)
    if bit == 32:
        return CitraRGB(w, h, pixels, topeng_r >> geser_r)
    semua_abu = True
    for i in range(len(palet)):
        r, g, b = palet[i]
        if r != g or g != b:
            semua_abu = False
    if semua_abu:
        maks = max(1, len(palet) - 1)
        pixels_abu: list[list[int]] = []
        for y in range(h):
            baris_abu = []
            for x in range(w):
                baris_abu.append(round(pixels[y][x][0] * maks / 255))
            pixels_abu.append(baris_abu)
        return CitraGrayscale(w, h, pixels_abu, maks)
    return CitraRGB(w, h, pixels, 255)


def tulis_bmp(path: str, citra: Citra, folder: Path = FOLDER_RESULT) -> None:
    w, h, maks = citra.w, citra.h, citra.maks
    palet: list[int] = []
    if citra.mode == "grayscale":
        bit = 0
        for b in (1, 4, 8):
            if maks < 1 << b:
                bit = b
                break
        if bit == 0:
            raise ValueError("Citra grayscale maksimal 8 bit (maks <= 255)")
        for i in range(maks + 1):
            palet.append(round(i * 255 / maks))
    else:
        bit = 24

    baris_byte = (w * bit + 31) // 32 * 4
    ukuran = baris_byte * h
    offset = 54 + len(palet) * 4
    data = bytearray(b"BM")
    data += (offset + ukuran).to_bytes(4, "little")
    data += bytes(4)
    data += offset.to_bytes(4, "little")
    data += (40).to_bytes(4, "little")
    data += w.to_bytes(4, "little")
    data += h.to_bytes(4, "little")
    data += (1).to_bytes(2, "little")
    data += bit.to_bytes(2, "little")
    data += bytes(4)
    data += ukuran.to_bytes(4, "little")
    data += bytes(8)
    data += len(palet).to_bytes(4, "little")
    data += bytes(4)
    for v in palet:
        data += bytes((v, v, v, 0))
    for y in range(h - 1, -1, -1):
        baris = bytearray(baris_byte)
        if citra.mode == "grayscale":
            for x in range(w):
                posisi = x * bit
                baris[posisi // 8] |= citra.pixels[y][x] << (8 - bit - posisi % 8)
        else:
            for x in range(w):
                r, g, b = citra.pixels[y][x]
                baris[x * 3] = round(b * 255 / maks)
                baris[x * 3 + 1] = round(g * 255 / maks)
                baris[x * 3 + 2] = round(r * 255 / maks)
        data += baris
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / path, "wb") as f:
        f.write(data)

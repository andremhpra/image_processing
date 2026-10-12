import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent.parent
sys.path.append(str(FOLDER.parent / "src"))

from bmp_io import (
    Citra,
    baca_bmp,
    tulis_bmp,
    histogram,
    gambar_histogram,
)

FOLDER_SAMPLES = FOLDER / "samples"
FOLDER_IMG = FOLDER / "result" / "img"
FOLDER_HISTOGRAM = FOLDER / "result" / "histogram"


def baca(nama: str) -> Citra:
    citra = baca_bmp(nama, FOLDER_SAMPLES)
    gambar_histogram(
        histogram(citra), Path(nama).stem + "_sebelum.bmp", FOLDER_HISTOGRAM
    )
    return citra


def tulis(nama: str, citra: Citra) -> None:
    tulis_bmp(nama, citra, FOLDER_IMG)
    gambar_histogram(histogram(citra), nama, FOLDER_HISTOGRAM)

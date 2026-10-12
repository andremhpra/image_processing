import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent.parent
sys.path.append(str(FOLDER.parent / "src"))

from bmp_io import Citra, baca_bmp, simpan_hasil

FOLDER_SAMPLES = FOLDER / "samples"
FOLDER_RESULT = FOLDER / "result"


def baca(nama: str) -> Citra:
    return baca_bmp(nama, FOLDER_SAMPLES)


def simpan(nama: str, sebelum: Citra, sesudah: Citra) -> None:
    simpan_hasil([(nama, sebelum)], [("hasil", sesudah)], FOLDER_RESULT)

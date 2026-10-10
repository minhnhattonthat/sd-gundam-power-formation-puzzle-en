import zlib
from pathlib import Path

import pytest

ROM = Path(__file__).resolve().parent.parent / "rom" / "SD Gundam - Power Formation Puzzle (Japan).sfc"


@pytest.mark.skipif(not ROM.exists(), reason="original ROM not present")
def test_original_rom_hash():
    assert zlib.crc32(ROM.read_bytes()) == 0x87E4476D

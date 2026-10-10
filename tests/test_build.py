import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lint  # noqa: E402
import lz  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ORIG.exists(), reason="original ROM not present")


@needs_rom
def test_identity_build_is_byte_identical():
    assert bytes(build.build_identity()) == build.ORIG.read_bytes()


@needs_rom
def test_jp_roundtrip_and_coverage():
    rom = build.ORIG.read_bytes()
    entries = json.loads((ROOT / "script" / "briefing.json").read_text(encoding="utf-8"))
    p = build.BRIEF_LO
    for e in entries:
        assert int(e["addr"], 16) == p
        b = build.JP.encode(e["jp"])
        assert rom[p:p + len(b)] == b, e["id"]
        p += len(b)
    assert p == build.BRIEF_HI  # the block is fully covered, no gaps


@needs_rom
def test_lz_roundtrip_font():
    rom = build.ORIG.read_bytes()
    raw, used = lz.decompress(rom, build.FONT_OFF)
    assert used == build.FONT_PACKED
    assert lz.decompress(lz.compress(raw, rom[build.FONT_OFF]))[0] == raw


def test_lz_item_count_guard():
    data = bytes(range(256)) * 9  # forces many items; compress must avoid (N>>3)&0xFF == 0
    packed = lz.compress(data)
    assert (int.from_bytes(packed[1:3], "little") >> 3) & 0xFF
    assert lz.decompress(packed)[0] == data


def test_text_lint_clean():
    errs = lint.lint()
    assert not errs, "\n".join(errs)


@needs_rom
def test_english_build_fits():
    rom = build.build_english()
    assert len(rom) == build.ROM_SIZE

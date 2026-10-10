"""Build entry point.
  python -X utf8 build.py identity   rebuild the original from script/*.json jp fields; must be byte-identical
  python -X utf8 build.py english    build/sdgundam_en.sfc from the en fields (empty en -> JP left in place: error)
  python -X utf8 build.py marker     every string replaced by its id + filler, for layout tours
"""
import json
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import copyright  # noqa: E402
import font  # noqa: E402
import lz  # noqa: E402
from tbl import Table  # noqa: E402

ORIG = ROOT / "rom" / "SD Gundam - Power Formation Puzzle (Japan).sfc"
OUT = {"english": ROOT / "build" / "sdgundam_en.sfc", "marker": ROOT / "build" / "sdgundam_marker.sfc",
       "identity": ROOT / "build" / "identity.sfc"}
ASAR = ROOT / "tools" / "asar" / "asar.exe"
JP = Table.load(ROOT / "tbl" / "jp.tbl")
EN = Table.load(ROOT / "tbl" / "en.tbl")

BRIEF_LO, BRIEF_HI = 0xE8000, 0xE8B47
FONT_OFF, FONT_PACKED = 0xEACB4, 7764        # $9D:ACB4, original packed size (in-place limit)
PROLOGUE_OFF, PROLOGUE_LDX = 0xFC4C0, 0x1DA85
OPTIONS_OFF, OPTIONS_BLOCK = 0xFF79F, 0x1F0DA  # param block: [0]=bank, [2..3]=pointer
TEXT_BANK, TEXT_LO, TEXT_HI = 0xA0, 0x100000, 0x108000  # new text bank $A0 (file 0x100000), code bank $A1
ROM_SIZE = 0x200000
MENU_CODE0 = 0x60  # first code for pre-rendered options-menu cells (text glyphs use 00-5E)

# Widths in characters (8 px each) for the English layout; see asm/main.asm for the matching start columns.
WIDTH = {"mission": 26, "ending": 26, "prologue": 26, "option": 64}


def load(name):
    return json.loads((ROOT / "script" / (name + ".json")).read_text(encoding="utf-8"))


def cpu(file_off):
    return (0x80 | file_off >> 15) << 16 | 0x8000 | (file_off & 0x7FFF)


def put_ptr(rom, kind, slot, target):
    n = 3 if kind == "p24" else 2
    rom[slot:slot + n] = (cpu(target) & (1 << 8 * n) - 1).to_bytes(n, "little")


def en_bytes(text):
    """English source text ('\\n' = new line) -> game bytes ending in FF."""
    return EN.encode(text.replace("\n", "{br}").replace(" ", "{sp}") + "{end}")


def marker_text(e):
    if e["kind"] == "option":
        return e["id"] if len(JP.encode(e["jp"])) > 1 else e["id"][1:]
    w = WIDTH[e["kind"]]
    lines = e["jp"].replace("{end}", "").split("{br}")
    filler = "The quick brown fox jumps over the lazy dog. " * 3
    return "\n".join(("[%s.%d] " % (e["id"], i) + filler)[:w] if ln else "" for i, ln in enumerate(lines))


def build_identity():
    rom = bytearray(ORIG.read_bytes())
    p = BRIEF_LO
    for e in load("briefing"):
        b = JP.encode(e["jp"])
        rom[p:p + len(b)] = b
        for kind, o in e["slots"]:
            put_ptr(rom, kind, int(o, 16), p)
        p += len(b)
    assert p == BRIEF_HI, hex(p)
    for e in load("prologue"):
        b = JP.encode(e["jp"])
        rom[PROLOGUE_OFF:PROLOGUE_OFF + len(b)] = b
    opts = JP.encode("{br}".join(e["jp"] for e in load("options")) + "{end}")
    rom[OPTIONS_OFF:OPTIONS_OFF + len(opts)] = opts
    f, _ = lz.decompress(rom, FONT_OFF)
    assert lz.decompress(lz.compress(f, rom[FONT_OFF]))[0] == f
    return rom


class Alloc:
    def __init__(self, rom, lo, hi):
        self.rom, self.p, self.hi = rom, lo, hi

    def put(self, b):
        if self.p + len(b) > self.hi:
            raise OverflowError("text bank full at %06X (+%d bytes)" % (self.p, len(b)))
        o = self.p
        self.rom[o:o + len(b)] = b
        self.p += len(b)
        return o


def build_english(marker=False):
    rom = bytearray(ORIG.read_bytes()) + b"\xff" * (ROM_SIZE - len(ORIG.read_bytes()))
    rom[0x7FD7] = 0x0B  # 2 MiB
    text = (lambda e: marker_text(e)) if marker else (lambda e: e["en"])
    missing = [e["id"] for n in ("briefing", "prologue", "options") for e in load(n) if not text(e)]
    if missing:
        raise SystemExit("untranslated: " + " ".join(missing))
    al = Alloc(rom, TEXT_LO, TEXT_HI)
    rom[BRIEF_LO:BRIEF_HI] = b"\xff" * (BRIEF_HI - BRIEF_LO)
    for e in load("briefing"):
        o = al.put(en_bytes(text(e)))
        for kind, s in e["slots"]:
            put_ptr(rom, kind, int(s, 16), o)
    for e in load("prologue"):
        rom[PROLOGUE_OFF:PROLOGUE_OFF + e["len"]] = b"\xff" * e["len"]
        o = al.put(en_bytes(text(e)))
        rom[PROLOGUE_LDX:PROLOGUE_LDX + 2] = (cpu(o) & 0xFFFF).to_bytes(2, "little")
    # Options menu: its writer emits 16 px per code and the menu DMAs fixed-size slots, so each item keeps its JP
    # glyph count and the English word is pre-rendered across that many 16x16 cells (new codes from MENU_CODE0).
    opts = load("options")
    old = len(JP.encode("{br}".join(e["jp"] for e in opts) + "{end}"))
    rom[OPTIONS_OFF:OPTIONS_OFF + old] = b"\xff" * old
    cells, code_of_cell, items = {}, {}, []
    for e in opts:
        n = len(JP.encode(e["jp"]))
        codes = bytearray()
        for px in font.render_cells(text(e), n):
            key = tuple(map(tuple, px))
            if not any(any(r) for r in px):
                codes.append(0x00)  # blank = space
                continue
            if key not in code_of_cell:
                code_of_cell[key] = MENU_CODE0 + len(code_of_cell)
                cells[code_of_cell[key]] = px
            codes.append(code_of_cell[key])
        items.append(bytes(codes))
    o = al.put(b"\xfe".join(items) + b"\xff")
    rom[OPTIONS_BLOCK] = TEXT_BANK
    rom[OPTIONS_BLOCK + 2:OPTIONS_BLOCK + 4] = (cpu(o) & 0xFFFF).to_bytes(2, "little")
    # boot copyright screen: new chr + tilemap in the text bank; operands of LDA #lo / LDA #bank at $8C:D171/D1B9
    for data, (lo_op, bank_op, old) in zip(copyright.build(rom), ((0x65172, 0x65177, 0x96BB), (0x651BA, 0x651BF, 0x9C3A))):
        assert rom[lo_op:lo_op + 2] == old.to_bytes(2, "little") and rom[bank_op] == 0x82
        o = al.put(data)
        rom[lo_op:lo_op + 2] = (cpu(o) & 0xFFFF).to_bytes(2, "little")
        rom[bank_op] = cpu(o) >> 16
    # font, in place
    raw = font.build_font({c: c - 0x20 for c in range(0x20, 0x7F)}, lz.decompress(rom, FONT_OFF)[0], cells)
    packed = lz.compress(raw, rom[FONT_OFF])
    if len(packed) > FONT_PACKED:
        raise OverflowError("font %d bytes > %d" % (len(packed), FONT_PACKED))
    rom[FONT_OFF:FONT_OFF + FONT_PACKED] = packed + b"\xff" * (FONT_PACKED - len(packed))
    return rom


def asar(path):
    r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ROOT / "asm" / "main.asm"), str(path)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("asar failed:\n" + r.stdout + r.stderr)


def main(mode):
    out = OUT[mode]
    out.parent.mkdir(exist_ok=True)
    if mode == "identity":
        rom = build_identity()
        out.write_bytes(rom)
        same = bytes(rom) == ORIG.read_bytes()
        print("identity:", "identical" if same else "DIFFERS", "crc %08X" % zlib.crc32(rom))
        return 0 if same else 1
    rom = build_english(marker=(mode == "marker"))
    out.write_bytes(rom)
    asar(out)
    print("built", out, "crc %08X" % zlib.crc32(out.read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "english"))

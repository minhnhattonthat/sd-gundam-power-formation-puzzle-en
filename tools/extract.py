"""Dump the game's Japanese text to script/*.json. Never overwrites an existing file without --force
(English lives in those files)."""
import json
import sys
from pathlib import Path

from tbl import Table

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "rom" / "SD Gundam - Power Formation Puzzle (Japan).sfc"
JP = Table.load(ROOT / "tbl" / "jp.tbl")

BRIEF_LO, BRIEF_HI = 0xE8000, 0xE8B47        # mission + ending block, bank $9D
MISSION_TABLES = (0x19B1C, 0x19B49, 0x19B76)  # 3 teams x 15 24-bit pointers
ENDING_P16 = (0x1D0CE, 0x1D0D0, 0x1D0D2, 0x1D0D4, 0x1A90B, 0x1A90D, 0x1A90F)
ENDING_IMM = (0x1A8F1,)                       # LDX #$8B0B at $83:A8F0
PROLOGUE = 0xFC4C0                            # $9F:C4C0, LDX # operand at $83:DA85
OPTIONS = 0xFF79F                             # $9F:F79F, param block $83:F0DA


def off(cpu):
    return ((cpu & 0x7F0000) >> 1) | (cpu & 0x7FFF)


def strings(rom, lo, hi):
    p, out = lo, []
    while p < hi:
        text, n = JP.decode(rom, p)
        out.append((p, text, n))
        p += n
    return out


def slots_for(rom, addr):
    """Pointer slots (kind, file offset) that reference string at `addr` in the briefing block."""
    cpu16 = 0x8000 | (addr & 0x7FFF)
    s = []
    for t in MISSION_TABLES:
        for i in range(15):
            o = t + 3 * i
            if off(int.from_bytes(rom[o:o + 3], "little")) == addr:
                s.append(["p24", "%06X" % o])
    for o in ENDING_P16 + ENDING_IMM:
        if int.from_bytes(rom[o:o + 2], "little") == cpu16:
            s.append(["p16", "%06X" % o])
    return s


def dump(rom):
    brief = []
    for i, (addr, text, n) in enumerate(strings(rom, BRIEF_LO, BRIEF_HI)):
        slots = slots_for(rom, addr)
        kind = "ending" if all(k == "p16" for k, _ in slots) else "mission"
        brief.append({"id": "B%02d" % i, "kind": kind, "addr": "%06X" % addr, "len": n, "slots": slots,
                      "jp": text, "en": ""})
    text, n = JP.decode(rom, PROLOGUE)
    prologue = [{"id": "P00", "kind": "prologue", "addr": "%06X" % PROLOGUE, "len": n, "jp": text, "en": ""}]
    text, n = JP.decode(rom, OPTIONS)
    options = [{"id": "O%02d" % i, "kind": "option", "jp": s, "en": ""}
               for i, s in enumerate(text[:-len("{end}")].split("{br}"))]
    return {"briefing": brief, "prologue": prologue, "options": options}


if __name__ == "__main__":
    rom = ORIG.read_bytes()
    for name, entries in dump(rom).items():
        path = ROOT / "script" / (name + ".json")
        if path.exists() and "--force" not in sys.argv:
            print("exists, skipped (use --force):", path)
            continue
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("wrote", path, len(entries))

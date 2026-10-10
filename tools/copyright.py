"""Boot copyright screen: replace the two Japanese rights lines with English, keeping the (C) BANDAI 1996 line.
BG1 4bpp, chr LZ at $82:96BB (128 tiles), tilemap LZ at $82:9C3A (16-byte header + 32x32 map), both loaded
by $8C:D171/$8C:D1B9. The JP lines sit on map rows 8-9 and 12-13 from col 3; their tiles (01-56) are reused."""
from pathlib import Path

import font
import lz

ROOT = Path(__file__).resolve().parent.parent
CHR_OFF, MAP_OFF = 0x116BB, 0x11C3A
LINES = {8: "SOTSU AGENCY \x01 SUNRISE", 12: "SOTSU AGENCY \x01 SUNRISE \x01 TV ASAHI"}  # \x01 = middle dot
COPY_TOP, COPY_BOTTOM = 0x057, 0x063  # the (C) glyph tiles of the BANDAI line
INK = 15
NT = 27  # text tiles per row, cols 4-30
FREE = [t for t in range(0x01, 0x80) if not 0x57 <= t <= 0x6E]


def render(text, width):
    g = font.load_glyphs(ROOT / "font" / "menu_13.txt", None)
    g[1] = ["...."] * 6 + [".##.", ".##."] + ["...."] * 5  # middle dot
    rows = [[0] * width for _ in range(16)]
    x = 6  # gap after the (C), like the BANDAI line
    for ch in text:
        for y, r in enumerate(g[ord(ch)]):
            for dx, c in enumerate(r):
                if c == "#":
                    rows[y + font.MENU_Y][x + dx] = INK
        x += len(g[ord(ch)][0])
    if x > width:
        raise ValueError("copyright line too wide: %r" % text)
    return rows


def tile4(rows, tx, ty):
    b = bytearray(32)
    for y in range(8):
        for x in range(8):
            v = rows[ty * 8 + y][tx * 8 + x]
            for k in range(4):
                if v >> k & 1:
                    b[(k >> 1) * 16 + 2 * y + (k & 1)] |= 0x80 >> x
    return bytes(b)


def build(rom):
    """Returns (chr_lz, map_lz) for the English copyright screen."""
    chr_ = bytearray(lz.decompress(rom, CHR_OFF)[0])
    mp = bytearray(lz.decompress(rom, MAP_OFF)[0])
    free = iter(FREE)
    seen = {bytes(32): 0}
    for row, text in LINES.items():
        px = render(text, 8 * NT)
        for half in (0, 1):
            r = row + half
            for col in range(3, 32):
                mp[0x10 + (r * 32 + col) * 2:0x10 + (r * 32 + col) * 2 + 2] = b"\x00\x00"
            mp[0x10 + (r * 32 + 3) * 2] = COPY_TOP if half == 0 else COPY_BOTTOM
            for tx in range(NT):
                t = tile4(px, tx, half)
                if t not in seen:
                    seen[t] = next(free)
                    chr_[seen[t] * 32:seen[t] * 32 + 32] = t
                o = 0x10 + (r * 32 + 4 + tx) * 2
                mp[o] = seen[t]
                mp[o + 1] = 0x00
    return lz.compress(bytes(chr_), rom[CHR_OFF]), lz.compress(bytes(mp), rom[MAP_OFF])

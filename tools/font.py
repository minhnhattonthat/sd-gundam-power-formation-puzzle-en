"""Build the English font block: same 12320-byte 2bpp layout as the original font at $9D:ACB4.
- Text glyphs (font/en_8x16.txt): code c is an 8x16 cell in tiles B(c) (top) and B(c)+16 (bottom); B+1/B+17 blank.
- Menu words (font/menu_13.txt, proportional): pre-rendered across whole 16x16 cells (tiles B, B+1, B+16, B+17),
  for the options menu, whose writer always emits 16 px per code.
Colours match the original: 1 = light ink, 3 = dark shadow (right and below)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_SIZE = 12320
MENU_Y = 1  # top row of the 13 px menu font inside the 16 px cell


def load_glyphs(path=ROOT / "font" / "en_8x16.txt", width=8):
    """{ascii: [row strings]}; width=None keeps each glyph's own width (its advance)."""
    g, cur = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("== "):
            cur = int(line[3:5], 16)
            g[cur] = []
        elif cur is not None and line and line[0] in ".#":
            g[cur].append(line.ljust(width, ".")[:width] if width else line)
    for c, rows in g.items():
        if len(rows) > 16:
            raise ValueError("glyph %02X has %d rows" % (c, len(rows)))
    return g


def base_tile(code):
    return ((code & 0xF8) << 2) | ((code & 7) << 1)


def pixels(rows, w=8):
    """16-row ink map (strings of . and #) -> palette indices with drop shadow."""
    ink = [[r < len(rows) and x < len(rows[r]) and rows[r][x] == "#" for x in range(w)] for r in range(16)]
    px = [[0] * w for _ in range(16)]
    for y in range(16):
        for x in range(w):
            if ink[y][x]:
                px[y][x] = 1
            elif (x > 0 and ink[y][x - 1]) or (y > 0 and ink[y - 1][x]) or (x > 0 and y > 0 and ink[y - 1][x - 1]):
                px[y][x] = 3
    return px


def tile_bytes(px, y0, x0=0):
    out = bytearray()
    for y in range(y0, y0 + 8):
        lo = hi = 0
        for x in range(8):
            v = px[y][x0 + x]
            lo |= (v & 1) << (7 - x)
            hi |= (v >> 1 & 1) << (7 - x)
        out += bytes([lo, hi])
    return out


def menu_width(word, g=None):
    g = g or load_glyphs(ROOT / "font" / "menu_13.txt", None)
    return sum(len(g[ord(c)][0]) for c in word)


def render_cells(word, ncells):
    """Pre-render `word` left-aligned into ncells 16x16 cells; returns a list of 16x16 palette-index grids."""
    g = load_glyphs(ROOT / "font" / "menu_13.txt", None)
    w = ncells * 16
    if menu_width(word, g) > w:
        raise ValueError("%r is %d px, budget %d" % (word, menu_width(word, g), w))
    rows = ["." * w for _ in range(16)]
    x = 0
    for c in word:
        glyph = g[ord(c)]
        for y, r in enumerate(glyph):
            yy = y + MENU_Y
            if yy < 16:
                rows[yy] = rows[yy][:x] + "".join("#" if a == "#" or b == "#" else "." for a, b in
                                                  zip(r, rows[yy][x:x + len(r)])) + rows[yy][x + len(r):]
        x += len(glyph[0])
    px = pixels(rows, w + 1)
    return [[row[i * 16:i * 16 + 16] for row in px] for i in range(ncells)]


def build_font(code_of, orig, cells=None):
    """code_of: {ascii: game code}; cells: {code: 16x16 grid} for menu words; orig: the original decompressed
    block, whose 32 bytes past the 0x3000 of tiles are the BG3 palette. Returns the raw 12320-byte font."""
    g = load_glyphs()
    font = bytearray(0x3000) + orig[0x3000:FONT_SIZE]

    def put(tile, data):
        font[tile * 16:tile * 16 + 16] = data

    for ch, code in code_of.items():
        px = pixels(g[ch])
        b = base_tile(code)
        put(b, tile_bytes(px, 0))
        put(b + 16, tile_bytes(px, 8))
    for code, px in (cells or {}).items():
        b = base_tile(code)
        if b + 17 >= 0x300:
            raise ValueError("code %02X outside the 0x3000-byte font DMA" % code)
        put(b, tile_bytes(px, 0)); put(b + 1, tile_bytes(px, 0, 8))
        put(b + 16, tile_bytes(px, 8)); put(b + 17, tile_bytes(px, 8, 8))
    return bytes(font)

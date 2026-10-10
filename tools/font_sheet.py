"""Render the 16x16 BG3 font (2bpp, 8 glyphs per 32-tile row) from a VRAM dump as a labelled glyph sheet.
usage: font_sheet.py vram.bin out.png [chr_word_addr=0] [scale=3]"""
import sys

from PIL import Image, ImageDraw


def tile2bpp(vram, byte_addr):
    px = []
    for y in range(8):
        lo, hi = vram[byte_addr + 2 * y], vram[byte_addr + 2 * y + 1]
        px.append([((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1) for x in range(8)])
    return px


def glyph(vram, code, base=0):
    t = ((code & 0xF8) << 2) | ((code & 7) << 1)
    img = Image.new("L", (16, 16))
    for dy, dx, n in ((0, 0, t), (0, 8, t + 1), (8, 0, t + 16), (8, 8, t + 17)):
        for y, row in enumerate(tile2bpp(vram, base + n * 16)):
            for x, v in enumerate(row):
                img.putpixel((dx + x, dy + y), (0, 255, 170, 90)[v])
    return img


if __name__ == "__main__":
    vram = open(sys.argv[1], "rb").read()
    base = int(sys.argv[3], 16) * 2 if len(sys.argv) > 3 else 0
    sc = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    cell = 16 * sc + 14
    sheet = Image.new("L", (16 * cell, 16 * cell), 40)
    dr = ImageDraw.Draw(sheet)
    for c in range(256):
        g = glyph(vram, c, base).resize((16 * sc, 16 * sc), Image.NEAREST)
        x, y = (c % 16) * cell, (c // 16) * cell
        sheet.paste(g, (x, y + 12))
        dr.text((x + 1, y), "%02X" % c, fill=255)
    sheet.save(sys.argv[2])

"""One-off: dump the FNT resources of a Windows .fon (NE) bitmap font as ASCII art, to seed font/en_8x16.txt.
usage: fon2txt.py FONT.fon  -> prints each resource's size, then glyphs 0x20-0x7E of the one matching --w/--h"""
import struct
import sys


def fnt_resources(b):
    ne = struct.unpack_from("<H", b, 0x3C)[0]
    rt = ne + struct.unpack_from("<H", b, ne + 0x24)[0]
    shift = struct.unpack_from("<H", b, rt)[0]
    p = rt + 2
    while True:
        typ, cnt = struct.unpack_from("<HH", b, p)
        if typ == 0:
            return
        p += 8
        for _ in range(cnt):
            off, ln = struct.unpack_from("<HH", b, p)
            if typ == 0x8008:
                yield b[off << shift:(off << shift) + (ln << shift)]
            p += 12


def glyphs(f):
    ver = struct.unpack_from("<H", f, 0)[0]
    h = struct.unpack_from("<H", f, 0x58)[0]
    first, last = f[0x5F], f[0x60]
    tbl = 0x76 if ver == 0x200 else 0x94
    ent = 4 if ver == 0x200 else 6
    out = {}
    for i in range(last - first + 1):
        w = struct.unpack_from("<H", f, tbl + i * ent)[0]
        off = struct.unpack_from("<H" if ver == 0x200 else "<I", f, tbl + i * ent + 2)[0]
        rows = []
        for y in range(h):
            bits = 0
            for col in range((w + 7) // 8):
                bits = bits << 8 | f[off + col * h + y]
            rows.append("".join("#" if bits >> ((w + 7) // 8 * 8 - 1 - x) & 1 else "." for x in range(w)))
        out[first + i] = rows
    return h, out


if __name__ == "__main__":
    b = open(sys.argv[1], "rb").read()
    res = int(sys.argv[sys.argv.index("--res") + 1]) if "--res" in sys.argv else None
    for i, f in enumerate(fnt_resources(b)):
        h, g = glyphs(f)
        print("# resource", i, "height", h, "width", len(g[0x41][0]))
        if "--dump" in sys.argv and res in (None, i):
            for c in range(0x20, 0x7F):
                print("== %02X %s" % (c, chr(c)))
                print("\n".join(g[c]))

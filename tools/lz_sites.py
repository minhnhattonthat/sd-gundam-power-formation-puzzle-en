"""List every JSL $8383A3 call site with the compressed source it loads (from the LDA #/STA $0105/$0104 pair
before it), and the decompressed size. --vram FILE also reports blocks whose output matches the VRAM font area."""
import sys

import lz

ROM = sys.argv[1]
d = open(ROM, "rb").read()


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def sites():
    for i in range(len(d) - 4):
        if d[i:i + 4] == b"\x22\xa3\x83\x83":
            win = d[max(0, i - 40):i]
            bank = lo = None
            for k in range(len(win) - 5):
                if win[k] == 0xA9 and win[k + 3:k + 6] == b"\x8d\x05\x01":
                    bank = win[k + 2]
                if win[k] == 0xA9 and win[k + 3:k + 6] == b"\x8d\x04\x01":
                    lo = win[k + 1] | win[k + 2] << 8
            cpu = 0x800000 | (i >> 15) << 16 | 0x8000 | (i & 0x7FFF)
            yield cpu, (bank << 16 | lo) if bank is not None and lo is not None else None


if __name__ == "__main__":
    vram = open(sys.argv[sys.argv.index("--vram") + 1], "rb").read()[:0x3000] if "--vram" in sys.argv else None
    for cpu, src in sites():
        if src is None:
            print("%06X  source not found" % cpu)
            continue
        out, used = lz.decompress(d, off(src))
        tag = ""
        if vram:
            same = sum(1 for a, b in zip(out, vram) if a == b)
            tag = " vram-match %.2f" % (same / max(1, min(len(out), len(vram))))
        print("%06X  src %06X (file %06X) packed %5d -> %5d%s" % (cpu, src, off(src), used, len(out), tag))

"""Heuristic scan for strings in the game font encoding: runs of mostly-kana bytes ending in FE/FF.
usage: scan_jp.py ROM [minlen=4]"""
import sys

from tbl import Table

KANA = set(range(0x01, 0x31)) | set(range(0x40, 0x5C)) | set(range(0x80, 0x9F)) | set(range(0xA5, 0xAF))
d = open(sys.argv[1], "rb").read()
minlen = int(sys.argv[2]) if len(sys.argv) > 2 else 4
t = Table.load(__file__.replace("tools\\scan_jp.py", "tbl/jp.tbl").replace("tools/scan_jp.py", "tbl/jp.tbl"))
i = 0
while i < len(d):
    j = i
    while j < len(d) and (d[j] in KANA or d[j] in (0xFE, 0x00) or 0x31 <= d[j] <= 0x7C or 0xA0 <= d[j] <= 0xB2):
        j += 1
    run = d[i:j]
    kana = sum(1 for b in run if b in KANA)
    if j < len(d) and d[j] == 0xFF and kana >= minlen and kana >= 0.6 * len(run) and 0xFE in run + b"\xfe":
        print("%06X %s" % (i, t.decode(d, i, j - i + 1)[0]))
    i = j + 1

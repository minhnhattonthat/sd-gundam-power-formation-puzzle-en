"""Split a ROM range into FF-terminated strings and look for 16-bit pointer tables that point at their starts."""
import sys

d = open(sys.argv[1], 'rb').read()
lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
starts = [lo]
for i in range(lo, hi):
    if d[i] == 0xFF:
        starts.append(i + 1)
print('strings', len(starts), 'first', [hex(s) for s in starts[:6]])
cpu = [(s & 0x7FFF) | 0x8000 for s in starts[:4]]
for want in cpu[1:3]:
    pat = want.to_bytes(2, 'little')
    print(hex(want), [hex(i) for i in range(len(d)) if d.startswith(pat, i)][:40])

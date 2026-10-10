"""LZSS codec for the game's decompressor at $83:83A3.

Stream: byte 0 unused (kept as-is), u16 item count N, then flag bytes (LSB first, 8 items each, last one N&7).
Flag 1 = literal byte. Flag 0 = match: lo, hi[, ext]: distance = ((hi & 0x0F) << 8 | lo) + 1 back from the output end,
length = (hi >> 4) + 2, or ext + 0x12 when hi >> 4 == 0. Copies run forward, so overlaps repeat like LZ77.
The 65816 loop mishandles N >> 3 with a zero low byte, so compress() avoids those item counts."""

MAX_DIST = 0x1000
MAX_LEN = 0xFF + 0x12


def decompress(d, pos=0):
    """Returns (output bytes, compressed length)."""
    start = pos
    n = d[pos + 1] | d[pos + 2] << 8
    pos += 3
    out = bytearray()
    for i in range(n):
        if i % 8 == 0:
            flags = d[pos]; pos += 1
        if flags >> (i % 8) & 1:
            out.append(d[pos]); pos += 1
            continue
        lo, hi = d[pos], d[pos + 1]
        dist = ((hi & 0x0F) << 8 | lo) + 1
        if hi >> 4:
            ln = (hi >> 4) + 2; pos += 2
        else:
            ln = d[pos + 2] + 0x12; pos += 3
        for _ in range(ln):
            out.append(out[-dist])
    return bytes(out), pos - start


def _items(data):
    """Greedy LZ parse with a hash chain; returns list of ('lit', b) / ('m', dist, len)."""
    items, i, heads = [], 0, {}
    while i < len(data):
        best_len, best_dist = 0, 0
        if i + 2 < len(data):
            for j in reversed(heads.get(data[i:i + 3], [])):
                if i - j > MAX_DIST:
                    break
                ln = 0
                while ln < MAX_LEN and i + ln < len(data) and data[j + ln] == data[i + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_dist = ln, i - j
                    if ln == MAX_LEN:
                        break
        step = best_len if best_len >= 3 else 1
        for k in range(i, i + step):
            if k + 2 < len(data):
                heads.setdefault(data[k:k + 3], []).append(k)
        if best_len >= 3:
            items.append(("m", best_dist, best_len))
        else:
            items.append(("lit", data[i]))
        i += step
    return items


def compress(data, head=0):
    items = _items(bytes(data))
    while (len(items) >> 3) & 0xFF == 0:
        # split the last match (or last literal run) to change the item count
        k = max(i for i, it in enumerate(items) if it[0] == "m" and it[2] >= 6) if any(
            it[0] == "m" and it[2] >= 6 for it in items) else None
        if k is None:
            raise ValueError("cannot adjust item count")
        _, dist, ln = items[k]
        items[k:k + 1] = [("m", dist, 3), ("m", dist, ln - 3)]
    out = bytearray([head]) + len(items).to_bytes(2, "little")
    for g in range(0, len(items), 8):
        chunk, flags, body = items[g:g + 8], 0, bytearray()
        for b, it in enumerate(chunk):
            if it[0] == "lit":
                flags |= 1 << b; body.append(it[1])
            else:
                _, dist, ln = it
                dd = dist - 1
                if ln <= 17:
                    body += bytes([dd & 0xFF, (dd >> 8) | (ln - 2) << 4])
                else:
                    body += bytes([dd & 0xFF, dd >> 8, ln - 0x12])
        out.append(flags); out += body
    return bytes(out)


if __name__ == "__main__":
    import os
    import sys
    rom = open(sys.argv[1], "rb").read()
    off = int(sys.argv[2], 16)
    dec, used = decompress(rom, off)
    print("decompressed %d bytes from %d" % (len(dec), used))
    re = compress(dec, rom[off])
    assert decompress(re)[0] == dec
    print("recompressed %d bytes" % len(re))

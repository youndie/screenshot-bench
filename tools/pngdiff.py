#!/usr/bin/env python3
"""Compare two directories of goldens pixel by pixel, independent of any tool's own tolerance.

    tools/pngdiff.py linux/viddik mac/viddik

For each PNG present in both: how many pixels differ at all, and the largest single-channel
difference. Standard library only (zlib), so it runs on either machine as is.
"""
import struct
import sys
import zlib
from pathlib import Path


def decode(path):
    data = Path(path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    pos, idat, w = 8, b"", 0
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            w, h, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and interlace == 0, f"{path}: depth {depth}, interlace {interlace}"
            bpp = {6: 4, 2: 3, 0: 1, 4: 2}[color]
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 0xFF
            elif f == 2:
                line[i] = (line[i] + b) & 0xFF
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
        rows.append(bytes(line))
        prev = line
    # Normalise to RGB so an RGBA golden and an RGB one of the same picture compare equal.
    rgb = []
    for line in rows:
        for x in range(w):
            px = line[x * bpp:(x + 1) * bpp]
            rgb.append(tuple(px[:3]) if bpp >= 3 else (px[0],) * 3)
    return w, h, rgb


def compare(a, b):
    wa, ha, pa = decode(a)
    wb, hb, pb = decode(b)
    if (wa, ha) != (wb, hb):
        return None, None, wa * ha
    differ = maxdelta = 0
    for x, y in zip(pa, pb):
        if x != y:
            differ += 1
            maxdelta = max(maxdelta, max(abs(i - j) for i, j in zip(x, y)))
    return differ, maxdelta, wa * ha


def main(left, right):
    names = sorted(p.name for p in Path(left).rglob("*.png"))
    rows = []
    for name in names:
        other = next(Path(right).rglob(name), None)
        if other is None:
            continue
        mine = next(Path(left).rglob(name))
        differ, delta, total = compare(mine, other)
        rows.append((name, differ, delta, total))
    identical = sum(1 for r in rows if r[1] == 0)
    worst = max(rows, key=lambda r: -1 if r[1] is None else r[1])
    shares = sorted(r[1] / r[3] * 100 for r in rows if r[1] is not None)
    median = shares[len(shares) // 2] if shares else 0
    print(f"{left}: {len(rows)} compared, {identical} identical, median {median:.3f}% px differ, "
          f"worst {worst[0]} {worst[1]} px ({worst[1] / worst[3] * 100:.3f}%), max channel delta "
          f"{max(r[2] or 0 for r in rows)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

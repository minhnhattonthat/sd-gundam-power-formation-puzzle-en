"""Summarise a romreads.lua log: per reading PC, how many ROM bytes it touched, over which frames and offsets.
Text-reading PCs show up as many distinct frames with a slowly advancing offset."""
import sys
from collections import defaultdict

by_pc = defaultdict(list)
for line in open(sys.argv[1]):
    if not line[0].isdigit():
        continue
    f, off, pc = line.split()
    by_pc[pc].append((int(f), int(off, 16)))
rows = []
for pc, v in by_pc.items():
    frames = {f for f, _ in v}
    rows.append((len(frames), pc, len(v), min(o for _, o in v), max(o for _, o in v), min(frames), max(frames)))
for r in sorted(rows, reverse=True)[: int(sys.argv[2]) if len(sys.argv) > 2 else 25]:
    print("frames=%4d pc=%s bytes=%5d off=%06X-%06X f=%d-%d" % r)

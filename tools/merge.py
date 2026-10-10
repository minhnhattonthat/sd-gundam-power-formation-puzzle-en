"""Merge translations/<batch>.json ({id: en}) into script/*.json. Refuses unknown ids; prints lint errors for the
merged entries but still writes (the lint/check is the gate).
usage: merge.py translations/batch01.json [...]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ("briefing", "prologue", "options")

data = {n: json.loads((ROOT / "script" / (n + ".json")).read_text(encoding="utf-8")) for n in FILES}
by_id = {e["id"]: e for n in FILES for e in data[n]}
for path in sys.argv[1:]:
    tr = json.loads(Path(path).read_text(encoding="utf-8"))
    unknown = sorted(set(tr) - set(by_id))
    if unknown:
        sys.exit("unknown ids in %s: %s" % (path, " ".join(unknown)))
    for k, v in tr.items():
        by_id[k]["en"] = v
    print("merged %d from %s" % (len(tr), path))
for n in FILES:
    (ROOT / "script" / (n + ".json")).write_text(json.dumps(data[n], ensure_ascii=False, indent=1) + "\n",
                                                 encoding="utf-8")

"""Write the reviewer pairs file: every entry as `>> id [kind] | JP` then the EN lines, in game order.
usage: pairs.py OUT.txt"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = []
for name in ("prologue", "briefing", "options"):
    for e in json.loads((ROOT / "script" / (name + ".json")).read_text(encoding="utf-8")):
        out.append(">> %s [%s] | %s" % (e["id"], e["kind"], e["jp"].replace("{br}", " / ").replace("{end}", "")))
        out += ["   " + ln for ln in e["en"].split("\n")]
        out.append("")
Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("wrote", sys.argv[1], len(out), "lines")

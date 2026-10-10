"""Text lint for script/*.json English. Prints errors and a count; exit 1 on any error.
Rules: encodable ASCII, no Japanese, width per line, lines per string, options fit their pre-render budget,
glossary (JP term present -> one of its EN forms present; Avoid spellings absent)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
from tbl import Table  # noqa: E402

JP = Table.load(ROOT / "tbl" / "jp.tbl")
WIDTH = 26
MAX_LINES = {"mission": 15, "ending": 11, "prologue": 8}  # tilemap rows: see docs/re/README.md
JP_CHARS = re.compile(r"[　-ヿ一-鿿＀-￯]")


def glossary_rows():
    rows = []
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and line.startswith("|") and not set(cells[0]) <= set("-") and cells[0] != "JP":
            rows.append((cells[0].split(" / "), [e for e in cells[1].split(" / ") if e], cells[-1]))
    return rows


def lint_entry(e, rows):
    errs, en, kind = [], e.get("en", ""), e["kind"]
    if not en:
        return ["untranslated"]
    if JP_CHARS.search(en):
        errs.append("Japanese characters in en")
    bad = sorted({c for c in en if not (" " <= c <= "~" or c == "\n")})
    if bad:
        errs.append("non-ASCII/unencodable %r" % "".join(bad))
    if kind == "option":
        budget = 16 * len(JP.encode(e["jp"]))
        if font.menu_width(en) > budget:
            errs.append("menu word %d px > %d" % (font.menu_width(en), budget))
        return errs
    lines = en.split("\n")
    for i, ln in enumerate(lines):
        if len(ln) > WIDTH:
            errs.append("line %d is %d chars > %d: %r" % (i, len(ln), WIDTH, ln))
        if ln != ln.rstrip():
            errs.append("line %d has trailing space" % i)
    if len(lines) > MAX_LINES[kind]:
        errs.append("%d lines > %d" % (len(lines), MAX_LINES[kind]))
    flat, jp = " ".join(lines), e["jp"].replace("{br}", "")
    for jps, ens, avoid in rows:
        if any(j and j in jp for j in jps) and ens and not any(x in flat for x in ens):
            errs.append("glossary: %s -> needs %s" % (jps[0], " / ".join(ens)))
        for a in (x.strip() for x in avoid.split(",")):
            if a and re.search(r"\b%s\b" % re.escape(a), flat):
                errs.append("glossary: avoid %r" % a)
    return errs


def lint():
    rows, errors = glossary_rows(), []
    for name in ("briefing", "prologue", "options"):
        for e in json.loads((ROOT / "script" / (name + ".json")).read_text(encoding="utf-8")):
            errors += ["%s: %s" % (e["id"], m) for m in lint_entry(e, rows)]
    return errors


if __name__ == "__main__":
    errs = lint()
    print("\n".join(errs))
    print("lint: %d error(s)" % len(errs))
    sys.exit(1 if errs else 0)

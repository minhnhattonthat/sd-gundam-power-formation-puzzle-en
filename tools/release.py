"""Release: check -> build -> checksum -> BPS (re-applied and verified) -> README -> zip (patch + README only).
Local only: never uploads. usage: release.py [VERSION]  (default 0.1)"""
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = [sys.executable, "-X", "utf8"]
SKILL = ROOT / ".claude" / "skills" / "translate-retro-game" / "scripts"
ORIG = ROOT / "rom" / "SD Gundam - Power Formation Puzzle (Japan).sfc"
VER = sys.argv[1] if len(sys.argv) > 1 else "0.1"
OUT = ROOT / "release"
NAME = "SD_Gundam_Power_Formation_Puzzle_EN_v%s" % VER


def run(*cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True, cwd=ROOT)


def hashes(b):
    return "CRC32 %08X, MD5 %s, SHA-1 %s" % (zlib.crc32(b), hashlib.md5(b).hexdigest(), hashlib.sha1(b).hexdigest())


run(*PY, "build.py", "english")
run(*PY, "tools/check.py")
OUT.mkdir(exist_ok=True)
rom = OUT / (NAME + ".sfc")
run(*PY, SKILL / "bps.py", "snes-checksum", ROOT / "build" / "sdgundam_en.sfc", "--out", rom)
bps = OUT / (NAME + ".bps")
run(*PY, SKILL / "bps.py", "make", ORIG, rom, bps)
check = OUT / "reapplied.sfc"
run(*PY, SKILL / "bps.py", "apply", ORIG, bps, check)
assert check.read_bytes() == rom.read_bytes(), "re-applied patch differs"
check.unlink()
smoke = subprocess.run([*PY, SKILL / "emu.py", rom, "--out", ROOT / "work" / "qa" / "release_smoke", "--route",
                        ROOT / "tools" / "routes" / "boot.txt", "--smoke"], cwd=ROOT)
assert smoke.returncode == 0, "smoke failed"

o, p = ORIG.read_bytes(), rom.read_bytes()
readme = (ROOT / "docs" / "README_release.txt").read_text(encoding="utf-8").format(
    version=VER, orig=ORIG.name, orig_size=len(o), orig_hash=hashes(o), patched_size=len(p), patched_hash=hashes(p),
    bps=bps.name)
(OUT / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
z = OUT / (NAME + ".zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(bps, bps.name)
    zf.write(OUT / "README.txt", "README.txt")
print("release ready:", z)

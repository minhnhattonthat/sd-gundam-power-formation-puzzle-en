# SD Gundam Power Formation Puzzle - English patch (SNES)

Unofficial fan translation of *SD Gundam - Power Formation Puzzle* (Super Famicom, Bandai, 1996), with the tools that built it.
**No ROM is included.** Patch your own dump.

## Download and patch
1. Grab the zip from [Releases](../../releases) (patch + README only).
2. Base ROM: `SD Gundam - Power Formation Puzzle (Japan).sfc`, 1,048,576 bytes, CRC32 `87E4476D`,
   SHA-1 `43be07a1eda1563e99343bb6b349e251b576b69d`.
3. Apply the `.bps` with Flips, beat or Rom Patcher JS. The result is a 2 MiB ROM.
4. Tested in Mesen2 on a cold boot (don't use old savestates).

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Intro text | Translated |
| Story-mode mission briefings (45, three teams) | Translated |
| Endings (all 8) | Translated |
| Options menu and boot copyright screen | Translated |
| Title menu, unit select, stage select, battle | English in the original |

New 8x16 font (26 characters per line); finished briefings stay up a few seconds longer.

Known issues: none known; [report one](../../issues/new/choose).

## Building from source
Needs Python 3.10+ (+ Pillow, pytest), [asar](https://github.com/RPGHacker/asar) in `tools/asar/`, and Mesen2 in `tools/mesen2/` for emulator QA.
Put the original ROM in `rom/`.

```
python -X utf8 build.py english      # -> build/sdgundam_en.sfc
python -X utf8 tools/check.py        # identity build, roundtrips, lint, ROM diff, leftover-Japanese scan
python -X utf8 tools/release.py 0.1  # patch + verification + zip (local only)
```

Layout: `script/` text (JP + EN), `translations/` merge inputs, `tbl/` tables, `font/` glyph sources, `asm/main.asm` engine patch,
`docs/re/README.md` reverse-engineering notes, `glossary.md` terms.

## Credits and notes
Produced with AI assistance (Claude) under the direction of the patch author. The glyph sources in `font/` were seeded from Windows bitmap fonts.
Game (C) Sotsu Agency, Sunrise, TV Asahi, Bandai. Unofficial; not affiliated with or endorsed by the rights holders.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

# SD Gundam Power Formation Puzzle (SFC) English translation

Skill: translate-retro-game (H:/translation/sd-gundam-power-formation-puzzle-claude/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.
Independent of the sibling repo ../sd-gundam-power-formation-puzzle: never read its files (user ruling, A/B comparison).

## Commands (run from repo root)
- Build:    `python -X utf8 build.py english`  -> build/sdgundam_en.sfc (also `identity`, `marker`)
- Check:    `python -X utf8 tools/check.py`  (pytest: identity, roundtrip, LZ, lint, build fits; pre-commit runs it)
- Lint:     `python -X utf8 tools/lint.py`; merge translations: `python -X utf8 tools/merge.py translations/<f>.json`
- Smoke:    `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py build/sdgundam_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)

## Paths
- Original ROM: `rom/SD Gundam - Power Formation Puzzle (Japan).sfc` (CRC32 87E4476D). Mesen2: `tools/mesen2/`, asar: `tools/asar/`.
- Text: `script/{briefing,prologue,options}.json` (jp + en). Translations land via `translations/*.json`.
- Tables `tbl/`, fonts `font/` (8x16 text, 13 px menu), engine patch `asm/main.asm`, RE notes `docs/re/README.md`.
- Routes: title -> story: `--route-str "700 -;6 start;120 -;6 a" --mash 60` reaches MISSION 1 at ~1440 (save state at 1380,
  before the font loads). Intro prologue plays from boot (~400-1300). Options: title, down x3, start.

## Rulings
- Official Gundam terms, no honorifics, English credits, full words; routine decisions pre-approved. gpt-6-astra OK for reviews.
- English layout: 8x16 font, 26 chars/line (briefings/endings/prologue); options words pre-rendered per JP cell budget.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update the Status section.

## Gotchas
- Font block (LZ $9D:ACB4) ends with the BG3 palette (32 bytes past 0x3000): keep it.
- asar picks immediate width from the literal: use `lda.w #N` in 16-bit code.
- Savestates past the briefing font load keep the old font: regenerate from cold boot after font/asm changes.

## Status
- Done: RE, identity build, extraction, engine (briefing/ending/prologue/options/copyright), translation + gpt-6-astra
  review (fixes applied), in-emulator QA of briefing, prologue, options, copyright, 4 ending variants
  (tools/lua/force_ending.lua), romdiff + JP scan in check, local v0.1 release in release/ (not published).
- Open: "CV Zanscare" faction reading unverified in-game (B33-35). User playtest pending.

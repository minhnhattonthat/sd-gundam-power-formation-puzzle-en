# Translation reviewer brief - SD Gundam Power Formation Puzzle (SFC, 1996)

You review a JP->EN fan translation. Read-only: no edits to repo files, no git, no subagents. Mechanical validity
(width <= 26 chars/line, ASCII, glossary spellings) is already enforced by `tools/lint.py` - judge translation quality.
Write your report to the path given in your dispatch (that file only).

## Inputs
- Pairs file (path in dispatch): `>> id [kind] | JP` (` / ` = JP line break) followed by the EN lines. Read ALL of it.
- `glossary.md` (rulings at the top; binding names/terms).

## Game context
- Falling-block puzzle battle game. Story mode: the player picks a team (Gundam Team, G Gundam Team, Gundam W Team);
  before each battle a timed narration ("mission briefing") types out under a MISSION n banner, then holds ~4 s.
- B00-B38 [mission]: 15 briefings per team. Most come in triples (same text, team name differs: B00/B01/B02 etc).
  B21, B22, B23 are shared by all teams (the OZ secret-weapon fights). B24-B38 are the branch taken after a loss.
- B39-B46 [ending]: endings. B41/B42 are rough, hot-blooded first person (G Gundam-style bravado). B46 is the bad end.
- P00 [prologue]: intro text crawl over a space scene.
- O00-O19 [option]: options menu words (Difficulty/Kids Mode values share Normal/Strong/Weak). Each word must fit
  a fixed pixel budget; don't propose longer words unless clearly necessary, and say so.
- Known uncertainty: "ＣＶ・サンス[7B]ール軍" ([7B] is a second ガ glyph) is read as ザンスカール (Zanscare, font lacks
  ザ) + CV (Crossbone Vanguard). Give your view.

## Judge
- Accuracy: mistranslation, omission, addition, reversed meaning. Quote the JP and say what it means.
- Consistency: glossary names/terms exactly; the three team variants of a triple must stay parallel.
- Things users caught that reviewers missed: wordplay losing punch, near-miss name spellings, abbreviations,
  awkward stock phrases, odd tense mixing within one briefing.
- Naturalness: would a fan-translation reader stumble? Lines are max 26 chars; keep paragraph breaks.

## Report
### Issues
#### Critical (meaning reversed, wrong team/faction)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN` (suggested EN with `/` for line breaks, each line <= 26 chars).
### Assessment
Approved | Needs fixes - one sentence why.

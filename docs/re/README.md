# RE notes: SD Gundam Power Formation Puzzle (SFC, 1996 Bandai)

ROM: `SD Gundam - Power Formation Puzzle (Japan).sfc`, 1 MiB LoROM (map $20, no SRAM), CRC32 87E4476D,
SHA-1 43be07a1eda1563e99343bb6b349e251b576b69d, MD5 c2259a02049fdc4ea05a0b8d98989df6. Header checksum valid.
Most UI (title menu, unit select, stage select, battle) is already English graphics. Japanese text is small.

## Text encoding (`tbl/jp.tbl`)
- One byte per glyph = index into a 16x16 font (2bpp, BG3). Glyph c uses tiles B, B+1, B+16, B+17 with
  B = ((c & F8) << 2) | ((c & 7) << 1). 00 = space (prologue), 01-2E hiragana in gojuon order, then a fixed
  kanji/katakana/latin subset up to B2. 7B duplicates ガ (56). FE = newline / item separator, FF = end.
- Font: LZ block `$9D:ACB4` (file 0xEACB4, 7764 bytes packed -> 12320), loaded by JSL $8383A3 at
  83:9D11 (briefing), 83:DA6B (prologue), 83:EFC6 (options?). DMA'd from $7F0000 to VRAM $0000.

## LZ compression (`tools/lz.py`)
- Decompressor $83:83A3; args in DP $0100: src 24-bit at $0104, dest at $0107. Format in `tools/lz.py`.
  `tools/lz_sites.py ROM` lists all 68 call sites and their sources.
- Loop bug: item count N with (N>>3)&0xFF == 0 misbehaves; compressor avoids it.

## Text sites
| What | Data | Pointers | Renderer |
|---|---|---|---|
| Mission briefings (3 teams x 15) | bank $9D file 0xE8000-0xE8B46 (39 strings) | 24-bit table $83:9B1C/9B49/9B76 (file 0x19B1C, 3x15), index team=$7FFF00, mission=$45 | typed, $83:998A |
| Endings (8) | same block 0xE88C1-0xE8B46 | 16-bit, bank from `PEA $9D00`: $83:D0CA (2x2 -> D0CE/D0D2), $83:A90B (3), `LDX #$8B0B` at $83:A8F0 | instant, $83:D8DD |
| Prologue | `$9F:C4C0` (file 0xFC4C0), 00 = space | `LDX #$C4C0` at $83:DA84 (bank PEA $9F00) | $83:D8DD, VRAM $6B86 |
| Options menu | `$9F:F79F` (file 0xFF79F) FE-separated items, FF end | param block $83:F0DA (bank,ptr,dest $7F:0000) | $83:D94D -> RAM buffer, 2 entries/char |

## Briefing renderer ($83:998A, task started from $83:9ACA)
- BG3, mode 1, `$2105 = #$49` at $83:990B (BG3 16x16 tiles). Tilemap VRAM $2000. Start `$2B = #$2003` ($83:9B04),
  per-char wait `$25 = 8` frames ($83:9AFE), scroll speed `$27 = 4`, lines before scroll `$29 = 4`.
- Each char: one tilemap word at $14 (INC). FE: `$2B += $20` ($83:9A09). Wait/scroll at $83:9A2C.
- $83:9A63: once `$2B & #$5080` (line >= 4) typing speeds to 1 frame/char and scroll doubles.
- BG3 masked by window 1 above scanline 136 (IRQ at $83:9BA3 clears $2124), so text shows only in the bottom band.
- Briefing is timed: no input needed, auto-advances to the battle.

## Ending/prologue renderer ($83:D8DD)
- Y = VRAM tilemap address, X = string (DB = bank). 8x8 BG tiles: each char writes B,B+1 then B+16,B+17 on the
  next row; `$49` char index (col = $49*2). FE: `$47 += $60` (24 px line).

## Tools
- `tools/dis65816.py ROM ADDR [N] --m16 --x16`: quick disassembler. `tools/font_sheet.py vram.bin out.png`.
- Lua: `tools/lua/romreads.lua` (ROM data reads per PC), `dma_log.lua`, `watch_write.lua`, `dump_ppu.lua`.

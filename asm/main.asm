; English engine patches. Applied by build.py with asar after the text/font data is inserted.
; Font: each code is an 8x16 glyph in tiles B (top) and B+16 (bottom), B = ((c&F8)<<2)|((c&7)<<1); see tools/font.py.
lorom

; ---------------------------------------------------------------------------
; Mission briefing ($83:998A): BG3 to 8x8 tiles, one 8 px column per char, two tilemap rows per 16 px line.
org $83990B
    db $09                      ; $2105: mode 1, BG3 priority, BG3 8x8 tiles (was $49)
org $8399D3
    jsl brief_putc              ; replaces LDA $14 / INC $14 / STA $2116 / LDA $20 / STA $2118
    nop #8
org $839A09
    dw $0040                    ; next line: two tilemap rows (was $20)
org $839A67
    dw $0100                    ; "line >= 4" test for the speed-up, with the doubled row stride (was $5080)
org $839AFE
    dw $0004                    ; frames per char while typing (was 8): English has ~2x the glyphs
org $839A14
    jsl brief_end_hold          ; FF handler: hold the finished text before hiding it (was SEP #$20 / STZ $2112)
    nop

; ---------------------------------------------------------------------------
; Ending/prologue writer ($83:D8DD): one 8 px column per char instead of two.
org $83D909
    nop                         ; col = $49 (was $49*2)
org $83D916
    nop #4                      ; drop the right half of the top row
org $83D92B
    nop #4                      ; drop the right half of the bottom row

; Start columns: 3 instead of 6, so 26 English chars span x 24-231 (JP: 11 wide chars from col 6).
org $83A8F9
    dw $6803                    ; endings via $83:A90B / LDX #$8B0B (was $6806)
org $83D0B8
    dw $4803                    ; endings via $83:D0CA (was $4806)
org $83DA88
    dw $6B83                    ; prologue (was $6B86)

; Text banks: endings (PEA $9D00) and prologue (PEA $9F00) now live in the English text bank $A0.
org $83A8F4
    dw $A000
org $83D0B3
    dw $A000
org $83DA80
    dw $A000

; ---------------------------------------------------------------------------
org $A18000
brief_putc:                     ; A16. $14 = tilemap word address, $20 = tile entry for glyph top
    lda $14
    sta $2116
    lda $20
    sta $2118
    lda $14
    clc
    adc #$0020
    sta $2116
    lda $20
    clc
    adc #$0010
    sta $2118
    inc $14
    rtl

!BRIEF_HOLD = 240               ; frames the finished briefing stays up (the original hid it ~15 frames after)
brief_end_hold:                 ; A16, runs inside the briefing task; $1A (per-char wait counter) is free here
    lda.w #!BRIEF_HOLD
    sta $1A
.wait
    lda.w #$0002
    sta $2124                   ; re-arm the BG3 window mask each frame like the typing loop (IRQ clears it at
    lda.w #$0001                ; line 136); otherwise scrolled-out rows wrap into view at the top
    jsl $8387C6                 ; task wait 1 frame
    dec $1A
    bne .wait
    sep #$20
    stz $2112
    rtl

-- Count executions of the briefing IRQ handler ($83:9BA3) and log $2105/$2124 writes with scanline.
local n = 0
L.on_exec(0x839BA3, 0x839BA3, function() n = n + 1 end)
for _, reg in ipairs({ 0x2105, 0x2124, 0x212C, 0x212E, 0x2111, 0x2112 }) do
  L.on_write(reg, reg, function(a, v)
    if L.frame >= 200 and L.frame <= 201 then
      local s = emu.getState()
      L.log(string.format("f%d sl%d W %04X=%02X pc=%02X%04X", L.frame, s["ppu.scanline"] or -1, a, v, s["cpu.k"], s["cpu.pc"]))
    end
  end)
end
L.on_frame(function(f) if f % 100 == 0 then L.log("frame " .. f .. " irq " .. n) end end)

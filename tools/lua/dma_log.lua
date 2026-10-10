-- Log every general DMA ($420B) as: frame pc ch src(24) size bbus vramaddr
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
emu.addMemoryCallback(L.safe(function(addr, value)
  local s = emu.getState()
  for ch = 0, 7 do
    if value & (1 << ch) ~= 0 then
      local b = 0x4300 + ch * 16
      local src = rd(b + 2) | rd(b + 3) << 8 | rd(b + 4) << 16
      local size = rd(b + 5) | rd(b + 6) << 8
      L.log(string.format("%d %02X%04X ch%d src=%06X size=%04X bbus=21%02X vram=%04X", L.frame,
        s["cpu.k"], s["cpu.pc"], ch, src, size, rd(b + 1), s["ppu.vramAddress"]))
    end
  end
end), emu.callbackType.write, 0x420B, 0x420B, emu.cpuType.snes, emu.memType.snesMemory)

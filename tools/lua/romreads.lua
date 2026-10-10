-- Log ROM data reads (not opcode fetches) between frames RR_LO..RR_HI as "first_frame file_off pc" lines.
-- Use: emu.py ... --script tools/lua/romreads.lua (edit RR_LO/RR_HI below or prepend globals).
RR_LO = RR_LO or 800
RR_HI = RR_HI or 1400
local seen = {}
emu.addMemoryCallback(L.safe(function(addr)
  if L.frame < RR_LO or L.frame > RR_HI then return end
  if (addr & 0xFFFF) < 0x8000 or (addr >> 16) & 0x7F >= 0x7E then return end
  local off = L.rom_off(addr)
  if not seen[off] then
    seen[off] = true
    L.log(string.format("%d %06X %06X", L.frame, off, emu.getState()["cpu.k"] << 16 | emu.getState()["cpu.pc"]))
  end
end), emu.callbackType.read, 0, 0xFFFFFF, emu.cpuType.snes, emu.memType.snesMemory)

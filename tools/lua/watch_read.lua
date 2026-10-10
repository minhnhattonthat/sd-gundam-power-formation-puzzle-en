-- Log the first read of each address in WR_LO..WR_HI (CPU addresses) with PC: "frame addr pc".
WR_LO = WR_LO or 0x7F0000
WR_HI = WR_HI or 0x7F01FF
local seen = {}
emu.addMemoryCallback(L.safe(function(addr)
  if seen[addr] then return end
  seen[addr] = true
  local s = emu.getState()
  L.log(string.format("%d %06X %02X%04X", L.frame, addr, s["cpu.k"], s["cpu.pc"]))
end), emu.callbackType.read, WR_LO, WR_HI, emu.cpuType.snes, emu.memType.snesMemory)

-- Log writes to WW_ADDR (after frame WW_FROM) with PC and the top of the stack (to find the caller).
WW_ADDR = WW_ADDR or 0x7F0000
WW_FROM = WW_FROM or 0
emu.addMemoryCallback(L.safe(function(addr, value)
  if L.frame < WW_FROM then return end
  local s = emu.getState()
  local t = {}
  for i = 1, 16 do t[#t + 1] = string.format("%02X", emu.read(s["cpu.sp"] + i, emu.memType.snesMemory)) end
  L.log(string.format("%d W %06X=%02X pc=%02X%04X stack %s", L.frame, addr, value, s["cpu.k"], s["cpu.pc"], table.concat(t, " ")))
end), emu.callbackType.write, WW_ADDR, WW_ADDR, emu.cpuType.snes, emu.memType.snesMemory)

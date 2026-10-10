-- On executing EP_ADDR, log frame, registers, DP bytes EP_DP..EP_DP+15 and 6 stack bytes (JSL/JSR return address).
EP_ADDR = EP_ADDR or 0x8382F1
EP_DP = EP_DP or 0x47
EP_FROM = EP_FROM or 0
L.on_exec(EP_ADDR, EP_ADDR, function()
  if L.frame < EP_FROM then return end
  local s = emu.getState()
  local m, st = {}, {}
  local d = s["cpu.d"]
  for i = 0, 15 do m[#m + 1] = string.format("%02X", emu.read(d + EP_DP + i, emu.memType.snesMemory)) end
  for i = 1, 6 do st[#st + 1] = string.format("%02X", emu.read(s["cpu.sp"] + i, emu.memType.snesMemory)) end
  L.log(string.format("%d A=%04X X=%04X Y=%04X DB=%02X dp[%02X]=%s stack=%s", L.frame, s["cpu.a"], s["cpu.x"], s["cpu.y"],
    s["cpu.dbr"], EP_DP, table.concat(m, " "), table.concat(st, " ")))
end)

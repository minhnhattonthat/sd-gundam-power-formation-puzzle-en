-- QA: jump straight to the story-mode ending dispatch ($83:B5A6) when the first mission scene starts ($83:9912,
-- a JSR'd scene function, so B5A6's tail returns to the main loop the same way).
-- Prepend globals: END_TEAM (0 Gundam, 1 G Gundam, 2 Gundam W), END_BRANCH ($7FFF02: 0 final, 1/2 OZ routes),
-- END_LOST ($7FFF06: 0 won, 1 lost).
local done = false
local function w16(a, v)
  emu.write(a, v & 0xFF, emu.memType.snesMemory)
  emu.write(a + 1, v >> 8, emu.memType.snesMemory)
end
L.on_exec(0x839912, 0x839912, function()
  if done then return end
  done = true
  w16(0x7FFF00, END_TEAM or 0)
  w16(0x7FFF02, END_BRANCH or 0)
  w16(0x7FFF06, END_LOST or 0)
  w16(0x7FFF0E, 8)
  local s = emu.getState()
  s["cpu.pc"] = 0xB5A6
  emu.setState(s)
  L.log("forced ending at frame " .. L.frame)
end)

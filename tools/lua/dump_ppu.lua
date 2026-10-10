-- At frame DUMP_AT: write ppu.txt (PPU state keys), vram.bin, cgram.bin, wram.bin into the --out dir.
DUMP_AT = DUMP_AT or 200
L.on_frame(function(f)
  if f ~= DUMP_AT then return end
  local s, keys = emu.getState(), {}
  for k, v in pairs(s) do if k:find("ppu") then keys[#keys + 1] = k .. "=" .. tostring(v) end end
  table.sort(keys)
  L.write_file(OUT .. "ppu.txt", table.concat(keys, "\n"))
  for name, mt in pairs({ vram = emu.memType.snesVideoRam, cgram = emu.memType.snesCgRam, wram = emu.memType.snesWorkRam }) do
    local t = {}
    for i = 0, emu.getMemorySize(mt) - 1 do t[#t + 1] = string.char(emu.read(i, mt)) end
    L.write_file(OUT .. name .. ".bin", table.concat(t))
  end
end)

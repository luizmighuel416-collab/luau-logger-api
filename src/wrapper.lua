-- Wrapper para executar o logger.lua com código de entrada
local input_file = arg[1]
if not input_file then
    print("Usage: luau wrapper.lua <input.lua>")
    return
end

local f = io.open(input_file, "r")
if not f then
    print("Failed to open input file")
    return
end

local code = f:read("*a")
f:close()

-- Aqui injetamos o código no ambiente do logger e executamos
-- (isso depende de como o logger.lua expõe sua função principal)

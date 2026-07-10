-- Wrapper para executar logger.lua e retornar output no stdout
local input_file = arg[1]
if not input_file then
    print("Usage: luau wrapper.lua <input.lua>")
    return
end

local f = io.open(input_file, "r")
if not f then
    print("Failed to open input file: " .. tostring(input_file))
    return
end

local code = f:read("*a")
f:close()

-- Carrega o logger.lua no mesmo ambiente
local logger_path = debug.getinfo(1).source:match("@?(.-)/?[^/]+$") .. "/logger.lua"
local logger_f = io.open(logger_path, "r")
if not logger_f then
    logger_f = io.open("src/logger.lua", "r")
end
if not logger_f then
    print("Failed to open logger.lua")
    return
end

local logger_code = logger_f:read("*a")
logger_f:close()

-- Executa o logger.lua para definir todas as funcoes globais
local chunk, err = loadstring(logger_code)
if not chunk then
    print("Failed to load logger.lua: " .. tostring(err))
    return
end

chunk()

-- Agora q está definido, chamamos dump_string com o código
-- dump_string(source, output_file) -> se output_file for nil, retorna (true, result)
local ok, result = q.dump_string(code, nil)
if ok and result then
    print(result)
else
    print("Failed to dump: " .. tostring(result))
end

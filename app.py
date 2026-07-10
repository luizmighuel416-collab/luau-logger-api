from flask import Flask, request, jsonify
import os
import requests
import re
import subprocess
import tempfile

app = Flask(__name__)

LOGGER_LUA_PATH = os.path.join(os.path.dirname(__file__), "src", "logger.lua")


def run_revea_logger(code: str) -> str:
    if not os.path.exists(LOGGER_LUA_PATH):
        raise FileNotFoundError("logger.lua nao encontrado em src/logger.lua")

    with open(LOGGER_LUA_PATH, "r") as f:
        logger_code = f.read()

    # Salva o codigo em um arquivo temporario
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as code_file:
        code_file.write(code)
        code_file.flush()
        code_path = code_file.name

    # Cria o wrapper que le o arquivo via variavel de ambiente
    wrapper_lua = (
        logger_code + "\n\n"
        + "-- Le o codigo do arquivo temporario\n"
        + 'local code_path = os.getenv("REVEA_CODE_PATH")\n'
        + "if not code_path then\n"
        + '    print("REVEA_CODE_PATH nao definida")\n'
        + "    return\n"
        + "end\n"
        + "\n"
        + "local f = io.open(code_path, \"r\")\n"
        + "if not f then\n"
        + '    print("Failed to open: " .. tostring(code_path))\n'
        + "    return\n"
        + "end\n"
        + "\n"
        + "local code = f:read(\"*a\")\n"
        + "f:close()\n"
        + "\n"
        + "local ok, result = q.dump_string(code, nil)\n"
        + "if ok and result then\n"
        + "    print(result)\n"
        + "else\n"
        + '    print("Failed to dump: " .. tostring(result))\n'
        + "end\n"
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as tmp:
        tmp.write(wrapper_lua)
        tmp.flush()
        wrapper_path = tmp.name

    try:
        env = os.environ.copy()
        env["REVEA_CODE_PATH"] = code_path

        result = subprocess.run(
            ["luau", wrapper_path],
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        output = result.stdout if result.stdout else result.stderr
        return output
    finally:
        if os.path.exists(wrapper_path):
            os.unlink(wrapper_path)
        if os.path.exists(code_path):
            os.unlink(code_path)


def deobfuscate_revea(code):
    result = code

    def unescape_hex(match):
        hex_str = match.group(1)
        try:
            cleaned = hex_str.replace('\\x', '')
            decoded = bytes.fromhex(cleaned).decode('utf-8', errors='ignore')
            return f'"{decoded}"'
        except:
            return match.group(0)

    result = re.sub(r'"(\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2})+)"', unescape_hex, result)

    def unescape_dec(match):
        nums = re.findall(r'\\(\d{1,3})', match.group(1))
        try:
            decoded = ''.join(chr(int(n)) for n in nums)
            return f'"{decoded}"'
        except:
            return match.group(0)

    result = re.sub(r'"(\\\d{1,3}(?:\\\d{1,3})+)"', unescape_dec, result)

    for _ in range(10):
        old = result
        aliases = {}
        for match in re.finditer(r'local\s+(\w+)\s*=\s*(\w+)', result):
            alias, original = match.groups()
            if original not in aliases and original != alias:
                aliases[alias] = original
        for alias, original in aliases.items():
            result = re.sub(r'\b' + re.escape(alias) + r'\b', original, result)
        if result == old:
            break

    lines = result.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'local\s+\w+\s*=\s+\w+\s*$', stripped):
            parts = stripped.replace('local ', '').split('=')
            if len(parts) == 2 and parts[0].strip() == parts[1].strip():
                continue
        cleaned_lines.append(line)
    result = '\n'.join(cleaned_lines)

    global_funcs = ['print', 'warn', 'error', 'pcall', 'xpcall', 'loadstring',
                    'require', 'pairs', 'ipairs', 'next', 'tonumber', 'tostring',
                    'type', 'assert', 'collectgarbage', 'getfenv', 'setfenv',
                    'rawget', 'rawset', 'rawequal', 'select', 'unpack', 'getmetatable',
                    'setmetatable', 'debug', 'math', 'string', 'table', 'coroutine',
                    'os', 'io', 'bit32', 'utf8']

    for func in global_funcs:
        result = re.sub(rf'_G\["{func}"\]\b', func, result)
        result = re.sub(rf'_G\[\'{func}\'\]\b', func, result)

    result = re.sub(r'\n{3,}', '\n\n', result)
    return result


def fetch_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


@app.route('/')
def home():
    return jsonify({
        "status": "Luau Logger API online",
        "endpoints": {
            "POST /api/deobf": "Recebe codigo Luau (file ou JSON com code/url), retorna desofuscado",
            "POST /api/revea": "Recebe codigo Luau (file ou JSON com code/url), executa logger.lua e retorna dump"
        }
    })


@app.route('/api/deobf', methods=['POST'])
def deobfuscate_endpoint():
    code = None

    if request.files:
        file = request.files.get("file")
        if file:
            code = file.read().decode("utf-8", errors="replace")

    if not code:
        data = request.get_json() or {}
        code = data.get("code", "")
        if not code and data.get("url"):
            code = fetch_url(data["url"])
            if not code:
                return jsonify({"success": False, "error": "Failed to fetch URL"}), 400

    if not code or not code.strip():
        return jsonify({"success": False, "error": "No code provided"}), 400

    try:
        deobfuscated = deobfuscate_revea(code)
        return jsonify({
            "success": True,
            "original_length": len(code),
            "deobfuscated_length": len(deobfuscated),
            "code": deobfuscated
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/revea', methods=['POST'])
def revea_endpoint():
    code = None

    if request.files:
        file = request.files.get("file")
        if file:
            code = file.read().decode("utf-8", errors="replace")

    if not code:
        data = request.get_json() or {}
        code = data.get("code", "")
        if not code and data.get("url"):
            code = fetch_url(data["url"])
            if not code:
                return jsonify({"success": False, "error": "Failed to fetch URL"}), 400

    if not code or not code.strip():
        return jsonify({"success": False, "error": "No code provided"}), 400

    try:
        dumped = run_revea_logger(code)
        return jsonify({
            "success": True,
            "original_length": len(code),
            "dumped_length": len(dumped),
            "code": dumped
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

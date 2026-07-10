import subprocess
import tempfile

LOGGER_LUA_PATH = os.path.join(os.path.dirname(__file__), "src", "logger.lua")

def run_revea_logger(code: str) -> str:
    if not os.path.exists(LOGGER_LUA_PATH):
        raise FileNotFoundError("logger.lua nao encontrado")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as tmp_in:
        tmp_in.write(code)
        tmp_in.flush()
        input_path = tmp_in.name

    try:
        result = subprocess.run(
            ["luau", LOGGER_LUA_PATH, input_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout if result.stdout else result.stderr
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)


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

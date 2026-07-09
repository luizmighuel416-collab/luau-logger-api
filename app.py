from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Se quiser persistência, pode usar SQLite ou PostgreSQL
# Aqui um exemplo simples em memória (reinicia a cada deploy)
logs = []

@app.route('/')
def home():
    return jsonify({"status": "Luau Logger API online", "version": "1.0"})

@app.route('/api/log', methods=['POST'])
def receive_log():
    data = request.get_json()
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script_name": data.get("script_name", "unknown"),
        "level": data.get("level", "INFO"),
        "message": data.get("message", ""),
        "metadata": data.get("metadata", {}),
        "ip": request.remote_addr
    }
    
    logs.append(log_entry)
    print(f"[{log_entry['level']}] {log_entry['script_name']}: {log_entry['message']}")
    
    return jsonify({"success": True, "received_at": log_entry["timestamp"]})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    return jsonify({"logs": logs[-limit:]})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    logs.clear()
    return jsonify({"success": True, "message": "Logs cleared"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

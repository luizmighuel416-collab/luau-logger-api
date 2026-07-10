import os
import tempfile
import requests

PASTEFY_URL = "https://pastefy.app/X7MUydRh/raw"
API_URL = "https://api-speack.onrender.com/speack/api/v1/deobf"
REVEA_URL = "https://web-production-eb197.up.railway.app/api/deobf"
REVEA_DUMP_URL = "https://web-production-eb197.up.railway.app/api/revea"
TOKEN_69MS = "ncj-ndh-kwm-wqj-3x4-lunar-is-the-best"


def _get_69ms_endpoint() -> str:
    try:
        r = requests.get(PASTEFY_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            endpoint = r.text.strip()
            if endpoint.startswith("http"):
                return endpoint
    except Exception:
        pass
    return None


def _clean_output(text: str) -> str:
    lines = text.splitlines()
    if lines and "Speack" in lines[0]:
        lines[0] = "-- Deobf by Speack | https://discord.gg/SxfqCrd952"
    return chr(10).join(lines)


def deobfuscate(code: str, mode: str = "moonsecv3") -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as f:
            response = requests.post(
                API_URL,
                files={"file": f},
                timeout=120
            )

        if response.status_code == 200:
            return _clean_output(response.text)
        return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def deobfuscate_from_url(url: str, mode: str = "moonsecv3") -> str:
    try:
        response = requests.post(
            API_URL,
            data={"url": url},
            timeout=120
        )

        if response.status_code == 200:
            return _clean_output(response.text)
        return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"


def deobfuscate_69ms(code: str) -> str:
    endpoint = _get_69ms_endpoint()
    if not endpoint:
        return "Erro: nao foi possivel obter o endpoint atual da API 69ms."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as f:
            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {TOKEN_69MS}"},
                files={"file": ("script.lua", f, "text/plain")},
                timeout=300
            )

        if response.status_code == 200:
            return _clean_output(response.text)
        return f"Erro da API: HTTP {response.status_code} - {response.text[:500]}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def deobfuscate_69ms_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return f"Erro ao baixar URL: HTTP {r.status_code}"
        code = r.text
        return deobfuscate_69ms(code)
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"


def deobfuscate_revea(code: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as f:
            response = requests.post(
                REVEA_URL,
                files={"file": f},
                timeout=120
            )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["code"]
            return f"Erro da API: {data.get('error', 'unknown')}"
        return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def deobfuscate_revea_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return f"Erro ao baixar URL: HTTP {r.status_code}"
        code = r.text
        return deobfuscate_revea(code)
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"


def deobfuscate_revea_dump(code: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as f:
            response = requests.post(
                REVEA_DUMP_URL,
                files={"file": f},
                timeout=120
            )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["code"]
            return f"Erro da API: {data.get('error', 'unknown')}"
        return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def deobfuscate_revea_dump_from_url(url: str) -> str:
    try:
        response = requests.post(
            REVEA_DUMP_URL,
            data={"url": url},
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["code"]
            return f"Erro da API: {data.get('error', 'unknown')}"
        return f"Erro da API: HTTP {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Erro de conexao: {e}"

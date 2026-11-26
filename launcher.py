"""Entry point for the packaged app: starts the API and opens the browser."""

import multiprocessing
import os
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

PORT = int(os.environ.get("PORT", "8000"))


def _base_dir() -> Path:
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent


def _setup_env(base: Path) -> None:
    bin_dir = base / "bin"
    if bin_dir.is_dir():
        os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("MODELS_DIR", str(base / "models"))
    os.environ.setdefault("FRONTEND_DIR", str(base / "web"))
    os.environ.setdefault("EMBEDDED_QDRANT", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("CORS_ALLOW_ORIGINS", f"http://127.0.0.1:{PORT},http://localhost:{PORT}")


def _ollama_status() -> str | None:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
            if b"llama3.1" not in r.read():
                return "Ollama is running but the llama3.1 model is missing. Run: ollama pull llama3.1"
    except Exception:
        return "Ollama is not running. Summaries and Ask AI need it (https://ollama.com)."
    return None


def _open_when_ready() -> None:
    for _ in range(120):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1)
            webbrowser.open(f"http://127.0.0.1:{PORT}/")
            return
        except Exception:
            time.sleep(1)


def main() -> None:
    multiprocessing.freeze_support()
    if sys.stdout is None or sys.stderr is None:
        sys.stdout = sys.stderr = open(Path(tempfile.gettempdir()) / "AIMeeting.log", "a", buffering=1, encoding="utf-8")
    _setup_env(_base_dir())
    warning = _ollama_status()
    if warning:
        print("WARNING:", warning)
    import uvicorn

    from app.main import app

    if "--no-window" not in sys.argv:
        threading.Thread(target=_open_when_ready, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")


if __name__ == "__main__":
    main()

from pathlib import Path

SENTINEL = Path.home() / ".ai_ablage_initialized"


def check_first_run() -> None:
    """Print installation instructions on first run."""
    if not SENTINEL.exists():
        print("Erste Ausf\u00fchrung erkannt. Bitte installieren Sie die Abh\u00e4ngigkeiten mit:\n"
              "    pip install -r MillerLieblingskind/requirements.txt\n")
        try:
            SENTINEL.touch()
        except Exception:
            pass

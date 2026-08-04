import json
from pathlib import Path


DATA_DIR = Path("data/reactive_defense")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _state_path(state_id: str) -> Path:
    return DATA_DIR / f"{state_id}.json"


def _write_state(state_id: str, data: dict):
    path = _state_path(state_id)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _read_state(state_id: str) -> dict:
    path = _state_path(state_id)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _delete_state(state_id: str):
    path = _state_path(state_id)
    if path.exists():
        path.unlink()


def _set_status(state_id: str, status: str):
    data = _read_state(state_id)
    data["status"] = status
    _write_state(state_id, data)

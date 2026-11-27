"""Append enquiry outcomes to a local JSON status log."""
import json
import os
import tempfile
from datetime import datetime, timezone


def append_entry(path: str, entry: dict) -> dict:
    """Append one record to the JSON status log (atomic write)."""
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entry}
    records = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                records = json.load(f)
        except json.JSONDecodeError:
            os.replace(path, path + ".corrupt")  # keep the bad file, start fresh
    records.append(entry)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return entry

"""
Structured run log: one JSON object per line, one line per agent run.

Written for every run, including ones that failed, so a failure never shows up
only as an absence. Read it back with:

    python runlog.py          # prints the last 10 entries
"""

import json
import sys
from datetime import datetime, timezone

import config


def write(entry: dict) -> None:
    """Append one record. Logging must never break the run it describes."""
    try:
        config.RUN_LOG.parent.mkdir(exist_ok=True)
        with config.RUN_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"  [runlog] couldn't write the log: {exc}", file=sys.stderr)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def tail(n: int = 10) -> list[dict]:
    if not config.RUN_LOG.exists():
        return []
    lines = config.RUN_LOG.read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lines[-n:]]


if __name__ == "__main__":
    for entry in tail():
        print(json.dumps(entry, ensure_ascii=False))

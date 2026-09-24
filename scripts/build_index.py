#!/usr/bin/env python3
"""Build index.json from packs/*.json.

Each entry in index.json contains only: id, author, label, url.
No indicator, entry, or exit keys are exposed.

Usage:
    python3 scripts/build_index.py            # write index.json
    python3 scripts/build_index.py --check    # exit 1 if index.json missing or differs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = REPO_ROOT / "packs"
INDEX_PATH = REPO_ROOT / "index.json"
BASE_URL = "https://raw.githubusercontent.com/d4rk-pri0r/krellbot-community-packs/main/packs"


def build_entries() -> list[dict]:
    entries: list[dict] = []
    for pack_path in sorted(PACKS_DIR.glob("*.json")):
        with pack_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        pack_id = data["id"]
        entries.append(
            {
                "id": pack_id,
                "author": data.get("author", ""),
                "label": data.get("label", ""),
                "url": f"{BASE_URL}/{pack_path.name}",
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if index.json is missing or differs from the generated content. Writes nothing.",
    )
    args = parser.parse_args()

    entries = build_entries()
    new_content = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not INDEX_PATH.exists():
            print(f"index.json missing at {INDEX_PATH}", file=sys.stderr)
            return 1
        existing = INDEX_PATH.read_text(encoding="utf-8")
        if existing != new_content:
            print("index.json differs from generated content. Run scripts/build_index.py to update.", file=sys.stderr)
            return 1
        return 0

    INDEX_PATH.write_text(new_content, encoding="utf-8")
    print(f"Wrote {INDEX_PATH} ({len(entries)} entr{'y' if len(entries) == 1 else 'ies'}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

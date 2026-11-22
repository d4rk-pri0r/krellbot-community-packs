#!/usr/bin/env python3
"""Build index.json from packs/*.json.

Each entry in index.json contains only: id, author, label, url.
No indicator, entry, or exit keys are exposed.

Usage:
    python3 scripts/build_index.py            # write index.json
    python3 scripts/build_index.py --check    # exit 1 if index.json missing or differs
    python3 scripts/build_index.py --validate # also lint every indexed pack
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.request import HTTPRedirectHandler, build_opener

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = REPO_ROOT / "packs"
INDEX_PATH = REPO_ROOT / "index.json"
RAW_REPO = "https://raw.githubusercontent.com/d4rk-pri0r/krellbot-community-packs"
BASE_URL = f"{RAW_REPO}/main/packs"
MAX_BODY_BYTES = 1_000_000


def read_pack(pack_path: Path) -> tuple[bytes, dict]:
    if pack_path.is_symlink():
        raise ValueError(f"{pack_path.name}: pack files must be regular JSON files")
    with pack_path.open("rb") as source:
        body = source.read(MAX_BODY_BYTES + 1)
    if len(body) > MAX_BODY_BYTES:
        raise ValueError(f"{pack_path.name}: exceeds the {MAX_BODY_BYTES}-byte install limit")
    try:
        data = json.loads(body.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"{pack_path.name}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise TypeError(f"{pack_path.name}: pack must be a JSON object")
    return body, data


def build_entries() -> list[dict]:
    entries: list[dict] = []
    for pack_path in sorted(PACKS_DIR.glob("*.json")):
        _, data = read_pack(pack_path)
        pack_id = data.get("id")
        if (
            not isinstance(pack_id, str)
            or not re.fullmatch(r"[a-z0-9-]{1,32}", pack_id)
            or pack_path.name != f"{pack_id}.json"
        ):
            raise ValueError(f"{pack_path.name}: filename must match a valid pack id")
        for field in ("author", "label", "origin"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip() or len(value) > 120:
                raise ValueError(f"{pack_path.name}: {field} must be a nonblank string of at most 120 characters")
        entries.append(
            {
                "id": pack_id,
                "author": data["author"],
                "label": data["label"],
                "url": f"{BASE_URL}/{pack_path.name}",
            }
        )
    return entries


class RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_packs(entries: list[dict], published_ref: str | None) -> None:
    from krellbot.pack.lint import check

    opener = build_opener(RejectRedirects()) if published_ref else None
    for entry in entries:
        filename = f"{entry['id']}.json"
        body, pack = read_pack(PACKS_DIR / filename)
        if opener is not None:
            url = f"{RAW_REPO}/{published_ref}/packs/{filename}"
            with opener.open(url, timeout=20) as source:
                published_body = source.read(MAX_BODY_BYTES + 1)
            if published_body != body:
                raise ValueError(f"{filename}: published content differs from the checked-out pack")
        # The engine also accepts legacy packs for display. Community packs must be runnable DSL.
        if type(pack.get("schema_version")) is not int or pack["schema_version"] != 1:
            raise ValueError(f"{filename}: schema_version must be 1")
        errors = check(pack)
        if errors:
            details = "\n".join(f"{error['field']}: {error['message']}" for error in errors)
            raise ValueError(f"{filename}: invalid pack\n{details}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if index.json is missing or differs from the generated content. Writes nothing.",
    )
    parser.add_argument("--validate", action="store_true", help="Check the index and run the Pack DSL validator.")
    parser.add_argument("--published-ref", help="Also verify the published raw files at this commit SHA.")
    args = parser.parse_args()

    if args.published_ref and (not args.validate or not re.fullmatch(r"[0-9a-f]{40}", args.published_ref)):
        parser.error("--published-ref requires --validate and a full commit SHA")

    try:
        entries = build_entries()
    except (OSError, TypeError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    new_content = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"

    if args.check or args.validate:
        if not INDEX_PATH.exists():
            print(f"index.json missing at {INDEX_PATH}", file=sys.stderr)
            return 1
        existing = INDEX_PATH.read_text(encoding="utf-8")
        if existing != new_content:
            print("index.json differs from generated content. Run scripts/build_index.py to update.", file=sys.stderr)
            return 1
        if args.validate:
            try:
                validate_packs(entries, args.published_ref)
            except (OSError, TypeError, ValueError) as exc:
                print(exc, file=sys.stderr)
                return 1
            print(f"Validated index and {len(entries)} pack(s).")
        return 0

    INDEX_PATH.write_text(new_content, encoding="utf-8")
    print(f"Wrote {INDEX_PATH} ({len(entries)} entr{'y' if len(entries) == 1 else 'ies'}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

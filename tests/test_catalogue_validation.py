"""Exercise the same catalogue command that runs on pull requests."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CatalogueValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.catalogue = Path(temporary.name)
        self.script = self.catalogue / "scripts" / "build_index.py"
        self.script.parent.mkdir()
        shutil.copyfile(ROOT / "scripts" / "build_index.py", self.script)
        self.pack_path = self.catalogue / "packs" / "fixture-pack.json"
        self.pack_path.parent.mkdir()
        pack = {
            "schema_version": 1,
            "id": "fixture-pack",
            "version": "1.0.0",
            "label": "Fixture pack",
            "author": "Test author",
            "origin": "Community pack. Unverified. No guarantee.",
            "timeframe": "1h",
            "indicators": {"sma20": {"fn": "sma", "src": "close", "len": 20}},
            "entry": ["close", ">", "sma20"],
            "exit": ["close", "<", "sma20"],
            "risk": {"max_account_pct": 25, "stop": {"type": "pct", "pct": 5}},
            "markets": [{"venue": "kraken", "pair": "SUIUSD"}],
        }
        self.pack_path.write_text(json.dumps(pack), encoding="utf-8")
        self.index = self.catalogue / "index.json"
        self.run_builder().check_returncode()

    def run_builder(self, *args):
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_catalogue_passes(self):
        result = self.run_builder("--validate")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_indexed_pack_fails_even_with_a_matching_index(self):
        pack = json.loads(self.pack_path.read_text(encoding="utf-8"))
        pack["entry"] = ["close", ">", "undefined_indicator"]
        self.pack_path.write_text(json.dumps(pack), encoding="utf-8")

        result = self.run_builder("--validate")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("fixture-pack.json: invalid pack", result.stderr)
        self.assertIn("undefined_indicator", result.stderr)

    def test_foreign_index_url_fails_the_generated_index_check(self):
        entries = json.loads(self.index.read_text(encoding="utf-8"))
        entries[0]["url"] = "https://example.invalid/pack.json"
        self.index.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

        result = self.run_builder("--validate")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("differs from generated content", result.stderr)

    def test_missing_community_origin_fails(self):
        pack = json.loads(self.pack_path.read_text(encoding="utf-8"))
        del pack["origin"]
        self.pack_path.write_text(json.dumps(pack), encoding="utf-8")

        result = self.run_builder("--validate")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("origin must be a nonblank string", result.stderr)

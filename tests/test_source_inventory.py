"""Inventory must detect altered source without treating checkout newlines as tampering."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def test_inventory_accepts_checkout_newlines_but_rejects_changed_source(tmp_path, monkeypatch):
    specification = importlib.util.spec_from_file_location("inventory_check", Path(__file__).parents[1] / "scripts/source_inventory.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "docs").mkdir()
    source = tmp_path / "guide.md"
    source.write_bytes(b"Original source\r\n")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["inventory"])
    module.main()
    monkeypatch.setattr(sys, "argv", ["inventory", "--check"])
    source.write_bytes(b"Original source\n")
    assert module.main() == 0
    source.write_bytes(b"Altered source\n")
    assert module.main() == 1
    source.write_bytes(b"Original source\n")
    (tmp_path / "omitted.md").write_text("New unrecorded source", encoding="utf-8")
    assert module.main() == 1
    assert json.loads((tmp_path / "docs/SOURCE_INVENTORY.json").read_text())["files"]

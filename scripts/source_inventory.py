"""Record only this new tree. No historical source is opened for comparison."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = sorted(
        set(
            subprocess.check_output(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=ROOT,
                text=True,
            ).splitlines()
        )
    )
    if "--check" in sys.argv:
        expected = json.loads((ROOT / "docs/SOURCE_INVENTORY.json").read_text(encoding="utf-8"))["files"]
        indexed = {row["path"]: row for row in expected}
        actual = {name for name in names if name != "docs/SOURCE_INVENTORY.json" and (ROOT / name).is_file()}
        errors = sorted(actual.symmetric_difference(indexed))
        converted = 0
        for name in actual.intersection(indexed):
            data = (ROOT / name).read_bytes()
            candidates = {hashlib.sha256(data).hexdigest()}
            if b"\x00" not in data:
                lf = data.replace(b"\r\n", b"\n")
                candidates.update(hashlib.sha256(value).hexdigest() for value in (lf, lf.replace(b"\n", b"\r\n")))
            if indexed[name]["sha256"] not in candidates:
                errors.append(name)
            elif hashlib.sha256(data).hexdigest() != indexed[name]["sha256"]:
                converted += 1
        print(json.dumps({"inventoryFiles": len(indexed), "lineEndingConversions": converted, "errors": errors}))
        return int(bool(errors))
    records = []
    for name in names:
        if name == "docs/SOURCE_INVENTORY.json":
            continue
        path = ROOT / name
        if not path.is_file():
            continue
        origin = (
            "Third-party license/notice text from newly installed dependency"
            if name.startswith("docs/dependency-licenses/")
            else "New requirements-based project material or package-manager metadata; AI-assisted, not a legal independence certificate"
        )
        if name.startswith("docs/assets/") and path.suffix == ".png":
            origin = "Genuine Playwright app capture; result data explicitly illustrative, not live YouTube; see docs/assets/README.md"
        if name == "apps/web/AGENTS.md":
            origin = "Next.js-generated framework guidance from the newly installed MIT-licensed dependency; upstream notice retained"
        records.append(
            {
                "path": name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
                "origin": origin,
            }
        )
    result = {
        "method": "Raw working-tree byte inventory of this separate workspace only; excludes this self-referential manifest and ignored private/runtime files. Git line-ending conversion can change raw hashes across operating systems",
        "files": records,
    }
    (ROOT / "docs/SOURCE_INVENTORY.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Inventoried {len(records)} new-tree files; no historical implementation read.")


if __name__ == "__main__":
    raise SystemExit(main())

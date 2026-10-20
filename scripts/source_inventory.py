"""Record only this new tree. No historical source is opened for comparison."""

import hashlib
import json
import subprocess
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
    main()

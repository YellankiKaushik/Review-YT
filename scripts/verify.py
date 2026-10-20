"""Run the new project's release checks and retain actual command outcomes."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/verification"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    npm = ["cmd.exe", "/d", "/c", "npm"] if os.name == "nt" else ["npm"]
    commands = [
        [sys.executable, "-m", "ruff", "check", "packages", "apps", "tests", "scripts"],
        [sys.executable, "-m", "pytest", "-q"],
        npm + ["run", "lint"],
        npm + ["run", "typecheck"],
        npm + ["test"],
        npm + ["run", "build"],
        [sys.executable, "-m", "build", "packages/review_yt_core", "--outdir", "artifacts/package"],
        npm + ["run", "test:e2e"],
        [sys.executable, "-m", "pip", "check"],
        npm + ["audit", "--audit-level=high"],
        [
            sys.executable,
            "-m",
            "pip_audit",
            "--skip-editable",
            "-f",
            "json",
            "-o",
            "artifacts/pip-audit-final.json",
        ],
        [sys.executable, "scripts/check_release_config.py"],
        [sys.executable, "scripts/secret_check.py"],
    ]
    records = []
    environment = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1"}
    for index, command in enumerate(commands, 1):
        start = time.monotonic()
        result = subprocess.run(
            command, cwd=ROOT, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        filename = f"{index:02d}.log"
        (OUT / filename).write_bytes(result.stdout)
        record = {
            "command": ["python" if item == sys.executable else item for item in command],
            "exit": result.returncode,
            "seconds": round(time.monotonic() - start, 2),
            "log": filename,
        }
        records.append(record)
        (OUT / "results.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(json.dumps(record), flush=True)
        if result.returncode:
            print(
                "Stopped at a failing check. Inspect its local log without exposing private values.",
                flush=True,
            )
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

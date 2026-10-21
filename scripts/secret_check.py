"""Local/CI release check. Never prints credential values or matched source text."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def main():
    tracked = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True
    ).splitlines()
    secrets = {}
    for name in (".env", "apps/web/.env.local"):
        for key, value in dotenv_values(ROOT / name).items():
            if (
                value
                and len(value) >= 12
                and any(part in key for part in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
            ):
                secrets[key] = value
    for key in (
        "YOUTUBE_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
    ):
        if os.getenv(key):
            secrets[key] = os.environ[key]
    bundles = [
        p
        for p in (ROOT / "apps/web").glob(".next*/static/**/*")
        if p.is_file() and p.suffix in (".js", ".json", ".map", ".html")
    ]
    logs = list((ROOT / "artifacts").glob("*.log"))
    matches = []
    for path in {ROOT / p for p in tracked} | set(bundles) | set(logs):
        if not path.is_file():
            continue
        data = path.read_bytes()
        for variable, value in secrets.items():
            if value.encode() in data:
                matches.append({"file": str(path.relative_to(ROOT)), "variable": variable})
        if re.search(rb"(?:sk-or-v1-|AIza)[A-Za-z0-9_-]{30,}", data):
            matches.append({"file": str(path.relative_to(ROOT)), "variable": "known-key-prefix"})
    unexpected = [
        p for p in tracked if Path(p).name.startswith(".env") and Path(p).name != ".env.example"
    ]
    prohibited = [
        p for p in tracked if Path(p).suffix in (".sqlite", ".db", ".zip", ".whl") or ".cache/" in p
    ]
    public = []
    for name in tracked:
        if name.endswith((".ts", ".tsx", ".mjs", ".js")) and re.search(
            r"NEXT_PUBLIC_[A-Z_]*(KEY|TOKEN|SECRET)",
            (ROOT / name).read_text(encoding="utf-8", errors="ignore"),
        ):
            public.append(name)
    history_count = 0
    if "--history" in sys.argv:
        objects = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT, text=True).splitlines()
        identities = dict.fromkeys(row.split(" ", 1)[0] for row in objects)
        process = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            for identity in identities:
                process.stdin.write((identity + "\n").encode())
                process.stdin.flush()
                header = process.stdout.readline().split()
                data = process.stdout.read(int(header[2]))
                process.stdout.read(1)
                if header[1] == b"blob":
                    history_count += 1
                    if any(value.encode() in data for value in secrets.values()) or re.search(rb"(?:sk-or-v1-|AIza)[A-Za-z0-9_-]{30,}", data):
                        matches.append({"object": identity, "variable": "reachable-history-secret"})
        finally:
            process.stdin.close()
            process.stdout.close()
            process.wait()
    result = {
        "scope": "tracked/nonignored files, built browser artifacts and local application logs; exact configured values and recognized provider prefixes, not a complete security audit",
        "sourceFiles": len(set(tracked)),
        "reachableBlobs": history_count,
        "browserArtifacts": len(bundles),
        "logs": len(logs),
        "configuredValues": len(secrets),
        "matches": matches,
        "unexpectedEnvironmentFiles": unexpected,
        "prohibitedArtifacts": prohibited,
        "publicSecretVariables": public,
    }
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/secret-check.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result))
    return int(bool(matches or unexpected or prohibited or public))


if __name__ == "__main__":
    raise SystemExit(main())

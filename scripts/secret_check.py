"""Local/CI release check. Never prints credential values or matched source text."""

import json
import os
import re
import subprocess
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
    result = {
        "scope": "tracked/nonignored files, built browser artifacts and local application logs; exact configured values and recognized provider prefixes, not a complete security audit",
        "sourceFiles": len(set(tracked)),
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

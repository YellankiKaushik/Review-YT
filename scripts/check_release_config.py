"""Static deployment invariants; this does not claim a cloud build or deployment."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    blueprint = yaml.safe_load((ROOT / "render.yaml").read_text())
    service = blueprint["services"][0]
    assert (
        service["runtime"] == "python"
        and service["plan"] == "free"
        and service["autoDeployTrigger"] == "off"
    )
    assert service["healthCheckPath"] == "/health" and (ROOT / "apps/api/serve.py").is_file()
    env = {item["key"]: item for item in service["envVars"]}
    assert (
        env["SUMMARY_ALLOW_PAID"]["value"] == "false"
        and env["SUMMARY_FALLBACK_ENABLED"]["value"] == "false"
    )
    assert (
        env["SUMMARY_ENABLED_PROVIDERS"]["value"] == "disabled"
        and env["SUMMARY_PROVIDER"]["value"] == "disabled"
        and env["HOST"]["value"] == "0.0.0.0"
    )
    assert "PORT" not in env and not any(k.startswith("OLLAMA") for k in env)
    assert all(
        env[key].get("sync") is False
        for key in ("YOUTUBE_API_KEY", "BACKEND_API_TOKEN")
    )
    vercel = json.loads((ROOT / "apps/web/vercel.json").read_text())
    assert vercel["framework"] == "nextjs" and vercel["outputDirectory"] == ".next"
    assert "npm ci" in vercel["installCommand"] and "npm run build" in vercel["buildCommand"]
    for target in (
        "requirements-runtime.lock",
        "requirements.txt",
        "packages/review_yt_core/pyproject.toml",
    ):
        assert (ROOT / target).is_file()
    workflow = yaml.safe_load((ROOT / ".github/workflows/verify.yml").read_text())
    assert workflow["permissions"] == {"contents": "read"}
    assert all(
        len(step["uses"].split("@")[1]) == 40
        for step in workflow["jobs"]["offline"]["steps"]
        if "uses" in step
    )
    print(
        "PASS: free Render native runtime, ephemeral cache, cloud-only allowlist, Vercel workspace and pinned read-only CI actions; static checks only."
    )


if __name__ == "__main__":
    main()

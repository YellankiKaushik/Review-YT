"""Inventory newly installed dependencies and retain their actual license texts."""

import hashlib
import json
import re
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/dependency-licenses"


def notice_file(path):
    name = path.name.lower()
    return (
        path.is_file()
        and (name.startswith(("license", "licence", "copying", "notice", "copyright")))
        and path.suffix.lower() in ("", ".txt", ".md", ".markdown")
        and path.stat().st_size < 300000
    )


def retain(path, identity):
    data = path.read_bytes()
    digest = hashlib.sha256((identity + str(path.relative_to(ROOT))).encode()).hexdigest()[:16]
    target = DEST / (digest + "-" + re.sub(r"[^A-Za-z0-9._-]", "_", path.name)[:60] + ".txt")
    target.write_bytes(data)
    return str(target.relative_to(ROOT)).replace("\\", "/")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    node = []
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    for relative, entry in lock["packages"].items():
        if "node_modules/" not in relative or entry.get("link"):
            continue
        base = ROOT / relative
        info = (
            json.loads((base / "package.json").read_text(encoding="utf-8"))
            if (base / "package.json").is_file()
            else entry
        )
        name = info.get("name") or relative.rsplit("node_modules/", 1)[-1]
        license = info.get("license") or entry.get("license") or "UNRESOLVED"
        if isinstance(license, dict):
            license = license.get("type", "UNRESOLVED")
        paths = [p for p in base.iterdir() if notice_file(p)] if base.is_dir() else []
        if name == "next":
            paths += [p for p in (base / "dist/compiled").rglob("*") if notice_file(p)]
        copies = [retain(path, "npm:" + name) for path in paths]
        node.append(
            {
                "name": name,
                "version": info.get("version", entry.get("version")),
                "license": license,
                "developmentOnly": entry.get("dev", False),
                "installedHere": base.is_dir(),
                "notices": copies,
            }
        )
    python = []
    for dist in metadata.distributions():
        name = dist.metadata["Name"]
        if name.lower().replace("_", "-") == "review-yt-core":
            continue
        license = (
            dist.metadata.get("License-Expression")
            or dist.metadata.get("License")
            or "; ".join(
                c for c in dist.metadata.get_all("Classifier", []) if c.startswith("License ::")
            )
            or "UNRESOLVED"
        )
        paths = []
        for relative in dist.files or []:
            path = Path(dist.locate_file(relative)).resolve()
            if path.is_relative_to(ROOT / ".venv") and notice_file(path):
                paths.append(path)
        python.append(
            {
                "name": name,
                "version": dist.version,
                "license": license,
                "notices": [retain(path, "python:" + name) for path in paths],
            }
        )
    result = {
        "scope": "npm lockfile including platform-optional entries; Python packages installed in the new environment, including development tools; SPDX/metadata is evidence, not legal clearance",
        "npm": node,
        "python": python,
    }
    (ROOT / "docs/DEPENDENCY_LICENSES.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    unresolved = [x["name"] for x in node + python if x["license"] == "UNRESOLVED"]
    copyleft = [
        x["name"]
        for x in node + python
        if re.search(r"(?<![A-Z])(A?GPL|LGPL|MPL)[- ]", str(x["license"]))
    ]
    report = "# Third-party notices\n\nThis new tree depends on third-party software. Original license/notice texts from this installation are retained in `dependency-licenses/`; `DEPENDENCY_LICENSES.json` records package versions, metadata and notice paths. These are third-party notices, not newly authored project text.\n\n"
    report += f"Inventoried {len(node)} npm lockfile entries and {len(python)} installed Python packages. Platform-optional packages not installed here are recorded from lockfile metadata; their complete platform distribution notices still require review when building for another OS. No dependency implementation source was copied into application modules.\n\n"
    report += (
        "Metadata-unresolved packages: "
        + (", ".join(unresolved) or "none")
        + ".\n\nPackages carrying GPL/LGPL/MPL-style metadata (including tools/optional libraries): "
        + (", ".join(copyleft) or "none detected")
        + ". Their exact conditions and distribution scope require review; permissive ownership of the entire dependency tree is not claimed. Metadata labels alone do not discharge license obligations.\n\n"
    )
    report += "VADER includes its lexicon and upstream notices under its MIT license; retain the upstream attribution. Python certifi's Mozilla Public License and native image-library notices are separate from the new source's pending license. Model weights are not bundled: local Gemma remains an installed external model governed by its provider terms. YouTube comments, captions, thumbnail images and generated live notes are runtime data, not a redistributable dataset in this repository. The small geometric app icon and CSS chart were authored for this implementation.\n"
    (ROOT / "docs/THIRD_PARTY_NOTICES.md").write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "npmEntries": len(node),
                "pythonPackages": len(python),
                "retainedNoticeFiles": len(list(DEST.iterdir())),
                "unresolvedMetadata": unresolved,
                "copyleftReview": copyleft,
            }
        )
    )


if __name__ == "__main__":
    main()

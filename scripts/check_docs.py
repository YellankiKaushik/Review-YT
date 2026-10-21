"""Validate committed documentation paths, image budgets and retained notice references."""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True
    ).splitlines()
    files = {ROOT / name for name in names if (ROOT / name).is_file()}
    errors = []
    links = 0
    docs = [p for p in files if p.suffix == ".md" and "dependency-licenses" not in p.parts]
    for page in docs:
        raw = page.read_text(encoding="utf-8")
        historical = "reports" in page.relative_to(ROOT).parts or page.name == "IMPLEMENTATION_JOURNAL.md"
        if not historical and any(host in raw for host in ("review-yt.vercel.app", "review-yt-api.onrender.com")):
            errors.append(f"{page.relative_to(ROOT)}: retired demo destination in active documentation")
        text = re.sub(r"```.*?```", "", raw, flags=re.S)
        targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
        targets += re.findall(r'(?:src|href)="([^"<>]+)"', text)
        for target in targets:
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            path = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
            links += 1
            if not path.is_relative_to(ROOT) or not path.exists():
                errors.append(f"{page.relative_to(ROOT)}: missing or out-of-tree target {target}")
            elif parsed.fragment and path.suffix == ".md":
                headings = re.findall(r"^#{1,6} +(.+)$", path.read_text(encoding="utf-8"), re.M)
                anchors = {re.sub(r"[^\w -]", "", h.lower()).replace(" ", "-") for h in headings}
                if unquote(parsed.fragment) not in anchors:
                    errors.append(f"{page.relative_to(ROOT)}: missing anchor {target}")
    assets = list((ROOT / "docs/assets").glob("*.png"))
    if any(p.stat().st_size > 1_500_000 for p in assets):
        errors.append("Documentation screenshot exceeds the 1.5 MB per-image budget")
    for name in ("review-yt-homepage.png", "review-yt-results.png", "review-yt-mobile.png", "review-yt-architecture.svg"):
        if not (ROOT / "docs/assets" / name).is_file():
            errors.append(f"Missing curated asset: {name}")
    dependency_inventory = json.loads((ROOT / "docs/DEPENDENCY_LICENSES.json").read_text(encoding="utf-8"))
    def visit(value):
        if isinstance(value, dict):
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, str) and value.startswith("docs/dependency-licenses/"):
            if not (ROOT / value).is_file():
                errors.append("Missing retained legal file: " + value)
    visit(dependency_inventory)
    print(json.dumps({"documents": len(docs), "relativeTargets": links, "curatedPNGs": len(assets), "errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

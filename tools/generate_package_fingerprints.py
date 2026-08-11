#!/usr/bin/env python3
"""Generate or verify deterministic package fingerprints for the durable dual tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "manifests" / "package-fingerprints.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for package in sorted(path for path in root.iterdir() if path.is_dir()):
        files = []
        for path in sorted(item for item in package.rglob("*") if item.is_file()):
            files.append(
                {
                    "path": path.relative_to(package).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
        records.append({"name": package.name, "files": files})
    return records


def render() -> str:
    payload = {
        "schema_version": 1,
        "claude": inventory(ROOT / "platforms" / "claude" / "skills"),
        "codex": inventory(ROOT / "platforms" / "codex" / "skills"),
        "shared": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
            for path in sorted((ROOT / "shared" / "canonical").glob("*.md"))
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the fingerprint file is stale")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Package fingerprints are stale; regenerate without --check")
        print(f"Verified {OUTPUT}")
        return
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Check or materialize shared canonical references into Claude and Codex packages."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared" / "canonical"
PLATFORMS = (
    ROOT / "plugins" / "summit53" / "skills",
    ROOT / "platforms" / "codex" / "skills",
)


def consumers(canonical: Path) -> list[Path]:
    """A package consumes a canonical file when it vendors a copy under references/."""
    found: list[Path] = []
    for platform in PLATFORMS:
        found.extend(platform.glob(f"*/references/{canonical.name}"))
    return sorted(found)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Check byte parity with shared/canonical or explicitly copy canonical "
            "references into existing Claude and Codex consumers. Seed a new consumer by "
            "copying the canonical file into its references/ folder once."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="check parity (default)")
    mode.add_argument("--write", action="store_true", help="overwrite existing consumers")
    args = parser.parse_args()

    canonical_files = sorted(SHARED.glob("*.md"))
    if not canonical_files:
        raise SystemExit("No canonical Markdown files found")

    drift: list[str] = []
    materialized = 0
    checked = 0
    for canonical in canonical_files:
        targets = consumers(canonical)
        if not targets:
            drift.append(f"{canonical.name}: no existing consumers")
            continue
        for target in targets:
            checked += 1
            if target.read_bytes() == canonical.read_bytes():
                continue
            if args.write:
                shutil.copyfile(canonical, target)
                materialized += 1
            else:
                drift.append(str(target.relative_to(ROOT)).replace("\\", "/"))

    if args.write:
        print(f"Materialized {materialized} changed reference(s); checked {checked} consumer(s)")
        return
    if drift:
        for item in drift:
            print(f"DRIFT: {item}")
        raise SystemExit(1)
    print(f"Canonical reference parity passed for {checked} consumer(s)")


if __name__ == "__main__":
    main()

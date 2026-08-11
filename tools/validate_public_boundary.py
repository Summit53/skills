#!/usr/bin/env python3
"""Fail when private provenance or tenant-specific markers enter the public tree."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CODEX = 16
EXPECTED_CLAUDE = 9
FORBIDDEN_ROOTS = {"skills", "provenance", "_canonical", "patches", "private"}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}
FORBIDDEN_PATTERNS = {
    "absolute Windows user path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    "private Notion URL": re.compile(r"app\.notion\.com", re.IGNORECASE),
    "hard-coded Org 2 label": re.compile(r"\bOrg(?:anization)?\s*2\b", re.IGNORECASE),
    "hard-coded organization.id 2": re.compile(
        r"organization\.id\s*(?:is|==|=|:)\s*[`\"']?2\b", re.IGNORECASE
    ),
    "personal review marker": re.compile(r"\bJamie\b"),
    "stale connector label": re.compile(r"Summit53(?: Staging_2|_Staging_2)"),
}


def package_names(path: Path) -> set[str]:
    return {item.name for item in path.iterdir() if item.is_dir()}


def main() -> None:
    errors: list[str] = []
    present_forbidden = sorted(name for name in FORBIDDEN_ROOTS if (ROOT / name).exists())
    if present_forbidden:
        errors.append(f"forbidden public roots present: {present_forbidden}")

    codex = package_names(ROOT / "platforms" / "codex" / "skills")
    claude = package_names(ROOT / "platforms" / "claude" / "skills")
    if len(codex) != EXPECTED_CODEX:
        errors.append(f"expected {EXPECTED_CODEX} Codex packages, found {len(codex)}")
    if len(claude) != EXPECTED_CLAUDE:
        errors.append(f"expected {EXPECTED_CLAUDE} Claude packages, found {len(claude)}")
    if not claude.issubset(codex):
        errors.append(f"Claude packages absent from Codex tree: {sorted(claude - codex)}")

    for path in sorted(item for item in ROOT.rglob("*") if item.is_file()):
        if path == Path(__file__).resolve():
            continue
        if ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            match = pattern.search(text)
            if match:
                relative = path.relative_to(ROOT).as_posix()
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{relative}:{line}: {label}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(
        f"Validated public boundary: {len(codex)} Codex packages, "
        f"{len(claude)} Claude packages"
    )


if __name__ == "__main__":
    main()

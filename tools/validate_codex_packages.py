#!/usr/bin/env python3
"""Validate the durable Summit53 Codex package tree without calling live systems."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / "platforms" / "codex" / "skills"
SHARED = ROOT / "shared" / "canonical"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def local_links(skill_dir: Path, markdown: Path) -> list[str]:
    errors: list[str] = []
    text = markdown.read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "#")):
            continue
        clean = target.split("#", 1)[0]
        resolved = skill_dir / clean if clean.startswith("references/") else markdown.parent / clean
        if not resolved.is_file():
            errors.append(f"{markdown.relative_to(ROOT)}: missing link {target}")
    return errors


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    packages = sorted(path for path in CODEX.iterdir() if path.is_dir())
    for package in packages:
        skill = package / "SKILL.md"
        agent = package / "agents" / "openai.yaml"
        if not skill.is_file():
            errors.append(f"{package.name}: missing SKILL.md")
            continue
        text = skill.read_text(encoding="utf-8")
        match = FRONTMATTER.search(text)
        if not match:
            errors.append(f"{package.name}: invalid frontmatter")
        else:
            keys = {
                line.split(":", 1)[0].strip()
                for line in match.group(1).splitlines()
                if ":" in line
            }
            if keys != {"name", "description"}:
                errors.append(f"{package.name}: frontmatter keys are {sorted(keys)}")
        if not agent.is_file():
            errors.append(f"{package.name}: missing agents/openai.yaml")
        elif f"${package.name}" not in agent.read_text(encoding="utf-8"):
            errors.append(f"{package.name}: default prompt does not name the skill")
        stale_connector_label = "Summit53 " + "Staging_2"
        if stale_connector_label in text:
            errors.append(f"{package.name}: stale plugin display label")
        for markdown in package.rglob("*.md"):
            errors.extend(local_links(package, markdown))
            body = markdown.read_text(encoding="utf-8")
            if (
                "references" in markdown.relative_to(package).parts
                and body.count("\n") > 100
                and "## Contents" not in body
            ):
                warnings.append(f"{markdown.relative_to(ROOT)}: long reference has no Contents section")
        for canonical in SHARED.glob("*.md"):
            vendored = package / "references" / canonical.name
            if vendored.exists() and vendored.read_bytes() != canonical.read_bytes():
                errors.append(f"{package.name}: shared drift in {canonical.name}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Validated {len(packages)} Codex package(s); {len(warnings)} warning(s)")


if __name__ == "__main__":
    main()

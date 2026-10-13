#!/usr/bin/env python3
"""Validate the Summit53 skill packages (shared by Claude and Codex) without calling live systems."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "summit53" / "skills"
SHARED = ROOT / "shared" / "canonical"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
# Codex's quick_validate accepts only these top-level keys; Claude accepts them too.
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
REQUIRED_KEYS = {"name", "description", "metadata"}
METADATA_KEYS = {"version", "baselined", "status"}
MAX_DESCRIPTION = 1024
PREFLIGHT = "connector-preflight.md"
HOST_ADAPTERS = "host-adapters.md"
# Host-specific constructs belong in host-adapters.md only; skill bodies stay host-neutral.
FORBIDDEN = {
    "Codex skill invocation": re.compile(r"(?<![\w$])\$[a-z][a-z0-9]*(?:-[a-z0-9]+)+\b"),
    "openai.yaml reference": re.compile(r"openai\.yaml"),
    "Codex Presentations/Documents skill": re.compile(r"\b(?:Presentations|Documents) skill\b"),
    "ToolSearch mechanics": re.compile(r"\bToolSearch\b"),
    "Claude invocation syntax": re.compile(r"/summit53:[a-z]"),
}
# Skill hosts substitute $0, $1 ... with invocation arguments when a SKILL.md loads,
# so a literal "$5,250,418" arrives as "<word>,250,418". Write amounts as "USD 5,250,418".
ARG_PLACEHOLDER = re.compile(r"\$[0-9]")


def frontmatter(text: str) -> tuple[dict[str, str], dict[str, str]] | None:
    """Return (top-level keys, metadata keys); nested values are read one level deep."""
    match = FRONTMATTER.search(text)
    if not match:
        return None
    values: dict[str, str] = {}
    metadata: dict[str, str] = {}
    parent = None
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if line.startswith((" ", "\t")):
            if parent == "metadata":
                metadata[key.strip()] = value
            continue
        parent = key.strip()
        values[parent] = value
    return values, metadata


def local_links(package: Path, markdown: Path) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    targets: set[str] = set()
    for target in LINK.findall(markdown.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean = target.split("#", 1)[0]
        resolved = package / clean if clean.startswith("references/") else markdown.parent / clean
        if not resolved.is_file():
            errors.append(f"{markdown.relative_to(ROOT)}: missing link {target}")
        else:
            targets.add(resolved.resolve().as_posix())
    return errors, targets


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    packages = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    for package in packages:
        skill = package / "SKILL.md"
        if not skill.is_file():
            errors.append(f"{package.name}: missing SKILL.md")
            continue
        text = skill.read_text(encoding="utf-8")
        parsed = frontmatter(text)
        if parsed is None:
            errors.append(f"{package.name}: invalid frontmatter")
            continue
        meta, metadata = parsed
        keys = set(meta)
        if not REQUIRED_KEYS <= keys:
            errors.append(f"{package.name}: frontmatter missing {sorted(REQUIRED_KEYS - keys)}")
        if keys - ALLOWED_KEYS:
            errors.append(f"{package.name}: unexpected frontmatter keys {sorted(keys - ALLOWED_KEYS)}")
        if set(metadata) != METADATA_KEYS:
            errors.append(f"{package.name}: metadata keys are {sorted(metadata)}, expected {sorted(METADATA_KEYS)}")
        agent = package / "agents" / "openai.yaml"
        if not agent.is_file():
            errors.append(f"{package.name}: missing agents/openai.yaml (Codex UI metadata)")
        elif f"${package.name}" not in agent.read_text(encoding="utf-8"):
            errors.append(f"{package.name}: agents/openai.yaml default prompt does not name the skill")
        if meta.get("name") != package.name:
            errors.append(f"{package.name}: frontmatter name {meta.get('name')!r} != directory")
        if len(meta.get("description", "")) > MAX_DESCRIPTION:
            errors.append(f"{package.name}: description exceeds {MAX_DESCRIPTION} characters")
        body = FRONTMATTER.sub("", text, count=1)
        if re.search(r"^---\n(?:name|description):", body, re.MULTILINE):
            errors.append(f"{package.name}: second frontmatter block in body")
        match = ARG_PLACEHOLDER.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{package.name}/SKILL.md:{line}: '$<digit>' is replaced by skill arguments at load time; write a currency code instead")
        for required in (PREFLIGHT, HOST_ADAPTERS):
            if not (package / "references" / required).is_file():
                errors.append(f"{package.name}: missing references/{required}")

        linked: set[str] = set()
        for markdown in sorted(package.rglob("*.md")):
            link_errors, targets = local_links(package, markdown)
            errors.extend(link_errors)
            linked |= targets
            content = markdown.read_text(encoding="utf-8")
            relative = markdown.relative_to(ROOT).as_posix()
            host_specific = markdown.name == HOST_ADAPTERS
            for label, pattern in ({} if host_specific else FORBIDDEN).items():
                match = pattern.search(content)
                if match:
                    line = content.count("\n", 0, match.start()) + 1
                    errors.append(f"{relative}:{line}: {label} ({match.group(0)!r})")
            if (
                "references" in markdown.relative_to(package).parts
                and content.count("\n") > 100
                and "## Contents" not in content
            ):
                warnings.append(f"{relative}: long reference has no Contents section")

        skill_text = skill.read_text(encoding="utf-8")
        for reference in sorted((package / "references").glob("*.md")):
            mentioned = f"references/{reference.name}" in skill_text
            # The canonical contracts reach a skill through the preflight's own links.
            if reference.name in (PREFLIGHT, HOST_ADAPTERS):
                continue
            if reference.resolve().as_posix() not in linked and not mentioned:
                errors.append(f"{package.name}: references/{reference.name} is never referenced")
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
    print(f"Validated {len(packages)} skill package(s); {len(warnings)} warning(s)")


if __name__ == "__main__":
    main()

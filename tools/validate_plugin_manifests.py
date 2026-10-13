#!/usr/bin/env python3
"""Validate the plugin and marketplace manifests that make the repo installable."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "summit53"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_PLUGIN = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN = PLUGIN / ".codex-plugin" / "plugin.json"
MCP = PLUGIN / ".mcp.json"
MCP_URL = "https://api.summit53.io/mcp"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.relative_to(ROOT)}: missing")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
    return {}


def main() -> None:
    errors: list[str] = []
    claude_plugin = load(CLAUDE_PLUGIN, errors)
    version = claude_plugin.get("version", "")
    if not SEMVER.match(version):
        errors.append(f"{CLAUDE_PLUGIN.relative_to(ROOT)}: version {version!r} is not semver")
    if claude_plugin.get("name") != PLUGIN.name:
        errors.append(f"{CLAUDE_PLUGIN.relative_to(ROOT)}: name must be {PLUGIN.name!r}")

    # Every manifest that carries a version must agree, or updates reach one host only.
    if CODEX_PLUGIN.exists():
        codex_plugin = load(CODEX_PLUGIN, errors)
        if codex_plugin.get("version") != version:
            errors.append(f"version mismatch: claude {version!r} vs codex {codex_plugin.get('version')!r}")
        if codex_plugin.get("name") != PLUGIN.name:
            errors.append(f"{CODEX_PLUGIN.relative_to(ROOT)}: name must be {PLUGIN.name!r}")

    marketplace = load(CLAUDE_MARKETPLACE, errors)
    entries = {entry.get("name"): entry for entry in marketplace.get("plugins", [])}
    entry = entries.get(PLUGIN.name)
    if not entry:
        errors.append(f"{CLAUDE_MARKETPLACE.relative_to(ROOT)}: no {PLUGIN.name!r} entry")
    elif (ROOT / entry.get("source", "")).resolve() != PLUGIN.resolve():
        errors.append(f"{CLAUDE_MARKETPLACE.relative_to(ROOT)}: source does not point at {PLUGIN.relative_to(ROOT)}")

    if CODEX_MARKETPLACE.exists():
        codex_market = load(CODEX_MARKETPLACE, errors)
        codex_entries = {e.get("name"): e for e in codex_market.get("plugins", [])}
        codex_entry = codex_entries.get(PLUGIN.name)
        if not codex_entry:
            errors.append(f"{CODEX_MARKETPLACE.relative_to(ROOT)}: no {PLUGIN.name!r} entry")
        else:
            path = codex_entry.get("source", {}).get("path", "")
            if (ROOT / path).resolve() != PLUGIN.resolve():
                errors.append(f"{CODEX_MARKETPLACE.relative_to(ROOT)}: source path does not point at {PLUGIN.relative_to(ROOT)}")

    servers = load(MCP, errors).get("mcpServers", {})
    server = servers.get("summit53", {})
    if server.get("url") != MCP_URL or server.get("type") != "http":
        errors.append(f"{MCP.relative_to(ROOT)}: summit53 must be an http server at {MCP_URL}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Validated plugin manifests at version {version}")


if __name__ == "__main__":
    main()

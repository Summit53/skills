#!/usr/bin/env python3
"""Generate the skill-routing eval suite under evals/routing/ from one table.

Each case sends a natural-language request with no MCP server attached and checks which
Summit53 skill Claude invokes. Routing depends only on skill descriptions, so no tenant
or connector is needed. Edit CASES, then run this script and commit the generated files.

Run the suite from the repository root (the plugin must sit under the eval target):

    claude plugin eval . --ablation none
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals" / "routing"
PLUGIN = "../../../plugins/summit53"

# (case name, prompt, expected skill, skills that must NOT be invoked, tags)
CASES: list[tuple[str, str, str, list[str], list[str]]] = [
    # A. One prompt per skill (from the staging smoke-test checklist).
    ("a01-ae-deal-inspection-prep", "Prep me for my deal inspection on Federation Insurance Group — Deal Execution Uplift. What will my manager ask?", "ae-deal-inspection-prep", [], ["per-skill"]),
    ("a02-board-revenue-pack", "I have a board meeting in three weeks. Build my board revenue pack for this quarter.", "board-revenue-pack", [], ["per-skill"]),
    ("a03-competitor-response-card", "A competitor just showed up in the Oceanic Pharma deal and they're saying they're cheaper. How do I respond?", "competitor-response-card", ["win-loss-analysis"], ["per-skill"]),
    ("a04-cs-renewal-forecast", "What's renewing in the next 90 days across my book, and how much ARR is at risk?", "cs-renewal-forecast", ["renewal-defence-pack"], ["per-skill"]),
    ("a05-customer-qbr", "Prep a customer QBR for Global Horizons Mining — what value have we delivered this quarter?", "customer-qbr", ["qbr-generator"], ["per-skill"]),
    ("a06-deal-review-prep", "Review the Kiwi Infrastructure Partners — Pipeline Coaching Program deal. How healthy is it and should I be worried?", "deal-review-prep", [], ["per-skill"]),
    ("a07-deal-timeline-defence", "When did the Southern Bank Corporation expansion deal go dark? Show me the evidence trail.", "deal-timeline-defence", [], ["per-skill"]),
    ("a08-first-meeting-deck", "I'm meeting Coral Bay Resources tomorrow for a first discovery call — make me a deck.", "first-meeting-deck", [], ["per-skill"]),
    ("a09-forecast-delta-brief", "Why is the forecast number different from last week? Prep me for the commit call.", "forecast-delta-brief", ["board-revenue-pack"], ["per-skill"]),
    ("a10-qbr-generator", "Prep for my QBR — pull together this quarter's numbers into our internal quarterly revenue review.", "qbr-generator", ["customer-qbr"], ["per-skill"]),
    ("a11-renewal-defence-pack", "Procurement is pushing back on Global Horizons Mining's renewal. Help me defend it.", "renewal-defence-pack", ["cs-renewal-forecast"], ["per-skill"]),
    ("a12-rep-coaching-report", "Prep my 1:1 with Rachel Kumar — what should I coach her on?", "rep-coaching-report", ["rep-evidence-dossier"], ["per-skill"]),
    ("a13-rep-evidence-dossier", "We're preparing for talent calibration. Pull together the performance record for Sarah Mitchell.", "rep-evidence-dossier", ["rep-coaching-report"], ["per-skill"]),
    ("a14-revenue-action-brief", "What should I focus on today and this week across the revenue team?", "revenue-action-brief-s53", [], ["per-skill"]),
    ("a15-territory-review", "How are my territories doing? Which regions are underperforming?", "territory-review", [], ["per-skill"]),
    ("a16-win-loss-analysis", "Why are we losing deals? What separates our wins from our losses?", "win-loss-analysis", ["competitor-response-card"], ["per-skill"]),
    # B. Near-miss pairs: each sounds like its neighbour but must route differently.
    ("b1-deal-review-not-inspection", "Give me the full picture on the Federation Insurance Group deal for my pipeline review with the team.", "deal-review-prep", ["ae-deal-inspection-prep"], ["near-miss"]),
    ("b2-inspection-not-deal-review", "Help me answer questions on the Federation Insurance Group deal before my 1:1 with my manager.", "ae-deal-inspection-prep", ["deal-review-prep"], ["near-miss"]),
    ("b3-internal-qbr-not-customer", "Build our quarterly business review deck for the exec team.", "qbr-generator", ["customer-qbr"], ["near-miss"]),
    ("b4-customer-ebr-not-internal", "Prep the EBR with Capital Wealth Advisory.", "customer-qbr", ["qbr-generator"], ["near-miss"]),
    ("b5-board-not-forecast-delta", "Is our revenue problem a market problem or an execution problem? The board will ask.", "board-revenue-pack", ["forecast-delta-brief"], ["near-miss"]),
    ("b6-renewal-defence-not-forecast", "Save plan for Capital Wealth Advisory — their renewal is at risk.", "renewal-defence-pack", ["cs-renewal-forecast"], ["near-miss"]),
    ("b7-win-loss-not-competitor-card", "What do our wins against competitors have in common?", "win-loss-analysis", ["competitor-response-card"], ["near-miss"]),
    ("b8-dossier-not-coaching", "We're considering a PIP for Jordan Reyes.", "rep-evidence-dossier", ["rep-coaching-report"], ["near-miss"]),
    # R. Start-here router and real-world phrasing seen in claude.ai.
    ("r1-router-which-org", "Which Summit53 organisation am I connected to?", "summit53", [], ["router"]),
    ("r2-router-setup", "Set up Summit53 for me — is it connected?", "summit53", [], ["router"]),
    ("r3-competitor-with-staging-suffix", "A competitor just showed up in the Oceanic Pharma deal and they're saying they're cheaper. How do I respond? Use the staging mcp server", "competitor-response-card", ["win-loss-analysis"], ["per-skill", "phrasing"]),
]


def skill_pattern(skill: str) -> str:
    return r'"skill"\s*:\s*"(?:summit53:)?' + skill + '"'


def render(name: str, prompt: str, expected: str, forbidden: list[str], tags: list[str]) -> str:
    # JSON strings are valid YAML scalars, which avoids quoting edge cases in prompts.
    description = f"Routes to {expected}"
    if forbidden:
        description += "; never " + ", ".join(forbidden)
    lines = [
        'schema_version: "1.1"',
        f"name: {name}",
        f"description: {json.dumps(description)}",
        f"tags: {json.dumps(['routing', *tags])}",
        f"plugins: {json.dumps([PLUGIN])}",
        "execution:",
        f"  prompt: {json.dumps(prompt, ensure_ascii=False)}",
        "  max_turns: 3",
        "  allowed_tools: [Read, Glob, Grep, Skill]",
        "graders:",
        f"  - name: routes-to-{expected}",
        "    type: tool_used",
        "    tool: Skill",
        f"    input_match: {json.dumps(skill_pattern(expected))}",
    ]
    for skill in forbidden:
        lines += [
            f"  - name: never-{skill}",
            "    type: tool_used",
            "    tool: Skill",
            f"    input_match: {json.dumps(skill_pattern(skill))}",
            "    min: 0",
            "    max: 0",
        ]
    return "\n".join(lines) + "\n"


def main() -> None:
    skills = {p.name for p in (ROOT / "plugins" / "summit53" / "skills").iterdir() if p.is_dir()}
    for name, _, expected, forbidden, _ in CASES:
        unknown = {expected, *forbidden} - skills
        if unknown:
            raise SystemExit(f"{name}: unknown skill(s) {sorted(unknown)}")
    if OUT.exists():
        shutil.rmtree(OUT)
    for case in CASES:
        case_dir = OUT / case[0]
        case_dir.mkdir(parents=True)
        (case_dir / "case.yaml").write_text(render(*case), encoding="utf-8")
    print(f"Wrote {len(CASES)} routing cases to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

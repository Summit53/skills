---
name: "first-meeting-deck"
description: "Build a grounded, customer-facing first-meeting or discovery PPTX for one Summit53 account or opportunity: assertive-but-invitational hypotheses, discovery agenda, market point of view, vendor-grounded capabilities and next steps, plus a visibly quarantined AE prep slide. Detects net-new vs expansion meetings and adapts to meeting length. Use when an AE is preparing for a first or early-stage customer meeting, e.g. 'first meeting deck for [deal/account]', 'prep a discovery deck', 'build slides for my call with [prospect]', 'I'm meeting [stakeholder] tomorrow — make me a deck', 'generate a hypothesis deck', 'customer-facing deck for [deal]', 'what should I show in the first meeting', 'turn this opportunity into a discovery deck'. Also use for an explicit 'refresh vendor context' or 'refresh vendor branding' request. Do not use for a value or success review with an existing customer — use customer-qbr. For a one-screen response to a named competitor in an active deal use competitor-response-card."
metadata:
  version: "1.2.0"
  baselined: "2026-10-13"
  status: "active"
---

# First Meeting Deck

Generate a customer-facing first meeting deck for a specific opportunity. The deck is a conversation-opener, not a pitch — it earns credibility through relevance, invites discovery through assertive hypotheses, and previews value without over-promising. Every internal diagnostic is filtered out; every slide is designed to be shown to the prospect, grounded in the vendor's real capabilities.

## Route first

- Use this skill for a first or early-stage meeting deck with a prospect, or with a new stakeholder at an existing customer (expansion meeting mode).
- A value, success or quarterly review with an existing customer → `customer-qbr`.
- A one-screen response to a named competitor in an active deal → `competitor-response-card`. This deck speaks in comparison categories, not competitor brands.
- An internal, manager-led review of the same deal → `deal-review-prep`.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its checklist before any data call. It covers tenant resolution (`current_context` first), picking between multiple Summit53 connectors, loading deferred tools in one batch ([host-adapters.md](references/host-adapters.md#loading-the-summit53-tools)), capability discovery with `list_available_tools`, live-schema inspection before every call (tool names and sample arguments in this file are semantic guidance), read-only discipline, fixture exclusion, unavailable-is-not-zero, correlational language and one-link delivery.

Skill-specific gates:

1. **Vendor files present and current.** Read both vendor reference files in full (see Reference files below) before any other step. Their `Last reviewed` date is **2026-04-21**: treat every date-sensitive claim in them — commercial offer mechanics, cohort names, slot counts and dates, "live" programmes, proof points, reference customers, and recently shipped capabilities — as unverified until checked against a current authoritative source (the vendor's own live website or pricing page, or the user's explicit confirmation in this conversation). An unverified or expired claim does not go on a slide.
2. **Resolve exactly one opportunity**, the attendees, meeting length and meeting objective before analysis. A name matching several opportunities is ambiguous — list the candidates and ask. Ask only when ambiguity would materially change the deck.
3. **Scope.** The opportunity's and account's organization must match `scoped_org_id`; on mismatch, stop.
4. **Demo label.** If the opportunity, account or narratives come from fixture or seeded data that provenance cannot separate from real records, every slide (Slide 0 included) carries **Demo data — not for customer or commercial decisions** in the footer, and the delivery note says the deck must not be shown to a real prospect.

## Reference files

- [references/vendor-context.md](references/vendor-context.md) — what the vendor says and stands for: identity, positioning and Signature Concepts, Real Capabilities, Honest Boundaries, Proof Points, Current Commercial Offer, Voice (including Language we never use), Market Point of View, and Maintenance (`Last reviewed`). Read it in Step 0; every transform that makes a capability, outcome or offer claim takes it as input.
- [references/vendor-branding.md](references/vendor-branding.md) — how the deck looks: colour palette, Slide Design Tokens, Background Strategy, Typography, Signature Visual, Visual Tone, What to Avoid, Accessibility Notes. Read it in Step 0; Steps 6–8 resolve every colour and typeface from it.

Throughout this file, `vendor-context.md` and `vendor-branding.md` mean these two files in `references/`. Do not modify either file unless the user explicitly asks for a vendor-context or vendor-branding refresh, and even then only after they approve the proposed changes (see Step 0).

## Why This Exists

AEs walk into first meetings with two bad options: show a generic capabilities deck (which kills credibility) or wing it (which kills structure). The opportunity contains rich material — strategic narrative, pre-empted objections, stakeholder-tailored value messaging, a recommended agenda — but all written for internal use. Meanwhile, the vendor's own positioning, real capabilities, and commercial offer sit in a separate brain (or worse, everyone's head, slightly differently). This skill unifies both sides — customer context + vendor context — and assembles a deck that opens a real conversation.

## Voice Guide — Read This Before Building Anything

The single biggest risk in this skill is leaking internal voice into customer-facing slides. Strategic narrative tools speak in declaratives tuned for a sales manager's eyes ("This deal requires…", "The compelling case for change is…"). That voice does not belong in front of a prospect.

The deck's voice must be **assertive but invitational**:

- **Assertive**: take a position, commit to a point of view, show you've done the work
- **Invitational**: frame every position as a hypothesis the customer is invited to challenge

The signature move is: *"Here's what we believe is going on. Is this right? What would you challenge?"* Never *"Here's what's going on"* full-stop, and never *"Maybe you could possibly be facing…"* tentatively. The prospect should leave feeling both respected (the AE prepared) and heard (their reality got tested, not preached).

**Banned phrases and framings:**
- "You need to…", "You must…", "The compelling case…" — too pushy
- "We think you might possibly be considering…" — too weak
- Any risk scores, framework percentages, health ratings, deal-drag scores, waste scores, or internal diagnostic numbers — even as subtle labels
- Product/platform/solution self-references before slide 6 — we haven't earned the right to pitch yet
- **Any capability claim not backed by the vendor context file** — see Step 0

**Required voice patterns:**
- "Our hypothesis is that…" / "We believe…" — assertive framing
- "Is this right?" / "What would you challenge?" / "Where are we wrong?" — the invitation
- "We'd like to understand…" — for discovery questions (not "Can you tell us…")
- The prospect's own language from their website, news, and prior conversations — mirror, don't translate
- The vendor's canonical positioning language from `vendor-context.md` — always

## Step 0: Load Vendor Context (or Set It Up)

Before any other step, the skill needs grounded facts about the vendor using it — what they actually do, what they don't, their real commercial offer, their visual brand system, their voice. Without this, the deck will infer vendor capabilities from the Value Pyramid's LLM-generated narrative (which is tuned to the *customer's* needs and will confidently claim capabilities the vendor doesn't have) and will fall back to generic visual styling that won't match the vendor's brand. Both are unacceptable on a customer-facing deck.

### Check for Existing Vendor Files

The skill uses two vendor-specific files, both in this skill's `references/` directory:

- **[references/vendor-context.md](references/vendor-context.md)** — what you say and stand for (positioning, real capabilities, honest boundaries, commercial offer, voice, market POV)
- **[references/vendor-branding.md](references/vendor-branding.md)** — how the deck looks (colour palette, typography, background strategy, slide design tokens, visual tone)

**If both present**: load both verbatim, run the currency check below, and proceed to Step 1. Their contents are passed to the transform prompts (Step 4) and the deck-generation script (Step 7) later.

**If either missing**: offer the guided setup before proceeding. Do not attempt to generate a deck without vendor context.

### Currency Check (every run)

Read the `Last reviewed` line in each file's Maintenance section (currently 2026-04-21). Before a date-sensitive claim reaches a slide or shapes a CTA, verify it against a current authoritative source:

- **Commercial offer** — programme name, price mechanics, cohort names, slot counts and launch dates. A cohort whose window has passed, or whose current status you cannot confirm, is an **expired claim**: do not reference it, and do not let Transform F propose it.
- **Proof points and reference customers** — use only entries that are current and permissioned. A named customer needs explicit reference permission from a current source; an anonymised outcome needs current evidence. Never use a placeholder proof point, a "[customer name]" stand-in, or a bracketed TODO; an empty Proof Points section simply means no proof line on the slide.
- **Recently shipped capabilities** — confirm anything that reads as new or roadmap-adjacent before it goes on Slide 6 or 7.

Verify with the web fetch / search tools available in the session (prefer the vendor's own live pages) or ask the user to confirm. Record the source URL and access date for each verified fact in Slide 0's speaker notes. If a claim cannot be verified, leave it out and list it in the delivery note as "skipped — unverified". Verification shapes this deck only; it does not rewrite the reference files.

### Guided Setup Ritual (first-run, or on an explicit refresh request)

Tell the user:

> No vendor context is set up yet. I need a few facts about your company to generate a deck that claims only what you actually do. This is a one-time setup that takes about 5 minutes. I'll show you the drafts and only save them if you say so. You can refresh it any time by saying "refresh vendor context". Ready?

If they say yes, run the setup in this order:

**Part A — Web research (silent, ~60 seconds)**

Ask: *"What's your company name and website URL?"*

Once received, run in parallel with the session's web fetch and web search tools:
- Fetch the homepage — pull hero message, mission, category language
- Fetch `/about` or `/company` if linked — mission, founder story, tone
- Fetch `/product` or `/features` or `/platform` — capabilities as publicly described
- Fetch `/customers` or `/case-studies` — named references, logo wall
- Fetch `/pricing` if public — commercial structure
- Search `[Company name] founder recent blog post` — surfaces recent tone-of-voice material
- Search `[Company name] positioning category` — surfaces how they describe themselves in third-party coverage

Extract from these: positioning, category language, signature concepts, published features, customer names, pricing mechanics, recent voice samples. Record the URL and access date for every fact you keep — they go into the draft's Maintenance section as a Sources list.

**Part B — Focused questions (the things web scraping can't answer)**

Ask these as one combined message, not sequentially — the user can answer in one pass:

> A few things I can't pick up from the web. Answer whatever you can; blanks are fine:
>
> 1. **What do you NOT do?** (Features you're often asked for but don't have. Integrations you don't support. Adjacent problems you don't solve. This is the most important question — it's what prevents the deck from over-claiming.)
>
> 2. **What's your current commercial offer?** (E.g., "Founding Partner Programme — USD 9/user/month for 3 months, mutual commitment". Just the mechanics; pricing won't appear on the deck but the skill needs to know what you're actually proposing.)
>
> 3. **Any proof points / named reference customers** you're willing to cite in a first meeting? (Empty is fine — don't invent.)
>
> 4. **Brand voice in 3 adjectives.** (Words that actually change how a sentence is written, not marketing-speak.)
>
> 5. **Phrases you never want to use.** (E.g., "solution", "game-changer", "transform your business".)
>
> 6. **Brand palette** — primary colour, secondary colour, dark background, light background. (Hex codes if you have them, or describe them: "our primary orange, darker grey backgrounds"; I can pick exact values.)
>
> 7. **Preferred typefaces** for headers and body. (E.g., "Helvetica Neue for headers, Calibri for body"; or "whatever works — we don't have a strong opinion".)
>
> 8. **Background preference** — do customer-facing decks typically use dark backgrounds throughout (brand-forward), or light content slides with dark title/close (conventional B2B)?

**Part C — Synthesise and review**

Combine web-research findings with the focused-question answers into **two drafts**. There is no blank template file; use these section structures (they match the installed files, so the transforms and generation script can read either):

- **vendor-context.md** —
  1. *Vendor Identity*: company name, one-line description, website, primary audience
  2. *Positioning*: category / how we describe ourselves, canonical positioning statement, positioning formula, signature concepts / frameworks
  3. *Real Capabilities — What We Actually Do*: grouped by area, each a concrete shipped capability
  4. *Honest Boundaries — What We Do NOT Do*
  5. *Proof Points*: named reference customers (only with permission), anonymisable outcomes (only with current evidence)
  6. *Current Commercial Offer*: offer name, key mechanics, typical first-meeting CTA
  7. *Voice*: brand voice in 3 adjectives, required voice patterns, language we never use
  8. *Market Point of View*: the vendor's deliberate public positions
  9. *Maintenance*: last reviewed date, reviewed by, sources (URL + access date)
- **vendor-branding.md** —
  1. *Colour Palette*: brand colours and neutral palette (hex)
  2. *Slide Design Tokens*: a table mapping each token used in Steps 6–8 (`title-slide-bg`, `content-slide-bg`, `title-on-dark`, `title-on-light`, `body-on-dark`, `body-on-light`, `accent-primary`, `accent-secondary`, `muted`, `divider`) to a hex value and usage
  3. *Background Strategy*: Pattern A (bookended) or Pattern B (dark throughout)
  4. *Typography*: header, body and accent typefaces, weights in use
  5. *Signature Visual* (optional): the one structural diagram, its placement, rendering and when to skip
  6. *Visual Tone*, *What to Avoid*, *Accessibility Notes*
  7. *Maintenance*: last reviewed date, reviewed by

Leave a field empty rather than writing a placeholder. Never put a bracketed TODO in a draft — list open gaps as numbered questions in chat instead.

Show both drafts to the user in sequence:

> Here's the draft vendor context I've built. Skim it — correct anything wrong, answer the open questions listed below it, reply "looks good, save it" to save, or tell me what to change.

After vendor-context.md is approved:

> And here's the branding file — visual design tokens for the deck. Same drill — correct, fill gaps, or approve.

Iterate until both are approved. **Ask before writing**: save each file to `references/vendor-context.md` and `references/vendor-branding.md` only after the user explicitly says to save. If the skill directory is read-only (for example an uploaded skill), hand the user the approved drafts as files to install instead, and use them in-conversation for this deck.

**Part D — Proceed**

Confirm: *"Saved. Moving on to generate the deck."* Continue to Step 1.

### Refresh Command

If the user says "refresh vendor context" or "refresh vendor branding" or "refresh both" at any point, confirm which file(s) and sections are in scope, re-run the relevant Part A + B + C sequence, and show the proposed evidence-backed changes (what changes, and the source URL + access date for each). Overwrite the file(s) only after the user approves. Useful when positioning evolves, new features ship, the commercial offer changes, or the brand palette gets updated. A deck run that merely finds a stale claim does **not** trigger a refresh — it skips the claim and mentions it in the delivery note.

### Degraded Modes

If the user really can't spare 5 minutes:
- Offer: *"Want to skip setup and paste 2-3 sentences about your company, what you do, and what you're offering? The deck will be weaker but workable."*
- Use the short input in-conversation for this deck. Offer to save it as a minimal `references/vendor-context.md` with a `## Minimal context — expand when possible` warning at the top, and write it only if the user says yes.

Never proceed with no vendor context at all. A generic first-meeting deck is worse than no deck.

## Step 1: Identify the Opportunity and Meeting Context

You need an opportunity ID plus context about who is attending. If the user provides an opportunity ID, call `get_opportunity` directly.

If they give a deal or account name:

1. Call `search_opportunities` with the name as the query
2. If multiple results come back, show them and ask the user to pick one. Do not continue until the opportunity is unambiguous
3. Call `get_opportunity` with the selected ID

### Critical Context Gathering

Before pulling data, confirm three things with the user. These change the deck materially, and guessing gets it wrong:

1. **Who is attending the meeting?** Names and roles if known. If not known, at minimum: executive, functional, technical, procurement, or a mix. This drives which Value Pyramid layer to lead with on slide 6.

2. **Is this truly the first meeting?** Or a follow-up / a first meeting with a new stakeholder at an existing contact? This changes whether the deck references prior conversations ("as we discussed in November…") or starts fresh.

3. **How long is the meeting?** 30 / 45 / 60 minutes. Affects slide count — 30-min meetings get 6 slides max, 60-min meetings get the full 9.

4. **What is the meeting's objective?** (e.g., earn a working session, meet a new executive sponsor, re-open a stalled conversation). It shapes the lead hypothesis and the first next step.

Ask these as a single grouped question if they aren't already clear. Don't interrogate the AE — one well-structured clarifier is fine; three sequential ones will annoy.

## Step 2: Pull Data in Parallel

Launch these calls in parallel. Most are independent. Inspect each tool's live schema first (sample arguments here are semantic guidance), confirm optional tools with `list_available_tools`, and never pass `refresh: true`.

**Async note**: `external_account_research` (item 5 below) is asynchronous — queue it first when firing the parallel batch so its latency overlaps with the synchronous calls instead of gating the end of Step 2. Fire it, move on to the rest of the batch immediately, and only block on its result when Step 4's mirroring inputs are actually needed. Do not treat it as an immediate synchronous return: if it returns a processing envelope with a `job_id`, poll `get_job` until the job is terminal, then re-call with identical arguments for the payload. A processing envelope is never "no research".

### Required Data Pulls

1. **Opportunity & Account Basics**
   - `get_opportunity` with the opportunity ID — deal name, amount, stage, close date, account name, owner, account ID
   - `search_opportunities` filtered by the account ID — any related deals at this account

2. **Strategic Narratives** (the heart of the deck — run all in parallel)
   - `opportunity_three_whys` — strategic framing (Why Change / Why Now / Why Us), market forces, power phrases, objection pre-emption
   - `opportunity_discovery_planner` — discovery guide, key questions, opener framing, CTA
   - `opportunity_value_pyramid` — stakeholder-tiered value messaging across Executive / Functional / Technical / Procurement layers
   - `opportunity_stakeholder_intelligence` — stakeholder profiles, coverage gaps, engagement moves, org structure

3. **Deal Context**
   - `get_opportunity_notes_summary` — AI-generated narrative of prior interactions
   - `get_opportunity_notes` with `limit: 10` as a supplement — more raw detail for the transform step
   - `get_opportunity_activities` — prior touchpoints, who has been engaged

4. **Expansion Mode Detection**
   - `list_account_contracts` with the account ID — if contracts exist, fork to expansion-meeting mode (see Step 5)

5. **Prospect Language Mirroring**
   - `external_account_research` with the account ID and a positioning-focused query (e.g., "services offerings customers mission") — returns content scraped from the prospect's own website. Extract their self-description language, customer names, and positioning for echo-back throughout the deck. **Async — see the queuing note above.**

6. **Revenue Signals** (access-guarded — leader/admin or owning rep only)
   - `get_opportunity_signals` with the opportunity ID — the Revenue Signal Layer: the deal's actual first constraint to fix, ranked signals (evidence/confidence/severity), and win-probability movement. This exists to sharpen Transform A's hypothesis language with what's really blocking the deal, instead of relying solely on the Three Whys narrative.
   - **Access guard**: this tool is restricted to the opportunity's leader/admin or the owning rep. If the calling AE isn't authorized, the call returns an authorization error rather than data — treat that as an expected, non-fatal outcome. Catch it, skip this data pull, and let Transform A fall back to Three-Whys-only hypothesis generation (see Handling Missing Data below). Do not surface the authorization error to the user as a blocker, and do not attempt to retry with different credentials.
   - **Guardrail**: the `first_constraint` and win-probability narrative may shape hypothesis *language and emphasis* on Slide 3. The underlying scores, confidence values, and severity ratings are internal diagnostics — same category as MEDDPIC/BANT scores — and must never be printed on a customer-facing slide, even as a subtle label.

7. **Competitive & Knowledge Base Enrichment**
   - `get_battlecard` (exact competitor-name match only) with the competitor name(s) surfaced in Three Whys `direct_competitive_differentiation` (or named in `external_account_research` / supplied by the AE, if any) — returns up to 3 ranked candidate battlecards. Feeds Transform G with concrete, vetted differentiators and objection-handling language instead of the model inventing generic "we're better" framing.
   - **Graceful skip**: not every account has a competitor worth battlecarding, and not every competitor has a battlecard in the Knowledge Base. If `get_battlecard` returns no candidates, skip it — Transform G falls back to Three-Whys-only differentiation (see Handling Missing Data).
   - `search_knowledge` with a query built from the account's industry, use case, or stakeholder focus (e.g., "[industry] case study outcomes") — searches the org Knowledge Base across positioning, case studies, product, and battlecard assets. Pulls real case studies and positioning snippets as proof points for Transform D (Capability, Slide 6) and Transform E (Value Preview, Slide 7), supplementing the often-thin or placeholder Proof Points section in `vendor-context.md`.
   - **Graceful skip**: if `search_knowledge` returns no relevant matches, proceed without KB-sourced proof points — `vendor-context.md`'s own Proof Points section (even if thin) remains the fallback. Do not invent a case study to fill the gap.
   - **Both are supplementary, never a bypass**: whatever these two tools contribute still has to clear the Transform Quality Check's vendor-grounding rules in Step 4 — a compelling battlecard line or KB case study does not override `vendor-context.md` Real Capabilities or Honest Boundaries.

8. **Framework Gaps for AE Prep** (Slide 0 only — never customer-facing)
   - `opportunity_framework_summary` with the opportunity ID and the framework active on this deal (MEDDPIC or BANT, whichever the opportunity is scored against) — pulls qualification gaps and scores that feed a new "What to probe" band on Slide 0.
   - **Hard rule, reinforcing the existing one**: this output is AE-prep material only. It must never be transformed into customer-facing language or appear anywhere on Slides 1–9. See the Slide 0 spec in Step 6 and the audits in Step 8.
   - If the framework hasn't been scored yet or the call returns empty, omit the Slide 0 band rather than rendering placeholder gaps (see Handling Missing Data).

9. **Target-account context** (optional enhancement — requires the customer's Outreach plan; read-only)
   - When the prospect was worked as an outreach target account, its stored thesis, buying committee and research ground the deck far better than a cold start. Confirm `search_target_accounts`, `get_target_account` and `get_stakeholder_research_brief` are exposed with `list_available_tools`. If they are absent, access-denied or plan-gated, skip this pull, continue, and list "Target-account context: unavailable" in the delivery note.
   - **Find and confirm the match.** Call `search_target_accounts` with `query` set to the account's company name (then its website domain if the name finds nothing). A result is the same prospect only when its name or domain matches the opportunity's account, and — where the target account has an `opportunity_id` or `crm_account` — that value matches the resolved opportunity or account. Several plausible candidates: list them and ask, or skip. Never use a near-match name.
   - **Read the matched account.** `get_target_account(target_account_id)` → `thesis`, `committee[]` (`committee_role`, `committee_angle`, `engaged`, `last_touch_date`), `coverage.roles[]` and `coverage.gaps`, `external_research{researched_at, results[]}`. `get_stakeholder_research_brief(target_account_id)` adds the account summary, mapped committee and coverage gaps; use it read-only and ignore its `suggestions[]` workflow.
   - **How each field shapes the deck** (inputs only — see the customer-facing safety rule below):
     - `thesis` → the seller's "why you, why now" framing: an input to Slide 2 (Why We're Here) and to Transform A's hypothesis emphasis, cross-checked against Three Whys `why_now`. It is never quoted verbatim on a slide.
     - `committee[]` roles and `committee_angle` → who is likely in the room and what each person cares about. Use them to answer Step 1's attendee question (confirm with the AE rather than assume), to choose the Value Pyramid layer for Transforms D and E, and to shape Transform B's agenda emphasis. Map into the existing transforms; do not add slides for it.
     - `coverage.gaps` (e.g. no economic buyer mapped) → raw discovery questions on Slide 0 ("Who signs off on this budget?") and a candidate for Transform F's coverage-gap next step ("a short session with whoever owns the budget decision"). For a single-threaded account `coverage_applicable` is false and `coverage_pct` is `null` — no gaps by design, not 0% coverage.
     - `external_research.results[]` → research inputs alongside Step 3's fresh signals: keep each result's `url` and `published_date`, plus the digest's `researched_at`. A digest older than ~90 days is possibly stale — re-verify any fact from it with the session's web tools before it reaches Slide 2, or leave it off. Every fact used carries its URL + date in the speaker notes, exactly like a fresh signal.
   - **Customer-facing safety.** `tier`, `fit_rating`, coverage percentages, `touch_history`, coordination state, `stage`, and `committee_role` labels (especially "blocker", "economic_buyer", "champion") are internal targeting data. They shape content only and never appear on any slide, Slide 0 included — on Slide 0, describe a person by what they care about (their `committee_angle`), not by their role label. Slide 0 may list coverage gaps as raw "who do we still need to meet" questions.
   - **Never write.** Do not call create/update/convert target-account tools, `submit_stakeholder_suggestions`, `accept_stakeholder_suggestion` or `dismiss_stakeholder_suggestion`, and do not pass `target_account_id` to `external_account_research` (that refreshes the stored digest). Use the stored digest as returned.

### Narrative Freshness Check

After pulling the three strategic narratives, check the `last_updated` field on each. If any is older than 14 days OR the `is_stale` flag is true, surface a warning before proceeding:

> ⚠️ The Three Whys narrative was last updated [N] days ago. Notes added since then won't be reflected. Want me to proceed, or regenerate the narrative first? (Regeneration requires the in-product tool, not this skill.)

Let the user decide — don't auto-block.

### Handling Missing Data

First meetings often have sparse data. Adapt gracefully:

- If `opportunity_three_whys` returns empty, the skill cannot meaningfully proceed — stop and tell the user: "The Three Whys narrative hasn't been generated for this opportunity yet. Please run that first, then re-run this skill."
- If `opportunity_discovery_planner` is empty, fall back to generic discovery agenda derived from the Three Whys Why Change section
- If `opportunity_value_pyramid` is empty, skip slide 7 (value preview) entirely rather than showing a thin version
- If `opportunity_stakeholder_intelligence` is empty, fall back to the AE's answer from Step 1
- If `get_opportunity_notes_summary` and `get_opportunity_notes` both return empty, this is likely a genuinely-first meeting — proceed without prior-conversation references
- If `external_account_research` returns empty, skip prospect-language mirroring
- If `list_account_contracts` is empty, proceed in net-new meeting mode (the default)
- If `get_opportunity_signals` returns an authorization error (caller isn't leader/admin/owning rep) or is empty, proceed with Three-Whys-only hypothesis generation for Transform A — no warning needed, this is an expected access boundary, not a data gap
- If `get_battlecard` returns no candidates, skip battlecard grounding for Transform G and fall back to Three-Whys-only differentiation (`why_us` + `direct_competitive_differentiation`)
- If `search_knowledge` returns no relevant results, proceed without KB-sourced proof points for Transforms D and E — `vendor-context.md` Proof Points remains the only source
- If `opportunity_framework_summary` is empty or the framework is unscored, omit the Slide 0 "What to probe" band entirely rather than rendering it with placeholder gaps
- If the target-account tools are unavailable, plan-gated or denied, or no target account confidently matches the prospect, build the deck exactly as before and note "Target-account context: unavailable" (or "no confirmed match") in the delivery note. An empty `committee[]` or `external_research` is unavailable evidence, never "no stakeholders" or "no news"

## Step 3: Fresh Signals (Optional — Progressive Disclosure)

The strategic narratives capture the AE's prior understanding but don't include fresh external signals (news from this week, recent announcements, LinkedIn posts). `external_account_research` is domain-scoped to the account's own site, so cannot surface these. The skill offers an opt-in research step using the session's web search and fetch tools. Every fact kept from this step is recorded with its source URL and access date, and stays a dated fact — it never becomes CRM evidence, and a hypothesis built on it stays a hypothesis.

### Offer the Signal Search

After data pulls complete, prompt the user:

> Baseline deck is ready to build. Want me to also research fresh signals (news, funding, announcements) to ground the hypothesis slide in current context? Adds ~60 seconds. Reply "yes", "skip", or specify a focus (e.g., "just leadership changes").

If skip, proceed to Step 4. If yes:

### Targeted Category Search

Run **five bounded web searches** with the host's web search tool, one per category. Keep queries short (3–6 words):

1. **Capital events** — `"[Account name] funding acquisition [current year]"`
2. **Leadership changes** — `"[Account name] CEO appointment hire"`
3. **Product/strategic moves** — `"[Account name] launch announcement"`
4. **Partnerships** — `"[Account name] partnership integration"`
5. **Market/regulatory shifts** — search the account's sector for recent news affecting them

Adapt based on what the account actually is. Drop irrelevant categories silently.

### Curate and Present

From the search results, select at most **1–2 findings per category** that are:
- Dated within the last 90 days of the run's as-of date (the org-scoped `as_of` the Summit53 tools return; see [host-adapters.md](references/host-adapters.md#dates)) (check the publication date on the page itself, not the search snippet)
- Clearly about *this* company (not a namesake)
- From a primary or reputable source — prefer the prospect's own site, filings and press releases
- Relevant to the Why Change / Why Now narrative

Present as a structured review:

> Found these fresh signals — pick which to include (max 3 on the deck):
>
> 1. [Headline, date, 1-line why it matters] — [source URL, accessed YYYY-MM-DD]
> 2. ...
>
> Reply with the numbers (e.g., "1, 3"), "all", "none", or "skip".

Cap the deck at 3 signals — more becomes noise. For each selected signal, keep the URL and access date: put the date on Slide 2 and the URL + access date in Slide 2's speaker notes.

If web search returns nothing meaningful:

> No fresh signals surfaced in the last 90 days. Proceeding without a signals section.

Proceed without blocking.

## Step 4: Transform Narratives (Hybrid LLM Step)

This is the quality-critical step. Pre-computed narratives are tuned for internal strategic use; the deck needs customer-facing voice. Transform the existing narratives with the host model, grounded in the vendor context from Step 0.

**Every transform that makes capability or outcome claims must take `vendor-context.md` as an input** — this is the guardrail against over-claiming.

### Transform Prompt Contracts

Each transform has four parts: **inputs**, **vendor grounding**, **instruction**, **output shape**.

---

**Transform A — Hypothesis Generation (feeds Slide 3)**

*Inputs:*
- Three Whys → `why_change` full text
- Notes summary (for freshness)
- AE-selected fresh signals (if any)
- Prospect self-description from `external_account_research`
- `get_opportunity_signals` output, if the caller was authorized — the `first_constraint` and win-probability movement narrative
- Target-account `thesis` and dated `external_research` results, if a confirmed target account was found (Step 2, item 9) — shape emphasis only; never quote the thesis

*Vendor grounding:* Not required — this slide is entirely about the customer.

*Instruction:*
> Generate exactly 3 hypothesis statements about what this prospect is navigating right now. Each must:
> - Be 2 sentences max
> - Open with "Our hypothesis is that…" or "We believe…"
> - Reference specific facts (the acquisition, the market shift, the funding event)
> - Mirror the prospect's own language where possible
> - Avoid any reference to the vendor or their product — this slide is about *them*
> - The slide (not each statement) ends with one invitation: "Is this right? What would you challenge?"
>
> If Revenue Signals were retrieved, let the deal's actual `first_constraint` sharpen which hypothesis leads and how confidently it's worded — e.g., a signal flagging "no economic buyer identified" as the first constraint should surface as a hypothesis about executive alignment or sponsorship, not a generic pain-point guess. **Use the signal to shape hypothesis language and priority only — never print the signal's score, confidence value, or severity rating.** If Revenue Signals weren't available (access-denied or empty), generate the hypotheses from the Three Whys narrative alone, exactly as before.

*Output shape:* `{ hypotheses: [string, string, string], invitation: string }`

---

**Transform B — Discovery Agenda (feeds Slide 4)**

*Inputs:*
- Discovery Planner → `discovery_guide` section (key questions block)
- Stakeholder Intelligence → attendees from Step 1
- Target-account `committee_angle` for each confirmed attendee and `coverage.gaps`, if available — shape emphasis, never name a role label

*Vendor grounding:* Not required — this slide is about what we want to learn from them.

*Instruction:*
> Convert the internal discovery questions into a customer-facing agenda. Rules:
> - Exactly 4 agenda items
> - Each phrased as "We'd like to understand [topic]" / "We'd love to explore [topic]" — not a direct question
> - One line each, scannable in 2 seconds
> - Order: 1) their reality today, 2) what's changing, 3) what success looks like, 4) how we might fit
> - Remove presumptuous items (e.g., budget) — defer those

*Output shape:* `{ agenda: [string, string, string, string] }`

---

**Transform C — Market Point of View (feeds Slide 5)**

*Inputs:*
- Three Whys → `market_forces_demanding_new_approaches` section
- Three Whys → `competitive_disadvantages` section (context only)

*Vendor grounding:*
- `vendor-context.md` → **Market Point of View** section — the vendor's own deliberate public positions

*Instruction:*
> Create a point of view about the prospect's market — not about the prospect, not about the vendor's product. Rules:
> - Lead with the vendor's Market Point of View from vendor context — these are their deliberate positions, use them
> - Cross-reference Three Whys market forces for deal-specific grounding
> - 2–3 observations total
> - **At least one observation must open with explicit first-person attribution** — "Our working thesis is that…" / "The way we see it…" / "We believe…" — transforming the observation from anonymous industry commentary into the vendor's distinctive point of view. This is a Why-Us proof point: it signals the vendor has a thesis, not just an opinion.
> - Framed as industry analysis, not as a threat to them
> - Each 1–2 sentences
> - No product references
> - No competitor or vendor brand names: if the vendor's Market Point of View names specific tools or companies, translate them into a category (e.g., "a stack of point tools plus a RevOps hire") unless the user explicitly asked for named comparisons
> - End with a transition like "This is the context in which we think [their firm] has a real opportunity."

*Output shape:* `{ observations: [string, ...], transition: string }`

---

**Transform D — Capability Statement (feeds Slide 6, net-new mode)**

*Inputs:*
- Value Pyramid → the stakeholder layer matching who is attending
- Three Whys → `critical_capabilities_gaps` section
- `search_knowledge` results (if any) — real case studies / positioning snippets as supplementary proof points

*Vendor grounding (CRITICAL):*
- `vendor-context.md` → **Real Capabilities** — the only source of truth for what the vendor does
- `vendor-context.md` → **Honest Boundaries** — what the vendor does NOT do
- `vendor-context.md` → **Proof Points** — anonymisable evidence
- `vendor-context.md` → **Positioning** → Canonical positioning statement + Signature concepts/frameworks — the vendor's distinctive architectural claim

*Instruction:*
> Generate 2–3 capability statements showing how the vendor typically helps firms like this. Rules:
> - **The FIRST statement must open with the vendor's canonical positioning language** from vendor-context.md — not a generic "we help you achieve X" framing. For Summit53, this means the lead statement explicitly frames Summit53 as the "Revenue Engine architected around the bow-tie" or equivalent Signature Concept phrasing. This is where the distinctive positioning flag gets planted.
> - **Every claim must map to a capability in vendor-context.md Real Capabilities.** If a capability would help the customer but isn't listed, do NOT include it — that's an over-claim.
> - Cross-check Honest Boundaries — if a statement drifts into something the vendor doesn't do, reframe.
> - Subsequent statements open with what the customer achieves (outcome), not what the vendor does. Example: "Advisory teams stop spending 40% of their time on production and redirect it to strategic work."
> - Match the stakeholder layer
> - If Proof Points has an anonymisable entry that passed the Step 0 Currency Check, weave one in as: *"A similar [type] committed to [outcome] — [progress]."* If `search_knowledge` surfaced a relevant case study or positioning snippet, it may be used instead of, or alongside, the vendor-context.md Proof Points entry — but it is still subject to the same rule as everything else in this transform: it must describe a capability that is actually listed in vendor-context.md Real Capabilities. A compelling KB case study about a capability outside Real Capabilities does not get used.
> - Stay concrete. No vague "drives efficiency" claims.

*Output shape:* `{ positioning_headline: string, capabilities: [{ outcome: string, supporting: string }, ...], proof_reference?: string }`

Note the added `positioning_headline` field — this is a single bold line that opens Slide 6 above the capability statements, anchoring the whole slide in the vendor's distinctive positioning.

---

**Transform G — Why Us / Differentiation (feeds the closing band of Slide 6)**

*Inputs:*
- Three Whys → `why_us` section (the differentiated value proposition)
- Three Whys → `direct_competitive_differentiation` subsection — this enumerates the realistic alternatives the prospect is weighing (build internally, generic BI tools, competitor platforms)
- `get_battlecard` output (if a competitor match exists) — vetted differentiators and objection-handling language for the named comparison category

*Vendor grounding:*
- `vendor-context.md` → **Positioning** → Signature concepts/frameworks
- `vendor-context.md` → **Honest Boundaries** — don't claim superiority in areas the vendor doesn't actually operate

*Instruction:*
> Generate exactly 2 differentiation claims addressing the alternatives the customer is realistically weighing. Rules:
> - Each claim is one sentence, max ~25 words
> - Each must implicitly or explicitly address a real alternative the prospect is considering — e.g., *"A BI tool gets you X; what the bow-tie gives you is Y"* or *"Building this internally with Multiplier's engineers would take 18 months; we start next week"*
> - Reference comparison *categories* (generic CRM, build-internally, point BI tools) — never name specific competitor brands unless the user explicitly asked for a named comparison and the evidence is current. First meetings are not the place for named competitive attacks.
> - Each claim must ground in a vendor Signature Concept or capability that genuinely differentiates — avoid hollow "we're more intuitive / more modern / faster" claims
> - If a `get_battlecard` match exists for a comparison category the prospect is realistically weighing, ground the claim in the battlecard's vetted comparison points and objection-handling language instead of inventing generic "we're better" framing — but the comparison-category rule still applies: translate the battlecard's specifics into a category claim, never a named competitor brand, and never claim strength in anything listed in Honest Boundaries.
> - No hedging. No "we think we're better". Make a specific claim.

*Output shape:* `{ differentiators: [string, string] }`

---

**Transform E — Value Preview (feeds Slide 7)**

*Inputs:*
- Value Pyramid → the stakeholder layer matching attendees. **Filter non-negotiable.** Exec attendees → Executive layer. Functional champion → Functional layer. Mixed → Executive + Functional. Never Technical or Procurement on a first meeting.
- Three Whys → `critical_success_factors` section
- `search_knowledge` results (if any) — supplementary case-study evidence for outcome hypotheses

*Vendor grounding (CRITICAL):*
- `vendor-context.md` → **Real Capabilities** — outcomes must be achievable with real capabilities
- `vendor-context.md` → **Honest Boundaries** — cross-check deliverability

*Instruction:*
> Generate exactly 3 outcome hypotheses — what success could look like in 12 months. Rules:
> - Each outcome must be achievable using only capabilities in vendor-context.md Real Capabilities. If it requires something not listed, pick a different outcome.
> - Framed as a hypothesis, not a promise ("Our hypothesis is that together we could…")
> - Each has a concrete metric or qualitative outcome (no vague "efficiency gains")
> - Each ties to what the stakeholder-tier cares about
> - Realistic — no 10x claims in a first meeting
> - If `search_knowledge` surfaced a relevant case study, one outcome hypothesis may reference it as grounding evidence — still phrased as a hypothesis, not a guarantee, and only for an outcome whose underlying capability is already in vendor-context.md Real Capabilities
> - End with: "None of this is a promise. It's a starting hypothesis we'd want to test together."

*Output shape:* `{ outcomes: [{ headline: string, detail: string }, { ... }, { ... }], disclaimer: string }`

---

**Transform F — Closing CTA (feeds Slide 8)**

*Inputs:*
- Discovery Planner → `next_steps_and_action_plan` section
- Stakeholder Intelligence → coverage gaps
- Target-account `coverage.gaps`, if available — phrased as a person or decision to meet, never as "gap" or a role label

*Vendor grounding:*
- `vendor-context.md` → **Current Commercial Offer** — real offer mechanics and typical first-meeting CTA

*Instruction:*
> Generate 2–3 proposed next steps for the customer to agree to in the meeting. Rules:
> - First step is the vendor's typical first-meeting CTA from vendor-context.md, phrased for this specific prospect
> - Subsequent steps fill coverage gaps if stakeholder intelligence shows them
> - No pricing, contract terms, or "sign here" energy
> - Never propose anything not aligned with the vendor's actual offer (e.g., don't propose a "free trial" if they don't offer one)
> - Never reference an offer, programme, cohort or slot count that did not pass the Step 0 Currency Check — an expired cohort is not an offer
> - One sentence each, action-oriented, time-bound where possible

*Output shape:* `{ next_steps: [string, ...] }`

---

### Transform Quality Check

After all transforms complete, scan for:
- Any capability claim not backed by `vendor-context.md` Real Capabilities → rewrite or remove
- Any outcome requiring a capability in Honest Boundaries → rewrite
- "Your platform" / "our solution" / "our product" before slide 6 → rewrite
- Declarative assertions without invitation voice on slide 3 → rewrite
- Qualification framework scores → strip
- Banned phrases from `vendor-context.md` Language We Never Use → rewrite
- **Slide 6 positioning headline from Transform D must use at least one Signature Concept from vendor-context.md** — if it doesn't, re-run Transform D with a sharper positioning mandate
- **Transform C must have at least one observation with explicit first-person attribution** — if no "Our working thesis is…" / "We believe…" / "The way we see it…" appears, re-run Transform C
- **Transform G differentiators must reference real alternatives** (build internally, generic CRM, point BI tools, etc.) — vague "we're better" claims without a comparison class fail the check
- **Any claim sourced from `search_knowledge` must still map to `vendor-context.md` Real Capabilities** — a compelling Knowledge Base snippet does not override Honest Boundaries; it supplements the vendor-grounding check, it never bypasses it
- **Any differentiator sourced from `get_battlecard` must still reference a comparison category, not a named competitor brand**, and must still pass the Honest Boundaries check — battlecard specifics get translated into category claims, not pasted in raw
- **Any Revenue Signal Layer score, confidence value, or severity rating leaking onto a customer-facing slide** → strip immediately, same rule as other framework scores
- **Any MEDDPIC/BANT gap language from `opportunity_framework_summary` appearing anywhere outside Slide 0** → strip immediately — this data is AE-prep-only by definition and must never reach a customer-facing slide
- **Any bracketed TODO, placeholder value, "[customer name]"-style stand-in, placeholder proof point, unconfirmed reference customer, or expired cohort/offer claim** → remove; the slide is better without it
- **Any date-sensitive claim (offer, cohort, proof point, new capability, fresh signal) without a verified current source** → remove and list as "skipped — unverified" for the delivery note
- **Any named competitor brand on Slides 1–9** the user did not explicitly ask for → translate to a comparison category
- **Any hypothesis phrased as fact, or any web fact presented as CRM evidence** → rewrite
- **Any target-account internal field on any slide** — tier, fit rating, coverage %, touch history, stage, the target-account thesis verbatim, or a committee-role label such as "blocker" or "economic buyer" → strip; use it only to shape content

Re-run failed transforms with the specific failure as additional context.

## Step 5: Detect Meeting Mode and Adapt

Two modes, detected from the data:

**Net-New Meeting Mode** (default)
- Triggered when `list_account_contracts` is empty
- Deck treats this as an acquisition conversation
- Slide 6 uses Transform D output
- Slide 7 uses Transform E output

**Expansion Meeting Mode**
- Triggered when `list_account_contracts` returns active contracts
- Deck opens by acknowledging the existing relationship
- Slide 6 replaced with "What we've delivered for [Account] so far", built from:
  - `get_value_impact_card` — evidence narrative (strip scores)
  - `list_impact_entries` for the primary contract — real delivered outcomes
- Slide 1 subtitle shifts to "Expanding the Partnership"
- Hypothesis voice softens slightly — you've earned a bit more directness

Detect once, early. Build the whole deck in that mode. Do not mix.

## Step 6: Build the Deck

Build the deck with the host presentation toolchain ([host-adapters.md](references/host-adapters.md#building-slides)); read that toolchain's instructions before writing any code. Apply the **design system from [references/vendor-branding.md](references/vendor-branding.md)** — colours, typefaces, background strategy, slide design tokens, visual tone. All branding choices come from that file, never hardcoded in this skill. The slide-level instructions below use the token names defined in `vendor-branding.md`'s **Slide Design Tokens** table — resolve each token to its hex value at generation time.

### Layout Philosophy (vendor-agnostic)

Regardless of brand:
- 16:9 widescreen, 0.75" margins minimum
- Dark title/close slides, light content slides
- **Lots of whitespace**. Customer-facing slides should never feel crammed.
- **No stat cards or dashboard-style elements.** Those feel internal. Use editorial blocks instead.
- **Minimal iconography.** No emoji, no decorative shapes. One accent element per slide max.
- Body text 16–20pt — larger than diagnostic decks because customers should read this, not scan it

### When to Use Visuals vs Prose

The deck is text-led by design — the editorial voice carries the weight, and filling every slide with diagrams turns it into a generic SaaS pitch. But **some concepts are structural**, and for those, shape carries meaning that prose genuinely can't.

Rule of thumb: use a visual when the underlying concept IS the shape. Use prose when the underlying concept is a claim, argument, question, or story.

**Concepts that warrant visuals:**
- Architectural shapes (bow-tie, figure-eight, pyramid, quadrant, loop) — these are inherently visual claims
- Temporal progressions (timelines, stages, phases) — time IS a visual axis
- Comparisons where positions matter (quadrants, 2x2s) — location in space carries meaning

**Concepts that should stay prose:**
- Hypothesis statements — language carries precision that shapes can't
- Market observations — observations are verbal claims
- Discovery questions — questions are language-native
- Outcome hypotheses — future states are narrative
- Next steps — actions are verbs

**The one signature visual rule:** a deck gets at most ONE signature visual, placed on Slide 6 where positioning lands. Vendors that don't have a structural positioning concept skip the visual entirely — a text-only Slide 6 is perfectly valid. Defining the signature visual lives in `vendor-branding.md` (see the Signature Visual section); the skill reads it and renders it conditionally.

### Slide Structure

Slide 0 (AE Prep Notes) is **always** included and **always** visually distinct. It lives inside the deck (not a separate prep file) so the AE can open one PPTX and have both the customer-facing slides and the pre-meeting material in one place. It is NOT marked hidden in the XML — Google Slides, lightweight previewers, and some mobile clients skip hidden slides entirely in the editor, which defeats the whole purpose. Instead, the slide is rendered with unmissable visual signals (bold accent-primary header strip with "AE PREP · DO NOT PRESENT", muted content overlay, dense prep-style layout) so the AE can spot it at a glance in the slide navigator and **manually skip it when starting presentation mode**. The remaining customer-facing slides are adaptive to meeting length:

- 30-minute meeting: Slides 0, 1, 2, 3, 4, 8, 9 (skip market POV and value preview)
- 45-minute meeting: Slides 0, 1, 2, 3, 4, 6, 8, 9 (skip market POV)
- 60-minute meeting: all slides (0 through 9)

---

#### Slide 0: AE Prep Notes *(always present, always visually distinct, manually skipped in presentation)*

This is the only slide the prospect must never see. It is the AE's cockpit: a single-page view of the narrative arc, the raw internal discovery questions (the unsanitised versions, not the "we'd like to understand" rewrites on Slide 4), the full Value Pyramid across all four stakeholder tiers (not just the filtered layer on Slide 7), the objection watchouts, and the deal's qualification framework gaps. Reviewed before the meeting, glanced at during, and — because no hidden-slide safety net is assumed — consciously skipped when entering presentation mode. The visual treatment below is the forcing function that makes accidental presentation essentially impossible.

- **No hidden flag**: Slide 0 is rendered as a normal, visible slide. Do NOT set any hidden-slide option in the build toolchain (for example PptxGenJS's `{ hidden: true }`) or inject `show="0"` into the XML. This is a deliberate change from a prior iteration of this skill: Google Slides and several preview clients silently skip hidden slides from the editor as well as from presentation mode, which hides the prep material from the AE who needs it most. The AE is expected to manually skip Slide 0 when starting presentation mode (right-click the thumbnail → "Skip slide" in Google Slides; simply advance past it in PowerPoint/Keynote). The visual signals below make this a conscious one-keystroke action, not something the AE can miss.
- **Background**: `content-slide-bg` with a subtle `muted` overlay (~10% opacity) so the slide is visually distinct from customer-facing slides even on a casual scroll-through. Combined with the header strip below, the "this doesn't look like the rest of the deck" cue is unmissable.
- **Top header strip (0.4" band — taller than it was, because it's now the primary safety net)**: `accent-primary` fill spanning the slide width. Left: bold caps **"AE PREP  ·  DO NOT PRESENT"** in `title-on-dark`, tracked wide (letter-spacing ≥ 4pt; `charSpacing` when building with PptxGenJS). Right: account name · meeting date · attendee names in `body-on-dark` 10pt. This strip must be the ONLY place in the entire deck where `accent-primary` appears as a full-width solid fill — so the AE's eye catches the orange bar instantly in the slide navigator thumbnail, distinguishing it from every other slide at a glance.
- **Band 1 — Narrative arc (single line, below header)**: one-sentence story compressed from Three Whys `why_change` + `why_now` + `why_us` power phrases. Shape: *"Why change → Why now → Why us."* Example: *"Advisory firms are stuck producing when they should be interpreting; AI has collapsed the production cost to zero; Summit53 is the Revenue Engine that lets them redirect the freed time."* Header typeface 14pt semibold, coloured `title-on-light`.
- **Band 2 — Discovery questions (left half of body)**:
  - Small caps label *"DISCOVERY — ANSWERS YOU WANT"* in `accent-primary`
  - 4–6 **raw** questions from `opportunity_discovery_planner` → `discovery_guide` key questions block. These are the blunt questions the AE is actually trying to get answered — not the customer-facing "we'd like to understand" rephrasings that appear on Slide 4. Body typeface 11pt, `body-on-light`.
  - For the top 2 questions, a "what good looks like" one-liner underneath in italic `muted` — a mental model for the kind of answer that would meaningfully advance the deal.
  - If a confirmed target account returned `coverage.gaps`, add up to two raw "who do we still need to meet" questions from them (e.g. "Who owns the budget decision?"). No role labels, coverage percentages, tier or fit rating.
- **Band 3 — Value Pyramid cheat sheet (right half of body)**:
  - Small caps label *"VALUE PYRAMID — ALL TIERS"* in `accent-primary`
  - Four compact rows in tier order: **Executive / Functional / Technical / Procurement**. Each row: tier label bold in `accent-secondary` 11pt, then a one-line value message in `body-on-light` 11pt. Source: `opportunity_value_pyramid`, compressed to one line per tier.
  - Purpose: Slide 7 shows only the filtered layer matching who was expected in the room. If an unexpected stakeholder walks in (a CFO joins what was billed as a VP Sales meeting), the AE has the right-tier message one glance away without fumbling through notes.
- **Band 4 — Watchouts (full-width bottom band)**:
  - Small caps label *"WATCHOUTS"* in `accent-primary`
  - Two columns:
    - **Left — "Objections to pre-empt"**: top 2–3 entries from Three Whys `pre_empted_objections`, condensed to "objection → one-line response posture"
    - **Right — "Do not say"**: banned phrases from `vendor-context.md` Language We Never Use, plus the standing rule *"No pricing, contract mechanics, or commitment language in the first meeting"*
  - Body typeface 10pt, `muted`
- **Band 5 — What to probe (framework gaps)**:
  - Small caps label *"WHAT TO PROBE — [FRAMEWORK] GAPS"* in `accent-primary` (substitute the actual framework name, e.g. "WHAT TO PROBE — MEDDPIC GAPS")
  - Source: `opportunity_framework_summary` for the opportunity's active framework. Show the 2–4 lowest-scoring or unaddressed elements (e.g., "Economic Buyer — not yet identified", "Paper Process — unclear") as a compact checklist, each with a one-line "what good looks like" prompt in italic `muted` underneath.
  - Because Slide 0 is AE-only, the framework scores/gaps themselves may render here — but keep the treatment small, muted, and checklist-style (not a headline stat) so it stays visually consistent with the rest of the prep slide rather than looking like something that could be mistaken for a customer-facing element.
  - **Hard rule, not just a style note**: this band's content must never be transformed into customer-facing language or copied onto Slides 1–9, under any circumstance. It is quarantined to Slide 0 the same way qualification framework scores are quarantined everywhere else in this skill — see the Transform Quality Check and the Step 8 QA audits.
  - **Graceful degradation**: if `opportunity_framework_summary` is empty or the framework hasn't been scored yet, omit this band entirely rather than rendering placeholder gaps.
- **Voice exemption**: unlike every other slide in this deck, Slide 0 uses **raw internal voice**. Discovery questions stay as questions ("What's their current advisory billable-time split?"), not softened to "we'd like to understand…". Stakeholder observations stay blunt. Framework gaps stay blunt too ("Economic Buyer — not yet identified", not "we'd like to understand who signs off"). This is a mental model for the AE, not a pitch — the customer-facing voice guardrails at the top of this file do not apply to Slide 0.
- **Transforms skipped**: Slide 0 is the one slide that bypasses Step 4 transforms entirely. Rendering uses raw outputs of `opportunity_discovery_planner`, `opportunity_value_pyramid`, `opportunity_three_whys`, and `opportunity_framework_summary` directly, with the generation script handling compression (truncation to one line per entry, max N items per band). Adding an LLM transform here would introduce a new over-claiming failure mode for no benefit — the data is already structured.
- **Density discipline**: this slide is read off a laptop, not projected, so use 10–12pt body text (smaller than customer-facing slides) to fit everything. Dense is acceptable; the AE zooms in if needed. Margins 0.5" (tighter than customer slides).
- **Graceful degradation**: if `opportunity_value_pyramid` only has Executive and Functional tiers, show those two and omit the others rather than rendering empty rows. If `pre_empted_objections` is empty, expand the "Do not say" column to fill the band. If `opportunity_framework_summary` is empty, omit Band 5 (see above). Never render a band with placeholder text.

---

#### Slide 1: Title Slide
- **Background**: `title-slide-bg`
- **Content**:
  - Main title: account name, header typeface 44pt, coloured `title-on-dark`
  - Subtitle: *"Initial Conversation"* (net-new) or *"Expanding the Partnership"* (expansion), coloured `body-on-dark`
  - Bottom strip: meeting date, AE name, vendor company name — coloured `body-on-dark` (vendor wordmark may use `accent-secondary` if specified in the branding Usage Patterns table)
- **Layout**: Centered, generous whitespace. Feels like the cover of a thoughtful memo.

---

#### Slide 2: Why We're Here
- **Background**: `content-slide-bg`
- **Data source**: Three Whys `why_now` + AE-selected fresh signals
- **Layout**: Title: *"Why we think now is the right moment to talk"* coloured `title-on-light`. 2–3 short editorial statements (1 sentence each) in `body-on-light`. If signals approved, integrate with dates visible. Thin `accent-primary` left margin on each statement. Prose, not lists.

---

#### Slide 3: Our Hypothesis About Your Business *(signature slide)*
- **Background**: `content-slide-bg`
- **Data source**: Transform A output
- **Layout**:
  - Top headline, header typeface 32pt, coloured `title-on-light`: *"Here's what we think is going on. Tell us where we're wrong."*
  - 3 hypothesis blocks stacked. Each with: a short `accent-secondary` label in caps (e.g., "MARKET REALITY", "OPERATIONAL PAIN"), the hypothesis in body typeface 18–20pt coloured `body-on-light`, thin `accent-primary` left border.
  - Bottom invitation in italic `body-on-light`: *"Is this right? What would you challenge?"*
- **Critical**: this slide does the most work. Give it space. Max 3 hypotheses.
- **Sharpened by Revenue Signals when available**: if `get_opportunity_signals` was retrieved (Step 2, item 6), the leading hypothesis reflects the deal's actual `first_constraint` — a sharper, more confident hypothesis than one derived from narrative alone. When Revenue Signals weren't available (access-denied or empty), this slide is built from Transform A's Three-Whys-only path with no visible difference in slide structure — the fallback is invisible to the prospect.

---

#### Slide 4: What We'd Like to Understand Today
- **Background**: `content-slide-bg`
- **Data source**: Transform B output
- **Layout**: Title: *"What we'd like to understand together"* coloured `title-on-light`. 4 agenda items with small `accent-primary` numerals, body text in `body-on-light`. Editorial, not project-plan.

---

#### Slide 5: A Point of View on Your Market *(60-min only)*
- **Background**: `content-slide-bg`
- **Data source**: Transform C output
- **Layout**: Title: *"How we see your market moving"* coloured `title-on-light`. 2–3 observations in prose (not bulleted), coloured `body-on-light`. Closing transition in italic.

---

#### Slide 6: How We Help Firms Like Yours *(45 and 60-min meetings)*

This slide does more work than any other content slide. It is the one place where the deck pitches — and it has to do three things in one frame: plant the distinctive positioning flag, show concrete capability grounded in real vendor features, and address the realistic alternatives the prospect is weighing. Lay it out as three vertical bands.

**Net-New Mode:**
- **Background**: `content-slide-bg`
- **Data sources**: Transform D output (positioning headline + capabilities, optionally sharpened by `search_knowledge` proof points), Transform G output (Why Us differentiators, optionally grounded in a `get_battlecard` match), `vendor-branding.md` → **Signature Visual** (optional — included if defined, skipped if not)

**Layout — three bands top to bottom:**

**Band 1 — Positioning anchor (top third)**
- Small caps label: *"WHERE WE HELP"* (or equivalent) in `accent-primary`
- Large positioning headline from Transform D's `positioning_headline` field, header typeface 28–32pt, coloured `title-on-light`. This is the distinctive claim — for Summit53, something like *"The Revenue Engine, architected around the bow-tie from day one."* Not a hedging "where we make a difference" title.
- If `vendor-branding.md` defines a Signature Visual: render it below the headline, right-aligned or centred per the branding file's placement guidance. Medium size (roughly 40% of slide width). Colours resolved from branding tokens.

**Band 2 — Capability claims (middle)**
- 2–3 capability statements from Transform D, rendered as editorial blocks
- Each block: short bold headline (e.g., "Advisory teams stop producing, and start interpreting.") in body typeface 18pt semibold, followed by 1–2 supporting sentences in body typeface 16pt
- The FIRST capability block follows the positioning headline's claim — it's the proof, not just an outcome
- If Transform D returned a `proof_reference`, include as a single italic line in `muted` at the end of this band — this may be sourced from vendor-context.md Proof Points or from a `search_knowledge` case study, per Transform D's rules

**Band 3 — Why us, specifically (bottom)**
- Thin divider in `divider` colour spanning most of the slide width
- Small caps label: *"WHY US, SPECIFICALLY"* in `accent-secondary`
- Two differentiator lines from Transform G, rendered as a tight vertical pair. Body typeface 14–16pt. Each line starts with a short thin accent mark (•, em-dash, or `accent-primary` bullet).
- Keep this band visually compressed — it's a closing punctuation mark, not the main event.

**Expansion Mode** (no changes from previous spec):
- **Background**: `content-slide-bg`
- **Data source**: `get_value_impact_card` (narrative only), `list_impact_entries`
- **Layout**: Title: *"What we've delivered for [Account Name] so far"* coloured `title-on-light`. 3–5 impact entries as editorial items: date in `muted`, outcome headline in `body-on-light`, one-sentence evidence in `body-on-light`. Ordered by recency. Strip scoring. End with forward-looking line: *"This is the foundation we'd build from."*
- Expansion mode skips Transform G (Why Us) — the existing relationship IS the Why Us proof.

---

#### Slide 7: What Success Could Look Like *(45 and 60-min)*
- **Background**: `content-slide-bg`
- **Data source**: Transform E output (grounded in vendor-context.md Real Capabilities, optionally sharpened with a `search_knowledge` case-study proof point)
- **Layout**: Title: *"If we got this right together, 12 months from now…"* coloured `title-on-light`. 3 outcome blocks:
  - Headline in header typeface 22pt, coloured `title-on-light`
  - Supporting detail in body typeface 16pt, coloured `body-on-light`
  - Thin `accent-secondary` left border
- Bottom italic disclaimer coloured `muted`: *"None of this is a promise. It's a starting hypothesis we'd want to test together."*
- **No pricing, contracts, or commercial mechanics on this slide.**

---

#### Slide 8: Proposed Next Steps
- **Background**: `content-slide-bg`
- **Data source**: Transform F output
- **Layout**: Title: *"Where we'd like to go from here"* coloured `title-on-light`. 2–3 numbered steps as editorial list, body text in `body-on-light`, numerals in `accent-primary`. One sentence each, action-oriented.
- First step time-bound (e.g., "A follow-up conversation in the next 10 days").

---

#### Slide 9: Closing Slide
- **Background**: `title-slide-bg`
- **Content**: Centered *"Thank you"* header typeface 44pt coloured `title-on-dark`, then *"[Account Name] × [Vendor Name]"* 24pt coloured `accent-secondary`. Bottom strip: AE name, email, date in `body-on-dark`.
- Clean and quiet. Mirrors title slide.

---

## Step 7: Generate the File

Generate the deck in one build script with the host toolchain ([host-adapters.md](references/host-adapters.md#building-slides)) that:

1. Embeds all pulled data, transformed content, and vendor-context design tokens directly
2. Uses helper functions for repeated patterns (hypothesis blocks, numbered agenda items, outcome blocks)
3. When building with PptxGenJS (Claude's pptx skill), uses factory functions for shadows and styles (a fresh options object for every `addShape`/`addText` call)
4. Adapts to the meeting-length slide set from Step 1
5. Adapts to net-new vs expansion mode from Step 5
6. **Resolve all colour and typeface values at generation time from `vendor-branding.md`** — map each design token (e.g., `title-slide-bg`, `accent-primary`) to its hex value from the branding file's Slide Design Tokens table. Never hardcode colour values in the generation script.
7. **Renders Slide 0 as visible with strong visual distinctness** — do NOT set any hidden-slide flag (for example PptxGenJS `slide.hidden = true`) or inject `show="0"` into the slide XML. Slide 0 is rendered as a normal, visible slide so it survives Google Slides, desktop-assistant PPTX previews, Quick Look, and other viewers that silently drop hidden slides from their editor. The safety net is visual: a full-width `accent-primary` header strip labelled **"AE PREP  ·  DO NOT PRESENT"** (0.4" tall, the only full-width `accent-primary` fill in the whole deck), plus the muted overlay and dense layout specified in the Slide 0 section above. Verify the treatment in Step 8 — do not skip the verification.
8. Handles edge cases (missing data, empty sections, no fresh signals, unauthorized Revenue Signals access, no battlecard/KB match, unscored framework)
9. Writes speaker notes: Slide 2 carries each fresh signal's URL + access date; Slide 0 carries the verified vendor-fact sources (URL + access date) and the list of claims skipped as unverified
10. Adds the demo label to every slide footer when the preflight requires it
11. Saves as `First-Meeting-[AccountName]-[Date].pptx` in the host's output location ([host-adapters.md](references/host-adapters.md#saving-and-delivering-files))

## Step 8: QA

After generating the file:

1. Render every slide to a full-resolution image with the host render path ([host-adapters.md](references/host-adapters.md#rendering-and-inspecting-slides)). Use the full-resolution renders for inspection; a thumbnail or contact-sheet view is only for the Slide 0 thumbnail check below.
2. Open and inspect **every slide individually at full size** for clipping, overlapping text, awkward wrapping, cramped layouts and colour-contrast issues. When rendering through LibreOffice, the branding typeface (Inter) may be substituted, so leave ~10% width slack in text boxes rather than trusting an apparent fit
3. **Placeholder and grounding scan** — no bracketed TODOs, placeholder values, lorem text, "[Account Name]"-style tokens, unconfirmed reference customers, expired cohort or offer claims, or competitor brand names the user didn't ask for, on any slide
4. **Voice audit** — read every slide out loud:
   - Slide 3 assertive-but-invitational, not preachy?
   - Any slide before 6 mention the vendor's product/platform/solution? Strip
   - Any internal diagnostic language (risk, health, score, framework)? Strip
   - Slide 7 making promises rather than hypotheses? Soften
5. **Vendor grounding audit** — cross-check slides 6 and 7:
   - Every capability claim maps to vendor-context.md Real Capabilities
   - No claim strays into Honest Boundaries territory
   - Language aligns with vendor-context.md Voice (no banned phrases)
   - Any claim sourced from `search_knowledge` or `get_battlecard` maps to a real capability / comparison category the same way a vendor-context.md-sourced claim would — supplementary data doesn't get a pass on grounding
6. **Branding audit** — cross-check visual rendering against vendor-branding.md:
   - All colours used match the palette in vendor-branding.md (no accidental hardcoded navy / off-white from template defaults)
   - Background strategy matches the vendor's stated pattern (A bookended or B dark throughout)
   - Accent colours respect accessibility notes (e.g., never using low-contrast colours for body copy)
   - No banned visual patterns from the "What to Avoid" section (gradients, emoji, stat-card grids, etc.)
   - If vendor-branding.md defines a Signature Visual: it appears on Slide 6, uses the specified colours, and does not crowd the capability text
7. **Positioning sharpness audit** — Slide 6 specifically:
   - The positioning headline uses a Signature Concept from vendor-context.md (e.g., "Revenue Engine", "Figure-Eight", "bow-tie") — not a generic "where we help" framing
   - The Why Us band appears at the bottom with 2 differentiators from Transform G
   - Differentiators reference real comparison categories, not vague "we're better" claims — including any sourced from `get_battlecard`
8. **Slide 5 attribution audit** — at least one market observation uses explicit first-person framing ("Our working thesis…", "We believe…", "The way we see it…")
9. Verify mode adaptation:
   - Net-new: slide 6 uses Transform D with real vendor capabilities AND Transform G Why Us band
   - Expansion: slide 6 shows actual impact entries, slide 1 subtitle is "Expanding the Partnership", Transform G is skipped
10. Verify meeting-length adaptation: 30-min deck has 6 customer-facing slides max (plus Slide 0 AE prep — visible but visually distinct)
11. **Slide 0 audit** — Slide 0 exists, appears first in the deck, and is rendered with the right treatment:
    - **Not hidden**: unzip the PPTX and confirm NO slide has the hidden flag. `unzip -p output.pptx ppt/slides/slide1.xml | grep -i 'show='` should return nothing; same for every other slide. If `show="0"` appears anywhere, the skill has regressed to the old hidden-slide approach — strip it. Hidden slides are silently skipped by Google Slides and several previewers, which means the AE can't see the prep material they need.
    - **Visual distinctness**: the `accent-primary` header strip with "AE PREP · DO NOT PRESENT" is present, spans the full slide width, and is at least 0.4" tall. It must be the only full-width `accent-primary` fill in the entire deck — confirm no other slide has one. The muted content overlay is visible (not so subtle that the slide blends into customer-facing slides at thumbnail size). Dense prep-style layout is obvious at a glance.
    - **Voice audit**: raw internal voice is correct here. If Slide 0 reads like a customer slide (softened, assertive-but-invitational), the prep purpose is lost — rebuild using raw `opportunity_discovery_planner` / `opportunity_value_pyramid` / `opportunity_framework_summary` output rather than the Transform B / Transform E output.
    - **Thumbnail sanity check**: open the generated PDF preview or the slide navigator of the PPTX and confirm Slide 0 is visibly, unmistakably different from Slide 1 in thumbnail size. If a reasonable person could scroll past it and miss it, make the header strip taller or the overlay stronger.
12. **Revenue Signals / framework-gaps leakage audit** (new — run this every time, not just when the data was available):
    - Search Slides 1–9 for any score, percentage, confidence value, or severity label that could have come from `get_opportunity_signals` or `opportunity_framework_summary` — none should exist. If Revenue Signals shaped Slide 3's hypothesis wording, confirm only the *wording* changed, not that a score or "first constraint" label got printed.
    - Confirm Slide 0's "What to probe" band (if present) does not have a customer-facing counterpart anywhere else in the deck — it is unique to Slide 0.
    - If `get_opportunity_signals` was denied (access guard), confirm Transform A completed via the Three-Whys-only fallback without erroring the whole skill run, and that Slide 3 reads no differently than it would have without Revenue Signals at all.
13. **Source audit** — every fresh signal on Slide 2 has a visible date and a URL + access date in the speaker notes; every verified vendor fact has its source in Slide 0's notes; every target-account research fact used carries its URL, `published_date` and the digest's `researched_at`, and any digest older than ~90 days was re-verified or left out
13b. **Target-account leakage audit** — search every slide (Slide 0 included) and the speaker notes on Slides 1–9 for tier, fit rating, coverage %, touch history, stage, the thesis text, and committee-role labels ("blocker", "economic buyer", "champion", "influencer"). None may appear
14. Do not declare success until at least one fix-and-verify cycle is complete: fix, re-render the changed slides, re-inspect them
15. **Deliver**: return **one clickable link** to the final PPTX, followed by a short note covering material evidence gaps, any claims skipped as unverified or expired, any fallback taken (no signals, no Revenue Signals access), and the demo label if applied. Remind the AE to skip Slide 0 when presenting

## Tips for Great First Meeting Decks

- **Assertive voice is earned by preparation, not asserted by rhetoric.** The deck earns the right to say "here's what we think" by being visibly grounded in the prospect's specific context AND the vendor's real capabilities.
- **Vendor grounding is the guardrail.** The transforms will happily invent plausible capabilities if not constrained. The vendor-context.md file is the contract that keeps the deck honest — and that contract extends to anything `search_knowledge` or `get_battlecard` contributes, too.
- **Less is more on the hypothesis slide.** Three is the ceiling. One great hypothesis beats three decent ones.
- **The invitation is the whole point.** "Tell us where we're wrong" isn't a throwaway.
- **Mirror their language relentlessly.** Language mirroring is the cheapest credibility signal available.
- **Never pitch before slide 6.** Slides 1–5 are entirely about them.
- **Design for a conversation, not a lecture.** Slides taking >30 seconds to read aloud need cutting.
- **Expansion meetings deserve different energy.** Feel like the next chapter, not a fresh pitch.
- **Slide 0 is the AE's cockpit.** Review it once five minutes before the meeting; glance at it during when an unexpected stakeholder joins or a discovery question dead-ends. If it's not helping during the meeting, the content is wrong — rebuild the raw inputs, don't polish the layout.
- **Access guards are a feature, not a bug.** If `get_opportunity_signals` comes back denied, that's the platform working as intended — degrade quietly and keep moving. Don't treat an authorization boundary as a data-quality problem.
- **Keep vendor-context.md alive — on request.** Stale context means stale decks, so check date-sensitive claims every run and suggest a refresh when they fail. But never rewrite the reference files as a side effect of building a deck; refresh only when the user asks, and save only what they approve.

## Tools Used

CRM tools (from Summit53 or equivalent revenue platform):

- `get_opportunity` — core deal and account details
- `search_opportunities` — related deals at the account
- `opportunity_three_whys` — strategic narrative (Why Change / Why Now / Why Us)
- `opportunity_discovery_planner` — discovery agenda, key questions, CTA
- `opportunity_value_pyramid` — stakeholder-tiered value messaging
- `opportunity_stakeholder_intelligence` — stakeholder profiles, coverage gaps
- `get_opportunity_notes_summary` — AI-generated narrative of prior interactions
- `get_opportunity_notes` — raw notes for transform freshness
- `get_opportunity_activities` — prior touchpoint context
- `list_account_contracts` — expansion mode detection
- `get_value_impact_card` — evidence narrative for expansion mode
- `list_impact_entries` — delivered outcomes for expansion mode
- `external_account_research` — prospect's own website language for mirroring (async — queue early in Step 2's parallel batch)
- `get_opportunity_signals` — Revenue Signal Layer: the deal's first constraint, ranked signals, and win-probability movement; sharpens Slide 3's hypothesis language. Access-guarded to leader/admin or the owning rep — degrade gracefully to Three-Whys-only hypotheses if denied. Scores/confidence/severity never appear on customer-facing slides.
- `get_battlecard` — best-matching competitive battlecard by competitor name (up to 3 candidates); grounds Transform G's differentiators. Skip gracefully if no match exists.
- `search_knowledge` — org Knowledge Base search across positioning, case studies, product, and battlecard assets; supplements thin/placeholder Proof Points for Transforms D and E. Skip gracefully if no relevant match exists. Supplements the vendor-grounding check — never bypasses it.
- `opportunity_framework_summary` — MEDDPIC/BANT/SPICED/THREE_WHYS framework scores and gaps; feeds Slide 0's "What to probe" band only. Never appears on customer-facing slides — omit the band if unscored.
- `search_target_accounts`, `get_target_account`, `get_stakeholder_research_brief` — optional, Outreach plan: thesis, buying committee, coverage gaps and dated external research for a confirmed matching target account (Step 2, item 9). Read-only; internal fields shape content and never appear on slides.

Gate and discovery:

- `current_context` — tenant gate; always first
- `list_available_tools` — confirms which optional tools (Revenue Signals, battlecards, Knowledge Base, account research) this connector exposes
- `get_job` — polls `external_account_research` if it returns a processing envelope

External tools (whatever web search and web fetch tools the session provides):

- Web search — fresh-signal research in Step 3; vendor positioning lookup and date-sensitive claim checks in Step 0
- Web fetch — vendor context setup and currency checks in Step 0; reading the full page behind a search result before citing it

Reference files:

- [references/vendor-context.md](references/vendor-context.md) — vendor's real capabilities, offer, voice, positioning, market POV
- [references/vendor-branding.md](references/vendor-branding.md) — vendor's visual design system for deck generation (colours, typography, background strategy, slide tokens)
- [references/connector-preflight.md](references/connector-preflight.md) — shared tenant, schema, fixture, read-only, missing-evidence and delivery contract

There are no blank template files; the guided setup in Step 0 describes the fields inline.

## Guardrails

- Read-only against Summit53: no writes, notes or `refresh: true`; never create, update or convert a target account, and never submit, accept or dismiss stakeholder suggestions. The only files this skill may write are the deck itself and — only on an explicit refresh or first-run setup the user approved — the two vendor reference files.
- Do not invent capabilities, proof points, customer outcomes, competitor claims, pricing or implementation commitments. No bracketed TODOs, placeholder proof points, unconfirmed reference customers or expired cohort claims.
- Verify date-sensitive vendor claims against a current source (vendor context last reviewed 2026-04-21); skip what cannot be verified.
- Record a URL and access date for every web fact; never present a web snippet as CRM evidence or a hypothesis as fact.
- Do not name competitors on customer slides unless the user explicitly asks and the evidence is current and relevant.
- Never expose framework scores, risk or health labels, signal confidence, private notes, AE-only objections, or access-denied detail on Slides 1–9.
- Never print target-account tier, fit rating, coverage %, touch history or committee-role labels on any slide, Slide 0 included.
- Do not hide Slide 0 with a hidden-slide flag or `show="0"`; keep the visible visual forcing function.

## Final verification checklist

- [ ] Preflight checklist complete; `current_context` ran first; returned IDs match `scoped_org_id`
- [ ] Exactly one opportunity resolved; attendees, meeting length and objective known
- [ ] Both vendor reference files read; date-sensitive claims verified or skipped
- [ ] Transform Quality Check passed (grounding, voice, no scores, no placeholders, no competitor brands)
- [ ] Slide 0 present, visible, unmistakably labelled; no `show="0"` anywhere
- [ ] Fresh signals dated on-slide with URL + access date in notes
- [ ] Target-account context used only after a confirmed match (or noted unavailable); no internal target-account field on any slide; nothing written
- [ ] Fixture data excluded, or the demo label is on every slide
- [ ] Every slide rendered and inspected at full size; one link returned with the gaps note
- [ ] Reference files unchanged unless the user requested and approved a refresh

## Design Rationale Notes

A few decisions worth making explicit for future maintainers:

**Why a separate vendor-context.md file rather than baking vendor details into SKILL.md?**
The skill is designed to be vendor-agnostic so it can ship to any vendor using Summit53 (or a similar revenue platform) as their CRM. Each vendor installation gets its own vendor-context.md. Baking specifics into SKILL.md would mean forking the skill per deployment — a maintenance nightmare.

**Why a guided setup rather than a pure template file?**
Asking users to fill a blank template has low conversion. Guided setup combining web research (what's already published) with focused questions (what the web can't answer) gets to a usable file in ~5 minutes with less cognitive load, and catches honest-boundaries information that self-written templates often skip.

**Why hybrid LLM (transform) rather than raw pre-computed narratives?**
CRM-generated strategic narratives are tuned for internal strategic use and typically run on lighter-weight LLMs. The deck needs assertive-but-invitational customer-facing voice, stakeholder-filtered messaging, and vendor-grounded capability claims — a different job. Transforming with the host model preserves the strategic investment in the in-product prompts while upgrading voice, tone, and grounding for customer consumption.

**Why stakeholder filtering on the Value Pyramid?**
Showing the Executive layer to a technical champion kills the meeting. Filtering by attendee tier is not optional.

**Why hide all diagnostic scores?**
One leaked slide showing "Economic Buyer: 25%" kills the relationship. No legitimate customer-facing use of internal qualification or health scoring.

**Why "assertive but invitational" rather than "curious and tentative"?**
First meetings benefit from the AE showing they've done the work and have a point of view, provided they explicitly invite challenge. Matches a credible strategic partner, not a generic vendor.

**Why is vendor grounding called out as a hard guardrail in Transforms C, D, E, and F?**
Without it, the transform step will confidently invent plausible-sounding capabilities to match the customer's Value Pyramid — capabilities the vendor doesn't actually have. A single over-claim caught in a first meeting is a deal-ender.

**Why are vendor context and vendor branding in separate files rather than one?**
Positioning evolves on a different cadence than brand palette. A vendor may ship a new feature monthly (context update) but change their brand system once every few years (branding update). Separating them means either can be refreshed without disturbing the other. It also lets vendors with detailed existing brand guides extract just the deck-relevant subset into `vendor-branding.md` without conflating it with positioning work.

**Why an in-deck prep slide — and why visible rather than hidden?**
The first question (in-deck vs separate prep doc) has two answers. First, portability — one PPTX the AE opens on a laptop / phone / in a pre-meeting huddle beats a deck-plus-separate-brief workflow every time. Second, context proximity — the prep notes sit next to the customer slides they drive, so if the AE edits a hypothesis on Slide 3 they can eyeball whether the underlying question on Slide 0 still matches.

The second question (visible vs hidden) got answered the hard way. The original design used PPTX's native hidden-slide flag (`show="0"`), reasoning that PowerPoint would skip it in Slide Show mode while keeping it visible in the editor. That assumption holds in PowerPoint desktop; it breaks in Google Slides (which silently drops hidden slides from the editor navigator unless the user deliberately unhides them), in desktop-assistant PPTX previews, in some mobile PowerPoint clients, and in Quick Look. For an AE whose workflow lives in Google Slides, the hidden flag meant the prep material was invisible — which is the worst of both worlds.

So Slide 0 is now rendered as a fully visible slide, and the "don't present this" guardrail is moved from an XML attribute to a **visual forcing function**: a 0.4" `accent-primary` header strip labelled "AE PREP · DO NOT PRESENT", enforced as the only full-width accent-primary fill in the deck so it's instantly spottable in thumbnail views. The AE manually skips the slide when entering presentation mode (one keystroke in any viewer). Trade-off accepted: slightly more AE discipline required, vastly better cross-client compatibility. If vendors using a PowerPoint-only workflow want the hidden-slide safety back, it can become a per-vendor preference in `vendor-branding.md` rather than a skill default — but the default is visible.

**Why does Slide 0 use raw internal voice and bypass Step 4 transforms?**
The entire point of Slide 0 is to give the AE the pre-transform material — the blunt questions, the full Value Pyramid across all tiers, the unvarnished objection list, and now the unvarnished framework gaps. Running it through the transforms would make it match the rest of the deck in tone, which defeats the purpose (the AE already has the transformed versions on Slides 3, 4, 5, 6, 7, and 8). It's deliberately the one place in the skill where internal voice wins.

**Why show all four Value Pyramid tiers on Slide 0 when Slide 7 is stakeholder-filtered?**
First meetings routinely have surprise attendees. A VP Sales meeting becomes a joint VP Sales + CFO meeting the day-of. The filter on Slide 7 is correct for customer viewing (showing a CFO the Technical-tier message kills the meeting), but the AE still needs fast access to the right-tier message in the moment. Slide 0 is the fallback: no frantic note-fumbling when the room composition changes, just a glance at the cheat sheet.

**Why is `get_opportunity_signals` access-guarded, and why degrade silently rather than surfacing the denial?**
The tool is deliberately restricted to the deal's leader/admin or owning rep because the Revenue Signal Layer's underlying evidence can include sensitive judgment calls about a rep's execution, not just the deal itself. An AE prepping someone else's deck (e.g., covering for a colleague) may legitimately not have access. Surfacing "you're not authorized" as an error would make the skill feel broken for a scenario that's actually normal — so the skill treats a denial exactly like an empty data pull: fall back to the Three-Whys-only path and keep moving. The prospect-facing slide looks identical either way; only the AE-side sharpness differs.

**Why do `get_battlecard` and `search_knowledge` results still have to clear the vendor-grounding check?**
Both pull from the org Knowledge Base, which is broader and less tightly curated than `vendor-context.md` — a battlecard might describe a roadmap item as if shipped, or a case study might reference a bespoke integration that isn't part of the standard offer. Treating KB content as automatically trustworthy would reopen exactly the over-claiming risk `vendor-context.md` exists to close. So these tools are additive evidence: they can sharpen a claim that's already grounded, but they can't be the sole grounding for a claim.

**Why does the framework-gaps band stay on Slide 0 even though other diagnostic-adjacent data already lives there?**
Slide 0 already carries the discovery questions and objection list, so it might seem like framework gaps could just merge into an existing band. They get a dedicated band instead because MEDDPIC/BANT gap data is qualitatively different — it is precisely the category of content the rest of this skill has the strongest, most repeated rule against ("no risk scores, framework percentages... even as subtle labels"). Giving it a clearly labelled, clearly bounded band on Slide 0 — rather than blending it into Band 4's watchouts — makes the AE-only/customer-never boundary visually explicit, and makes it trivial to audit in Step 8 (one band to check, not a data type scattered across multiple bands).

# Vendor Branding — Summit53

Visual design tokens the first-meeting-deck skill uses when generating decks for Summit53. Read by Step 6 (Build the Deck) and Step 7 (Generate the File) of SKILL.md. Adapted from Summit53's full brand guide; only the parts relevant to PPTX deck generation are included here.

---

## Colour Palette

### Brand Colours

- **Primary (terra cotta)**: `#FF6B35` — the Summit53 signature. Used for titles, primary accents, brand moments, bullet markers, thin left borders on editorial blocks.
- **Secondary (teal)**: `#06B6D4` — complementary accent for dividers, small caps labels, secondary emphasis.
- **Primary muted**: `#C2410C` — for larger fills where saturated orange would dominate.
- **Secondary muted**: `#0E7490` — muted teal counterpart.

### Neutral Palette

- **Dark background**: `#1F2937` — primary dark fill (title and close slides).
- **Darker background**: `#111827` — deeper fill for emphasised blocks on dark surfaces.
- **Light background**: `#FFFFFF` — content slide background.
- **Light background alt**: `#F3F4F6` — softer alternative for secondary card layers on light slides.
- **Text on dark**: `#F9FAFB` — primary text against dark backgrounds.
- **Text on light**: `#111827` — primary text against light backgrounds.
- **Muted text**: `#6B7280` — disclaimers, captions, source URLs, italic support text.
- **Divider/border**: `#E5E7EB` — subtle horizontal lines between sections.

---

## Slide Design Tokens

These are the tokens SKILL.md Step 6 references by name. Resolve each to its hex value at generation time.

| Token | Hex | Usage |
|---|---|---|
| `title-slide-bg` | `#1F2937` | Title and close slide backgrounds |
| `content-slide-bg` | `#FFFFFF` | All content slide backgrounds |
| `title-on-dark` | `#F9FAFB` | Main title text on dark backgrounds |
| `title-on-light` | `#111827` | Main title text on light backgrounds |
| `body-on-dark` | `#F9FAFB` | Body copy on dark backgrounds |
| `body-on-light` | `#111827` | Body copy on light backgrounds |
| `accent-primary` | `#FF6B35` | Primary accents (numerals, left borders, small caps labels on Slide 0 band labels) |
| `accent-secondary` | `#06B6D4` | Secondary accents (hypothesis labels, outcome block left borders, Why Us band label) |
| `muted` | `#6B7280` | Disclaimers, captions, italic qualifiers, prep-slide support text |
| `divider` | `#E5E7EB` | Thin horizontal dividers between slide bands |

---

## Background Strategy

**Pattern A — Bookended (selected)**: dark title slide → light content slides (Slides 2–8) → dark close slide. This is the pattern the first-meeting deck uses.

Rationale: Summit53's voice is direct and editorial; customer-facing slides read as a thoughtful memo, not a pitch deck. Light content slides give the prose room to breathe. Dark bookends carry the brand moment at open and close.

The AE prep slide (Slide 0) uses `content-slide-bg` with a light `muted` overlay (~10% opacity) plus an `accent-primary` header strip so it is immediately visually distinct from customer-facing slides during a casual scroll-through.

---

## Typography

**Header typeface**: Inter (or equivalent grotesque sans — Helvetica Neue acceptable fallback). Used for slide titles and large accent text at 28–44pt depending on slide.

**Body typeface**: Inter (same face, lighter weights). Used for body copy at 16–20pt on customer-facing slides, 10–12pt on the AE prep slide.

**Accent typeface**: Same family as header/body. No display/script fonts. No secondary serif.

**Weights in use**:
- Header: 600 (semibold) for slide titles, 700 (bold) for occasional emphasis
- Body: 400 (regular) default, 500 (medium) for inline emphasis, 600 (semibold) for editorial block headlines
- Small caps labels: 600 (semibold), tracking +50

Avoid italic except for (a) the invitation line on Slide 3, (b) the disclaimer on Slide 7, (c) the `muted` italic support text on Slide 0, (d) the transition line on Slide 5.

---

## Signature Visual

Summit53 has one deck-relevant structural diagram: **the Figure-Eight revenue loop** (bow-tie drawn as a continuous loop). It is the defining visualisation of the positioning and maps to Signature Concepts in `vendor-context.md`.

**Placement**: Slide 6 only, in Band 1 (positioning anchor). Centred beneath the positioning headline. Roughly 40% of slide width, centred or right-aligned per slide composition.

**Rendering**:
- Two overlapping circles forming a lemniscate / infinity shape
- Left loop: acquisition (outreach → qualification → deal → commit)
- Right loop: delivery + expansion (impact → expansion → renewal)
- Crossover point: labelled *"Commit / Value"* — the pinch where the motion crosses
- Stroke only, no fill. Stroke weight medium (3–4pt equivalent).
- Left loop in `accent-primary` (`#FF6B35`). Right loop in `accent-secondary` (`#06B6D4`). Crossover marker in `title-on-light` with a small `accent-primary` dot.
- Stage labels in `muted` 9–10pt around the loops — not more than 6 labels total or it becomes illegible at deck scale.

**When to skip**: if Slide 6 content density makes the visual feel crammed, omit it. A text-only Slide 6 with a strong positioning headline is perfectly valid per SKILL.md guidance. Better absent than cramped.

---

## Visual Tone

- **Editorial, not dashboard.** Prose blocks with thin accent borders, not stat cards.
- **Flat, not glossy.** No gradients, no drop shadows beyond subtle slide-level elevation.
- **Whitespace-rich.** Margins 0.75" minimum on content slides; 0.5" on the AE prep slide (denser is acceptable there).
- **One accent element per slide max** — a thin `accent-primary` left border, a `divider` horizontal line, or a small `accent-secondary` label. Never all three.
- **No iconography beyond the signature visual.** No stock icons, no Lucide glyphs, no emoji.

---

## What to Avoid

Direct translations into "don't do this" rules for the generation script:

- No gradient fills. Brand colours are used flat.
- No drop shadows, beveled edges, or glow effects.
- No emoji. Anywhere. Ever.
- No stat-card grids or KPI-dashboard-style layouts — they read internal.
- Brand colours are for headers, thin borders, numerals, and small-caps labels. Never for data fills or full background blocks on content slides.
- No decorative shapes (stars, arrows, chevrons) beyond the Signature Visual.
- No multi-column bullet grids. Prose blocks stacked vertically.
- No template-default colour leakage (PowerPoint's default navy `#1F3864`, Office green `#70AD47`, or any of the out-of-the-box accent ramp).

---

## Accessibility Notes

- WCAG AA contrast (4.5:1 minimum) on all body copy. `#111827` on `#FFFFFF` clears this comfortably; `#F9FAFB` on `#1F2937` also clears.
- Accent primary `#FF6B35` has borderline contrast on white for body copy — use it for large headlines, short labels, and decorative elements, not for long body text.
- Accent secondary `#06B6D4` is acceptable for small-caps labels and thin borders but should not carry body copy on white.
- Never rely on colour alone to convey meaning (not a concern for first-meeting decks, which carry no data vis by design — stated here for consistency).

---

## Maintenance

**Last reviewed**: 2026-04-21
**Reviewed by**: Summit53

Update when the palette changes, a new typography decision is made, or the Signature Visual evolves. Quarterly review is appropriate.

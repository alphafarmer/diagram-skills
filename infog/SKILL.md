---
name: infog
description: |
  /infog — reference-architecture infographic pages. Produces a one-page, multi-panel HTML
  infographic: icon-badge nodes, real flows, visual metaphors (swimlanes, funnel+prism machines,
  metro lines, dashboards, runways, territory maps) — NEVER rows of text boxes. Dense detail moves
  into circled-number keys BELOW each diagram. Validated-then-drawn-then-adversarially-reviewed
  pipeline built in.
  USE WHEN: asked for an infographic, visual overview, programme map, architecture picture,
  "show the process visually", one-pager of a research/product area, or /infog <topic>.
  DO NOT USE FOR: single charts, prose reports, slide decks, or evidence-report pages (/vispage).
metadata:
  type: authoring-method
---

# /infog — the reference-architecture infographic method

The generator scaffold is in this skill dir: `template.py` — copy it, do not reinvent the helpers.

## The binding pipeline (all three stages, every time)

1. **VALIDATE FIRST.** Spawn a reader subagent over the source material (pages, repos, logs) that
   returns a structured fact sheet with exact numbers + sources, and explicitly corrects YOUR
   numbers where wrong. Draw nothing before it lands. The page's truth claim is this pass.
2. **DRAW from the fact sheet only.** Every figure on the page must exist in the sheet.
3. **ADVERSARIAL REVIEW.** Spawn a reviewer subagent on the built file: geometry (coordinates
   parsed, collisions estimated at ~5.8px/char @11px, ~6.6 @12–13px, anchor-aware), key
   integrity (every circled number on-canvas has a key item and vice versa), icon-ref integrity
   (every <use href> resolves in the symbol sheet), accuracy spot-check vs the fact sheet, and
   the brief test: "does each panel read as a diagram, not box rows?" Apply the fix list, then
   publish. Expect one REWORK round; that is the system working.

## The visual grammar (what makes it "not boxes")

- **Icon badges, not labeled rectangles**: a colored circle + white line-art glyph + label below.
  template.py ships a 17-glyph symbol sheet (terminal, shield, scroll, spark, db, gauge, prism,
  funnel, valve, lens, lock, switch, flask, brain, tag, star…) drawn once in a hidden
  `<svg><defs><symbol>` sheet, used everywhere via `<use href="#i-x">`. Add glyphs as symbols,
  24×24 viewBox, stroke-width 2, currentColor.
- **Panel archetypes** — pick per content shape, never default to a grid of boxes:
  * **Swimlane architecture** (a system): 2–4 horizontal lane bands + side planes, icon nodes,
    colored flows crossing lanes. THE hero panel for any "how it works".
  * **Cycle machine** (a loop/process): ramp → gauge → funnel → prism/splitter → valve → shield,
    with a dashed return loop. Give physical metaphors to stages.
  * **Metro line** (a timeline/sequence of gates): one thick line, ring stations with status
    glyphs (✓ ✗ ! 🔒 ~) in brand colors, labels alternating above/below, a banner strip beneath.
  * **Dashboard** (measurements): donut (real arcs, not pie emoji), slope/dumbbell chart for
    before→after, weight bars. Each with its headline number IN the graphic.
  * **Runway/road** (roadmap): thick road + dashed centerline, milestone lollipops, red
    toll-gate slabs carrying the pre-registered decision conditions.
  * **Territory map** (competitive field): 2×2 quadrant with party icon badges placed on the
    axes + callout cards on the right.
- **Text discipline — the load-bearing rule**: on-canvas text is ONLY label + one number + a
  circled key digit (①②③). ALL sentences go in `<ol class="keys">` under the panel, each item
  led by a colored number chip matching the on-canvas digit. This is what stops "squished boxes".
- **Layout discipline**: viewBox 1160 wide; `.ig{overflow-x:auto}` + `svg{min-width:1160px}` so
  small viewports scroll instead of shrinking below legibility; label columns via the Col
  y-cursor helper (collisions become impossible); unique marker ids per svg (defs() helper).

## Palette (strong, never faded)

ink #141821 · blue #1D4ED8 (live/ours) · green #0F7B33 (proven/adopt) · amber #B45309
(cost/trade-off) · red #B91C1C (measured problem/gate) · purple #6D28D9 (injection/steering) ·
teal #0E7490 (machinery) · gold #A16207 (metering/meta) · gray #6B7280 (parked/boundary/external).
Saturated fills, #141821 strokes, white glyphs/text on fills. Close with a `.legendrow` naming
EVERY color used. Light tint bands (#EFF6FF-class) are allowed ONLY as lane backgrounds.

## Honesty rules (inherited, binding)

Numbers verbatim from the fact sheet with their boundaries; failures and kills drawn with the
same prominence as wins; unmeasured = ABSENT, never estimated silently; distinct
similar-looking numbers explicitly kept apart (the "three 96%s" lesson); provenance tag
("claimed", "3-day mean") wherever a figure is not a hard measurement.

## Build mechanics

1. Copy `template.py` into a scratch folder; fill the fact-sheet constants; pick archetypes;
   generate `<name>.html`.
2. If your publishing pipeline auto-stamps pages, do NOT write your own "Last updated:" line —
   exactly one stamp per page.
3. Publish through your own static-page pipeline and verify the served bytes match the local file
   (sha256).
4. Link the page from the index or journal it belongs to.

## Layout laws learned from review round 2 (binding — these were the 22 fixes)
- **Flows BEFORE nodes/labels** in emission order, so text always paints on top; dogleg any
  connector that would share an x/y line with a label block anyway.
- **Measure every long string** against its container: chars × 5.8px (11px font) / 6.6px (12–13px),
  half each side when text-anchor=middle. Split to tspans/lines rather than trust it.
- **Every circled number on-canvas must have a key item below, and vice versa** — check both
  directions per panel; keydot() markers go ON the element they annotate.
- **Escape &amp;lt; in SVG text** (raw < breaks XML extraction).
- **No emoji where a symbol exists** (🔒 → #i-lock) — emoji render in color fonts and clash.
- **No sub-labels straddling lane borders**; size lanes to hold both label lines.
- **Container width**: .jp max-width must exceed svg min-width + all padding (1264 for 1160).
- **Kill degenerate/duplicate elements** before review (zero-length paths, leftover transforms).
- **Data-ink honesty**: a bar drawn bigger than its value for visibility gets a leader-line
  annotation instead.

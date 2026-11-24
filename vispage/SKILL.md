---
name: vispage
description: |
  /vispage — evidence-report HTML pages built from data-driven SVG figures: Manrope on a cool-grey
  page, white figure cards, big KPI tiles, ranked bars, stacked splits, pipelines, swimlanes, phase
  roadmaps, verdict boards and status matrices. Every section is led by a figure with a caption that
  says what to conclude. It is a Python component library (15 figure types), a page shell, and a
  render checker that FAILS on overflowing or colliding labels. The checker is meta-tested.
  USE WHEN: writing a findings / review / audit / programme / recommendation page that has numbers or
  a process in it, or when asked for "lots of visuals" or /vispage.
  DO NOT USE FOR: a one-page architecture infographic with icon badges and metro lines (/infog), a
  single chart, app-like UI screens, or slide decks.
metadata:
  type: authoring-method
---

# /vispage — visual evidence pages

## The files
| File | What it is |
|---|---|
| `vispage.py` | The palette tokens, 15 figure functions, and `page()` / `fig()` / `details()` / `chip()` |
| `example.py` | Every component with demo data. **Copy it as your starting point.** |
| `render_check.py` | Headless-Chromium check plus screenshots. `--selftest` proves it catches seeded faults. |

## The method: how the page reads
1. **Nav line.** Backlinks (← related pages) followed by `Last updated:` from `date -u`, never estimated. `page()` does this for you.
2. **H1 and subtitle.** The subtitle names the sources and the review status, plus a chip (`draft`, `settled`, …).
3. **"In one line" box.** The verdict, in a sentence the reader could repeat.
4. **Numbered sections (`1 · What happened`, `2 · Why`, `3 · The fix` …).** Lead each section with a figure. Prose is optional; the figure carries the point.
5. **Every figure = SVG + caption.** The caption says what to conclude, then the source, window and caveat. Put a `note_bar` inside the figure only for the one takeaway.
6. **A "Decisions needed" card** near the end: a numbered list, one decision per line.
7. **Details, collapsed.** Specs, method, caveats and the evidence path go in `details()` blocks.

Aim for one figure per claim. Write for the reader first: plain sentences, a unit and window on every number, and no internal jargon at the top.

## The components (all take plain data and return an SVG string, 920 wide)
| Function | Use it for |
|---|---|
| `kpi_tiles(title, [(value,label,tone)], notes)` | The headline: 3–5 big numbers plus takeaway strips |
| `hbars(title, rows, inner=…, legend_items, note)` | A ranked quantity. The optional dark inner overlay shows "the part that was X". |
| `split_bars(title, [(label,pct,note)])` | Per-actor split, e.g. fix vs forward time |
| `stacked(title, rows, segments, note)` | 100% shares compared across two bases |
| `before_after(title, [(label,before,after/None,note)])` | Would the fix have helped? `None` shows a "needs other fix" chip. |
| `pipeline(title, stages, below, badges, above_link, note)` | Flow with entry points (below) and a late-discovery arc (above) |
| `swimlanes(title, columns, lanes, note)` | A process by size or role × step. `None` = step skipped. |
| `phases(title, items, notes)` | Roadmap with gate states; dashed = gated / not started |
| `cycle(title, boxes, loop_label, chips, notes)` | A lifecycle with a feedback loop, plus owner chips |
| `two_columns(title, left, right)` | Keep vs delete, added vs removed |
| `board(title, columns, note)` | Verdict board: KILL / SLIM / KEEP |
| `ranked_rows(title, rows, …)` | Keyed list with a bar and a status chip (rules, risks, steers) |
| `ladder(title, steps, note)` | Escalation tiers |
| `status_matrix(title, rows)` | Capability / status table drawn as a figure |
| `targets(title, rows, note)` | Metric / now / target, with mini bars and a falsifier |

**Tones:** `green` (good/done/keep), `amber` (partial/in flight/warning), `red` (bad/missing/gated-hard), `indigo` (neutral emphasis/planned), `blue` (info), `ink` (structure), `grey` (skipped/trivial). Never invent new colours.

## Hard rules
- **Every number comes from an evidence file.** Keep the evidence next to the build script and name its path in the Method details. Estimates are labelled as estimates in the caption.
- **Build pages from a script** (`build_page.py`), never by hand-editing the HTML, so the next edit is a data change.
- **`render_check.py page.html shots/` must PASS**, and you must **look at the screenshots** before publishing. The checker catches geometry, not taste. When a label overflows, shorten the words; don't shrink the font below 10.
- **Labels are short.** A note bar holds about 130 characters, and a swimlane cell about 18.
- **No coloured left-edge stripes on cards.** Use a full 1 px border and a tint. The CSS here already complies.
- **Exactly one `Last updated:` stamp**, and backlinks to the related pages.

## Workflow
```bash
pip install playwright && playwright install chromium     # once, for render_check.py
cp ~/.claude/skills/vispage/example.py ./build_page.py      # swap in your data
python3 build_page.py page.html
python3 ~/.claude/skills/vispage/render_check.py page.html shots
# Read shots/figNN.png, fix, repeat until PASS and it looks right
```
`example.py` adds its own directory to `sys.path`; in a copied `build_page.py` use
`sys.path.insert(0, os.path.expanduser("~/.claude/skills/vispage"))` before `from vispage import *`.
The page is a single self-contained HTML file (fonts load from Google Fonts); publish it however you publish static pages.

## Self-check before calling it done
- The selftest passes: `render_check.py --selftest`.
- `render_check.py` PASSES on the page.
- You looked at the screenshots.
- Every figure has a caption with a source.
- The Decisions card exists if the page asks the reader for anything.

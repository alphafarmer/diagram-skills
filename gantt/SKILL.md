---
name: gantt
description: |
  /gantt — planned-against-actual schedule charts as SVG: the plan as a dashed band, what happened as a
  solid bar under it, the overrun in red, late starts hatched, gates as diamonds, milestones as flags,
  a today line, row groups, and a stacked layout for phones. Same palette as /vispage, so a chart drops
  straight into a vispage page; also builds a standalone page.
  USE WHEN: a page needs to show a schedule, a plan against progress, slips, or "where are we on the
  timeline" — phases, sprints, rollouts, experiment steps.
  DO NOT USE FOR: a roadmap with no dates (vispage phases()), resource levelling or dependency
  critical-path planning (this draws, it doesn't schedule).
metadata:
  type: authoring-method
---

# /gantt — planned against actual

## The files
| File | What it is |
|---|---|
| `gantt.py` | `gantt()` (desktop, 920 wide), `gantt_phone()` (stacked, 360 wide), `gantt_block()` (both, switched by CSS, with Expand all / Roll up all buttons), plus `page()` / `fig()` for a standalone page |
| `example.py` | Two demo schedules with made-up data. **Copy it as your starting point.** |

The layout checker is `../vispage/render_check.py` (install vispage alongside).

## The data
```python
rows = [
  {"group": "Build"},                                                   # a group heading
  {"label": "Search API", "note": "back end",                           # one row; note is optional
   "plan": ("2026-03-05", "2026-03-12"),                                # planned start, end
   "actual": ("2026-03-05", "2026-03-10"),                              # (start, None) = still in work; None = not started
   "gates": [("2026-03-12", "go / no-go")], "flags": [("2026-03-10", "on staging")]},
]
gantt_block("Website relaunch", rows, "2026-03-01", "2026-03-21", today="2026-03-12",
            note=("Read:", "one sentence on what to conclude", "red"))
```
Dates are ISO (`2026-03-05` or `2026-03-05T12:00`). Each row's status is worded for you: "done · on plan",
"done · 2 d late", "in work · +1 d over plan", "not started · 3 d past start".

## How to read it (put this in your caption)
- Dashed band = the plan. Solid bar = what happened: blue in work, green done, red past the planned end.
- Hatched amber = should have started by today and hasn't.
- Diamond = a gate; flag = a milestone; blue line = today.
- Each group is a band you can click to roll up or expand. Its roll-up bar shows the whole group's plan and
  its actual so far (red if any item is behind), so a rolled-up chart still tells the story.
- The output is HTML, not one SVG: a header, one `<details>` per group, and a footer, all on the same x scale.
  Roll-up needs no JavaScript; only the two buttons use a one-line onclick.

## Rules
- **Every date comes from a source** (tracker, git log, run records). Name it in the caption. A plan
  that was re-baselined keeps its ORIGINAL dates; say so if you show the new ones.
- **`today` comes from the clock** on a live page, not typed in. Pass the date the data was read.
- **Keep labels short:** about 26 characters for a row name, 30 for its note.
- **Order rows the way the reader thinks** (by phase, or worst-slip first); the chart does not sort.
- The axis thins itself: daily, every 2 days, weekly, fortnightly, then monthly.
- **Run the checker and look at the screenshots.** It fails on overflowing or colliding labels.

## Workflow
```bash
cp ~/.claude/skills/gantt/example.py ./build_page.py      # swap in your rows
python3 build_page.py page.html
python3 ~/.claude/skills/vispage/render_check.py page.html shots
```
Inside a vispage page, wrap it like any figure: `fig(gantt_block(...), "caption")`, and append `gantt.CSS`
(the `.gt*` rules) to the page CSS.

#!/usr/bin/env python3
"""Two demo schedules with made-up data. Doubles as the skill's smoke test:
   python3 example.py /path/out.html && python3 ../vispage/render_check.py /path/out.html /path/shots
Copy this file as the starting point; replace the demo rows with your plan and your dates."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gantt import gantt_block, fig, page

# A three-week web relaunch, read on 12 March: some rows on plan, some late, one not started.
RELAUNCH = [
    {"group": "Design"},
    {"label": "Research interviews", "note": "UX", "plan": ("2026-03-02", "2026-03-04"), "actual": ("2026-03-02", "2026-03-04")},
    {"label": "Wireframes", "note": "UX", "plan": ("2026-03-04", "2026-03-06"), "actual": ("2026-03-04", "2026-03-08"),
     "gates": [("2026-03-08", "design sign-off")]},
    {"group": "Build"},
    {"label": "Page templates", "note": "front end", "plan": ("2026-03-06", "2026-03-11"), "actual": ("2026-03-08", None)},
    {"label": "Search API", "note": "back end", "plan": ("2026-03-05", "2026-03-12"), "actual": ("2026-03-05", "2026-03-10"),
     "flags": [("2026-03-10", "API on staging")]},
    {"label": "Content migration", "note": "editors", "plan": ("2026-03-09", "2026-03-16"), "actual": None},
    {"group": "Launch"},
    {"label": "Load test", "note": "ops", "plan": ("2026-03-16", "2026-03-18"), "actual": None, "gates": [("2026-03-18", "go / no-go")]},
    {"label": "Go live", "note": "everyone", "plan": ("2026-03-19", "2026-03-20"), "actual": None, "flags": [("2026-03-20", "launch")]},
]

# A two-quarter programme: the axis thins to weekly or fortnightly ticks on its own.
PROGRAMME = [
    {"group": "Phase 1 · prove it"},
    {"label": "Discovery", "plan": ("2026-01-05", "2026-01-30"), "actual": ("2026-01-05", "2026-02-06")},
    {"label": "Pilot with 3 teams", "plan": ("2026-02-02", "2026-03-27"), "actual": ("2026-02-09", None),
     "gates": [("2026-03-27", "pilot review")]},
    {"group": "Phase 2 · scale it"},
    {"label": "Rollout", "plan": ("2026-04-01", "2026-06-26"), "actual": None, "flags": [("2026-06-26", "all teams")]},
]

S = [("1 · A short project, by day", [fig(gantt_block("Website relaunch", RELAUNCH, "2026-03-01", "2026-03-21", today="2026-03-12",
        note=("Read:", "templates are 1 day over and still open; content migration should have started on 9 March.", "red")),
        "Demo data. Each row: dashed band = plan, solid bar = what happened. Red = the part past the planned end.")]),
     ("2 · A longer programme, ticks thin out", [fig(gantt_block("Programme roadmap", PROGRAMME, "2026-01-01", "2026-06-30", today="2026-03-12"),
        "Demo data. Same function over six months. Click a group band to roll it up; its bar shows the whole group.")])]
html = page("gantt examples", "Made-up demo data for the gantt skill.", "plan as a dashed band, actual as a solid bar, slips in red, today as a line.",
            S, nav_links=[("diagram-skills", "#")])
out = sys.argv[1] if len(sys.argv) > 1 else "gantt-examples.html"
open(out, "w").write(html); print("wrote", out)

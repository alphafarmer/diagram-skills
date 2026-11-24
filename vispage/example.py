#!/usr/bin/env python3
"""Every vispage component on one page. Doubles as the skill's smoke test:
   python3 example.py /path/out.html && python3 render_check.py /path/out.html /path/shots
Copy this file as the starting point for a new page; replace the demo data with evidence."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vispage import *

S = []
S.append(("1 · Headline", [fig(kpi_tiles("The week in five numbers",
    [("82", "episodes", "red"), ("~176", "rounds", "amber"), ("66%", "omission", "indigo"), ("25–60%", "of the week", "ink"), ("1 in 13", "first-time ship", "blue")],
    [("Headline:", "one plain sentence a reader can repeat.", "green")]), "Caption: what to conclude, plus source and window.")]))
S.append(("2 · Comparisons", [
    fig(hbars("Rounds by class", [("mocked seam", 64, "31 eps", "indigo", 35), ("env drift", 25, "12 eps", "indigo", 20), ("requirement", 23, "9 eps", "indigo", 15)],
              legend_items=[("omission", "#4A47A3"), ("other", PALE_BAR)], note=("Takeaway:", "the dark part is avoidable.", "red")), "hbars with inner overlay."),
    fig(split_bars("Time split", [("agent-a", 60, "builder"), ("agent-b", 35, "sims")], legend_items=[("fix", "#B4231F"), ("forward", "#DCEFE3")]), "split_bars."),
    fig(stacked("Share by label", [("BY EPISODE", [54, 22, 6]), ("BY ROUNDS", [115, 37, 24])],
                [("O · omission", "indigo"), ("J · gap", "amber"), ("H · hard", "red")], note=("Band:", "54–66%.", "amber")), "stacked."),
    fig(before_after("Before vs after", [("worst episode", 10, 2, "what fixes it"), ("infra problem", 8, None, "needs a build")]), "before_after.")]))
S.append(("3 · Processes", [
    fig(pipeline("Where bugs enter", [("brief", "ink"), ("build", "ink"), ("test", "ink"), ("review", "ink"), ("LIVE", "red")],
                 below=[(0, "a · requirement", "11%", "amber"), (2, "c · mocked", "38%", "amber")], badges=[(3, "catches logic", "green")],
                 above_link=(2, 4, "found: 2–24 h later", "by live drive", "red"), note=("Why:", "review can't see a mocked seam.", "ink")), "pipeline."),
    fig(swimlanes("Loop by size", ["brief", "read", "build", "proof", "review", "deploy"],
                  [("XS", "tiny", "grey", [None, None, ("build", "grey"), ("1 line", "green"), ("self", "grey"), None]),
                   ("L", "risky", "red", [("checklist", "indigo"), ("probe", "red"), ("seam", "amber"), ("packet", "green"), ("review", "indigo"), ("env+sha", "red")])],
                  note=("Rule:", "no blocking findings ⇒ ship.", "green")), "swimlanes."),
    fig(phases("Roadmap", [("PHASE 0", "files", "no engine", "NEXT", "green", False), ("PHASE 1", "build", "gates\nboard", "M BUILD", "amber", False), ("PHASE 2", "pilot", "1 lane", "GATED", "indigo", True)],
               [("Exit:", "seeded faults must be refused.", "ink")]), "phases."),
    fig(cycle("Knowledge loop", [("CAPTURE", "failed round\n→ 1 lesson", "amber"), ("CURATE", "cheap model\nbudgeted", "indigo"), ("CARD", "1 page/system", "green"), ("PULL", "at brief", "blue")],
              "feeds back", ["sys A · owner", "sys B · owner"], notes=[("End state:", "memory replaces it.", "indigo")]), "cycle.")]))
S.append(("4 · Verdicts", [
    fig(two_columns("Keep vs delete", ("KEEP", "green", [("real probes", "found leaks")]), ("DELETE", "red", [("typed matrix", "self-report"), ("keep-warm", "burn")])), "two_columns."),
    fig(board("Old estate", [("KILL", "red", ["stage agents"]), ("SLIM", "amber", ["4 verifiers → 1"]), ("KEEP", "green", ["stop rule"])]), "board."),
    fig(ranked_rows("Steers", [("B", "read + probe first", "before design", 26, "script", "green"), ("G", "re-read numbers", "before stating", 6, "honour", "red")],
                    "rounds prevented", "enforced by"), "ranked_rows."),
    fig(ladder("Review tiers", [("XS", "self", "no verdict", "grey"), ("S/L", "reviewer", "one round", "blue"), ("ESC", "senior", "risky only", "indigo")]), "ladder."),
    fig(status_matrix("Capabilities", [("definitions", "LIVE", "green", "8 defs"), ("predicate gates", "MISSING", "red", "0 ran"), ("model tier", "PARTIAL", "amber", "FULL or LIGHT")]), "status_matrix."),
    fig(targets("Targets", [("first-time ship", "1 in 13", "≥1 in 3", .08, .33), ("tokens / lane", "unmeasured", "no rise", None, None)],
                note=("Falsifier:", "no movement in 2 weeks ⇒ cut it.", "amber")), "targets.")]))
html = page("vispage component gallery", "Every component with demo data.", "copy this file, swap in evidence.", S,
            nav_links=[("components", "#")], author="vispage", version="gallery")
out = sys.argv[1] if len(sys.argv) > 1 else "vispage-gallery.html"
open(out, "w").write(html); print("wrote", out)

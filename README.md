# diagram-skills

Three [Claude Code](https://claude.com/claude-code) skills for building diagram-led HTML pages.
All three are plain Python that writes SVG; no charting library and no network calls at build time.

| Skill | What it makes |
|---|---|
| [`infog`](infog/) | A one-page, multi-panel infographic: icon-badge nodes, swimlanes, metro lines, cycle machines, runways and territory maps, with numbered keys under each diagram instead of text boxes. |
| [`gantt`](gantt/) | Planned-against-actual schedule charts: plan as a dashed band, actual as a solid bar, overruns in red, late starts hatched, gates, milestones and a today line, with a stacked layout for phones. Same palette as vispage. |
| [`vispage`](vispage/) | Evidence-report pages: 15 data-driven SVG figure types (KPI tiles, ranked bars, stacked splits, pipelines, swimlanes, phases, verdict boards, status matrices …), a page shell, and a render checker that fails on overflowing or colliding labels. |

## Install
```bash
git clone https://github.com/alphafarmer/diagram-skills
mkdir -p ~/.claude/skills
cp -r diagram-skills/infog diagram-skills/vispage diagram-skills/gantt ~/.claude/skills/
```
Then ask Claude Code for "an infographic of …" or use `/infog`, `/vispage`, `/gantt`.

## Requirements
- Python 3.9+.
- `vispage/render_check.py` only (also checks gantt pages): `pip install playwright && playwright install chromium`.
- Pages link the Manrope and JetBrains Mono fonts from Google Fonts (SIL Open Font License).

## Try it
```bash
python3 vispage/example.py gallery.html          # every vispage component with demo data
python3 vispage/render_check.py gallery.html shots
python3 gantt/example.py gantt.html                # two demo schedules
```

## License
MIT. See [LICENSE](LICENSE).

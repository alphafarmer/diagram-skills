#!/usr/bin/env python3
"""vispage — component library for evidence-report pages.

Every figure function takes plain data and returns an SVG string (viewBox 920 wide, scales to
the container). Compose them with page(). Then run render_check.py: it FAILS on text that
overflows or overlaps and writes a screenshot of every figure for you to eyeball.
See example.py for every component with demo data.
"""
import html as _html
import subprocess

E = _html.escape
W = 920  # every figure is drawn in a 920-unit-wide viewBox

# ---- palette (do not invent new colours) ----
INK, MUT, LINE, CARD, BG = "#1B2029", "#5B6472", "#D6DAE2", "#FFFFFF", "#EDEFF3"
TONES = {  # tone -> (solid, tint, border, light-text-on-solid)
    "green":  ("#0F7B33", "#DCEFE3", "#BCDDC9", "#CDE6D6"),
    "amber":  ("#B45309", "#FFF1DC", "#F0DDBB", "#F5E2C8"),
    "red":    ("#B4231F", "#FBF1F1", "#E7C7C7", "#F6D2D0"),
    "indigo": ("#4A47A3", "#E7E9F5", "#CBCEE8", "#D8D9EE"),
    "blue":   ("#2F6BFF", "#E3ECFF", "#C9D8FF", "#D6E2FF"),
    "ink":    ("#1B2029", "#F2F3F6", "#D6DAE2", "#AEB6C6"),
    "grey":   ("#8A93A3", "#F2F3F6", "#D6DAE2", "#EEF0F3"),
}
PALE_BAR = "#C9CEE8"
FONT = 'font-family="Manrope,sans-serif"'
MONO = "font-family=\"'JetBrains Mono',monospace\""


def tone(name):
    return TONES[name]


def stamp():
    """The page timestamp. ALWAYS from the clock, never estimated."""
    return subprocess.check_output(["date", "-u", "+%Y-%m-%d · %H:%MZ"]).decode().strip()


# ---------------------------------------------------------------- primitives
def svg(height, label, title, body, arrows=False):
    defs = ('<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
            f'<path d="M0 0 L9 4.5 L0 9 z" fill="{MUT}"/></marker></defs>') if arrows else ""
    return (f'<svg viewBox="0 0 {W} {height}" role="img" aria-label="{E(label)}" '
            f'style="display:block;width:100%;height:auto">{defs}'
            f'<text x="0" y="14" {FONT} font-size="13" font-weight="800" fill="{INK}">{E(title.upper())}</text>'
            f'<g {FONT}>{body}</g></svg>')


def text(x, y, s, size=12, fill=INK, weight=400, anchor="start", mono=False, raw=False):
    """raw=True lets you pass pre-built <tspan> markup (use rich())."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {MONO if mono else ""}>{s if raw else E(s)}</text>')


def rich(label, body, color=INK):
    """'<b>Label:</b> body' inside one <text>: a bold coloured lead-in, then plain text."""
    return f'<tspan font-weight="800" fill="{color}">{E(label)}</tspan> {E(body)}'


def rect(x, y, w, h, fill, stroke=None, rx=8, sw=1, dash=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{h}" rx="{rx}" fill="{fill}"{s}{d}/>'


def arrow(x1, y1, x2, y2, color=MUT, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#ah)"{d}/>'


def note_bar(y, label, body, tn="ink"):
    """Full-width tinted strip with a bold lead-in: the figure's takeaway. Keep to ~130 characters."""
    solid, tint, border, _ = tone(tn)
    lead = solid if tn != "ink" else INK
    return rect(0, y, W, 34, tint, border) + text(16, y + 21, rich(label, body, lead), 12, raw=True)


def legend(x, y, items):
    """items = [(label, fill)]"""
    out, cx = "", x
    for lab, fill in items:
        out += rect(cx, y, 12, 12, fill, rx=2) + text(cx + 18, y + 10, lab, 11, MUT)
        cx += 30 + 6.2 * len(lab)
    return out


# ---------------------------------------------------------------- figures
def kpi_tiles(title, tiles, notes=()):
    """tiles = [(value, label, tone)]  (3-5 tiles)   notes = [(lead, body, tone)]
    The headline figure: big numbers in solid tiles, then 1-2 takeaway strips."""
    n = len(tiles); gap = 15; tw = (W - gap * (n - 1)) / n
    b = ""
    for i, (v, lab, tn) in enumerate(tiles):
        solid, _, _, light = tone(tn); x = i * (tw + gap)
        b += rect(x, 30, tw, 76, solid, rx=10) + text(x + tw / 2, 66, v, 28, "#fff", 800, "middle")
        b += text(x + tw / 2, 90, lab, 11.5, light, 400, "middle")
    y = 120
    for lead, body, tn in notes:
        b += note_bar(y, lead, body, tn); y += 42
    return svg(y + 4, title, title, b)


def hbars(title, rows, vmax=None, value_fmt="{}", inner=None, legend_items=(), note=None, label_w=200, bar_w=520):
    """Ranked horizontal bars.
    rows = [(label, value, side_note, tone, inner_value)]  (side_note/tone/inner_value optional)
    inner_value draws a dark overlay (e.g. the part that was omission); pale bar = the rest."""
    vmax = vmax or max(r[1] for r in rows)
    b = ""
    for i, r in enumerate(rows):
        lab, v = r[0], r[1]
        side = r[2] if len(r) > 2 else ""
        tn = r[3] if len(r) > 3 and r[3] else "indigo"
        iv = r[4] if len(r) > 4 else None
        y = 34 + i * 28; fw = bar_w * v / vmax
        b += text(0, y + 14, lab, 12.5, INK, 700)
        if iv is not None:
            b += rect(label_w, y, fw, 18, PALE_BAR, rx=4) + rect(label_w, y, bar_w * iv / vmax, 18, tone(tn)[0], rx=4)
        else:
            b += rect(label_w, y, fw, 18, tone(tn)[0], rx=4)
        b += text(label_w + fw + 8, y + 14, value_fmt.format(v), 12, INK, 800)
        if side:
            b += text(W, y + 14, side, 11, MUT, 400, "end")
    y = 34 + len(rows) * 28 + 4
    if legend_items:
        b += legend(label_w, y, legend_items); y += 22
    if note:
        b += note_bar(y + 4, *note); y += 46
    return svg(y + 4, title, title, b)


def split_bars(title, rows, vmax=100, left_tone="red", right_tone="green", fmt="{}% fix", legend_items=(), label_w=150, bar_w=600):
    """Each row is one bar split in two (e.g. fix vs forward time). rows = [(label, left_value, note)]"""
    b = ""
    for i, (lab, v, nt) in enumerate(rows):
        y = 34 + i * 26; fw = bar_w * v / vmax
        b += text(0, y + 14, lab, 12.5, INK, 700) + rect(label_w, y, fw, 18, tone(left_tone)[0], rx=4)
        b += rect(label_w + fw, y, bar_w - fw, 18, tone(right_tone)[1], rx=4)
        if fw > 50:
            b += text(label_w + 6, y + 13, fmt.format(v), 10.5, "#fff", 700)
        b += text(label_w + bar_w + 12, y + 13, nt, 11, MUT)
    y = 34 + len(rows) * 26 + 6
    if legend_items:
        b += legend(label_w, y, legend_items); y += 20
    return svg(y + 4, title, title, b)


def stacked(title, rows, segments, legend_rows=True, note=None, label_w=150):
    """100% stacked bars. segments = [(name, tone)]; rows = [(row_label, [values in segment order])]"""
    b = ""
    for ri, (rl, vals) in enumerate(rows):
        y = 40 + ri * 64; tot = sum(vals); x = label_w
        b += text(0, y + 22, rl, 11.5, MUT, 800)
        for (name, tn), v in zip(segments, vals):
            w = (W - label_w) * v / tot
            b += rect(x, y, w - 2, 36, tone(tn)[0], rx=6)
            if w > 70:
                b += text(x + w / 2, y + 23, f"{v} · {round(100 * v / tot)}%", 13, "#fff", 800, "middle")
            x += w
    y = 40 + len(rows) * 64
    if legend_rows:
        for i, (name, tn) in enumerate(segments):
            b += rect(0, y + i * 22, 12, 12, tone(tn)[0], rx=2) + text(20, y + i * 22 + 10, name, 12)
        y += len(segments) * 22 + 6
    if note:
        b += note_bar(y, *note); y += 42
    return svg(y + 4, title, title, b)


def pipeline(title, stages, below=(), above_link=None, badges=(), note=None):
    """A left-to-right flow of stages with callouts.
    stages = [(label, tone)]          below = [(stage_idx, label, sub, tone)]  arrows up into the stage
    above_link = (from_idx, to_idx, label, sub, tone)  dashed arc from one stage to another + a callout box
    badges = [(stage_idx, label, tone)]  small chip just under a stage"""
    n = len(stages); gap = 20; sw = (W - gap * (n - 1)) / n
    xs = [i * (sw + gap) for i in range(n)]
    b = ""
    for i, (lab, tn) in enumerate(stages):
        b += rect(xs[i], 44, sw, 40, tone(tn)[0], rx=9) + text(xs[i] + sw / 2, 69, lab, 13, "#fff", 800, "middle")
        if i < n - 1:
            b += arrow(xs[i] + sw + 2, 64, xs[i + 1] - 2, 64)
    for i, lab, tn in badges:
        solid, tint, border, _ = tone(tn)
        b += rect(xs[i] + 4, 98, sw - 8, 22, tint, border, rx=6) + text(xs[i] + sw / 2, 113, lab, 10.5, solid, 700, "middle")
    y = 134
    for i, lab, sub, tn in below:
        solid, tint, border, _ = tone(tn); cx = xs[i] + sw / 2
        b += f'<path d="M{cx:.1f} {y} L{cx:.1f} 90" stroke="{solid}" stroke-width="2" marker-end="url(#ah)"/>'
        b += rect(cx - 64, y, 128, 38, tint, border, rx=7) + text(cx, y + 16, lab, 11, INK, 700, "middle") + text(cx, y + 31, sub, 10.5, solid, 700, "middle")
    y = 184 if below else 134
    if above_link:
        a, z, lab, sub, tn = above_link; solid, tint, border, _ = tone(tn)
        x1, x2 = xs[a] + sw * 0.7, xs[z] + sw * 0.3
        b += f'<path d="M{x1:.1f} 42 Q {(x1 + x2) / 2:.1f} 6 {x2:.1f} 42" stroke="{solid}" stroke-width="2.5" fill="none" stroke-dasharray="6 4" marker-end="url(#ah)"/>'
        bx = min(xs[z] + sw - 170, W - 170)
        b += rect(bx, y + 6, 170, 46, tint, border, rx=8) + text(bx + 85, y + 25, lab, 11.5, solid, 800, "middle") + text(bx + 85, y + 42, sub, 11, INK, 400, "middle")
        y += 58
    if note:
        b += note_bar(y + 6, *note); y += 48
    return svg(y + 4, title, title, b, arrows=True)


def two_columns(title, left, right):
    """Keep-vs-delete, added-vs-removed, pros-vs-cons.
    left/right = (heading, tone, [(item, side_note)])"""
    b, colw = "", (W - 16) / 2
    for ci, (head, tn, items) in enumerate((left, right)):
        solid, tint, border, _ = tone(tn); x = ci * (colw + 16)
        b += rect(x, 28, colw, 34, solid, rx=9) + text(x + 16, 50, head, 13, "#fff", 800)
        for i, (it, nt) in enumerate(items):
            y = 70 + i * 36
            b += rect(x, y, colw, 30, tint, border, rx=7) + text(x + 12, y + 19, it, 12, INK, 800)
            if nt:
                b += text(x + colw - 12, y + 19, nt, 10.5, solid, 600, "end")
    h = 70 + max(len(left[2]), len(right[2])) * 36
    return svg(h, title, title, b)


def swimlanes(title, columns, lanes, note=None):
    """Process by lane (e.g. change size) x step. columns = [step names]
    lanes = [(name, description, tone, [cell or None])]; cell = (label, tone)  None = step skipped."""
    lane_w, gap = 128, 10
    cw = (W - lane_w - gap * len(columns)) / len(columns)
    cx = [lane_w + gap + i * (cw + gap) for i in range(len(columns))]
    b = "".join(text(cx[i] + cw / 2, 40, c.upper(), 11.5, MUT, 800, "middle") for i, c in enumerate(columns))
    for li, (name, desc, tn, cells) in enumerate(lanes):
        y = 52 + li * 70
        b += rect(0, y, lane_w, 58, tone(tn)[0], rx=10) + text(lane_w / 2, y + 28, name, 20, "#fff", 800, "middle")
        b += text(lane_w / 2, y + 46, desc, 9, "#fff", 600, "middle")
        prev = None
        for i, cell in enumerate(cells):
            if cell is None:
                b += rect(cx[i], y + 14, cw, 30, "#FFFFFF", LINE, rx=7, dash="4 4") + text(cx[i] + cw / 2, y + 34, "—", 12, "#AEB6C6", 400, "middle")
                continue
            lab, ctn = cell
            b += rect(cx[i], y + 8, cw, 42, tone(ctn)[1], LINE, rx=8) + text(cx[i] + cw / 2, y + 34, lab, 10.5, INK, 700, "middle")
            if prev is not None:
                b += arrow(cx[prev] + cw + 1, y + 29, cx[i] - 2, y + 29)
            prev = i
    y = 52 + len(lanes) * 70
    if note:
        b += note_bar(y, *note); y += 42
    return svg(y + 4, title, title, b, arrows=True)


def ranked_rows(title, rows, value_caption="", chip_caption="", note=None, bar_x=470, bar_w=250):
    """Keyed, ranked list with a bar and a status chip — e.g. rules/steers/risks.
    rows = [(key, label, meta, value, chip_text, chip_tone)]"""
    vmax = max(r[3] for r in rows)
    b = text(bar_x, 34, value_caption, 11, MUT) + text(W, 34, chip_caption, 11, MUT, 400, "end")
    for i, (k, lab, meta, v, chip, ctn) in enumerate(rows):
        y = 44 + i * 30; solid, tint, border, _ = tone(ctn)
        b += rect(0, y, 26, 22, INK, rx=6) + text(13, y + 16, k, 12, "#fff", 800, "middle", mono=True)
        b += text(36, y + 16, lab, 12, INK, 700) + text(bar_x - 5, y + 16, meta, 10.5, MUT, 600, "end")
        bw = bar_w * v / vmax
        b += rect(bar_x, y + 2, bw, 18, tone("indigo")[0], rx=4) + text(bar_x + bw + 6, y + 16, str(v), 11.5, INK, 800)
        b += rect(W - 128, y + 1, 128, 20, tint, border, rx=6) + text(W - 64, y + 15, chip.upper(), 9.5, solid, 800, "middle", mono=True)
    y = 44 + len(rows) * 30 + 4
    if note:
        b += note_bar(y, *note); y += 42
    return svg(y + 4, title, title, b)


def ladder(title, steps, note=None):
    """Escalation ladder, each rung indented. steps = [(label, who, when, tone)]"""
    b = ""
    for i, (lab, who, when, tn) in enumerate(steps):
        x, y, w = i * 60, 34 + i * 50, W - i * 60
        b += rect(x, y, w, 42, tone(tn)[0], rx=9) + text(x + 16, y + 26, lab, 13, "#fff", 800) + text(x + 110, y + 26, who, 13, "#fff", 800)
        b += text(x + w - 14, y + 26, when, 11, "#fff", 500, "end")
    y = 34 + len(steps) * 50 + 4
    if note:
        b += note_bar(y, *note); y += 42
    return svg(y + 4, title, title, b)


def before_after(title, rows, before_cap="before", after_cap="after", unit_px=15, label_w=280):
    """Paired bars per item. rows = [(label, before, after_or_None, note)]; None = 'needs other fix' chip."""
    b = text(label_w, 34, before_cap, 11, tone("red")[0], 800) + text(label_w + 170, 34, after_cap, 11, tone("green")[0], 800)
    for i, (lab, bv, av, nt) in enumerate(rows):
        y = 44 + i * 40
        b += text(0, y + 20, lab, 12, INK, 700)
        b += rect(label_w, y + 6, unit_px * bv, 20, tone("red")[0], rx=4) + text(label_w + unit_px * bv + 5, y + 21, str(bv), 11.5, tone("red")[0], 800)
        if av is not None:
            b += rect(label_w + 170, y + 6, unit_px * av, 20, tone("green")[0], rx=4) + text(label_w + 170 + unit_px * av + 5, y + 21, f"~{av}", 11.5, tone("green")[0], 800)
        else:
            s, t_, bd, _ = tone("amber")
            b += rect(label_w + 170, y + 6, 86, 20, t_, bd, rx=4) + text(label_w + 213, y + 20, "other fix", 10, s, 800, "middle")
        b += text(label_w + 280, y + 20, nt, 10.5, MUT)
    return svg(44 + len(rows) * 40, title, title, b)


def board(title, columns, note=None):
    """Kanban-style verdict board (e.g. KILL / SLIM / KEEP). columns = [(heading, tone, [items])]"""
    n = len(columns); gap = 10; cw = (W - gap * (n - 1)) / n
    b = ""
    for ci, (head, tn, items) in enumerate(columns):
        solid, tint, border, _ = tone(tn); x = ci * (cw + gap)
        b += rect(x, 28, cw, 34, solid, rx=9) + text(x + cw / 2, 50, head, 13, "#fff", 800, "middle")
        for j, it in enumerate(items):
            y = 70 + j * 38
            b += rect(x, y, cw, 32, tint, border, rx=7) + text(x + 12, y + 20, it, 11.5, INK, 700)
    y = 70 + max(len(c[2]) for c in columns) * 38 + 4
    if note:
        b += note_bar(y, *note); y += 42
    return svg(y + 4, title, title, b)


def status_matrix(title, rows, cap_w=330):
    """Capability/status table as a figure. rows = [(capability, STATUS, tone, note)]"""
    b = ""
    for i, (cap, st, tn, nt) in enumerate(rows):
        y = 30 + i * 32; solid, tint, _, _ = tone(tn)
        b += rect(0, y, W, 26, "#FFFFFF" if tn == "green" else tint, LINE, rx=6) + text(12, y + 17, cap, 12, INK, 700)
        b += rect(cap_w, y + 4, 86, 18, solid, rx=5) + text(cap_w + 43, y + 17, st, 10, "#fff", 800, "middle", mono=True)
        b += text(cap_w + 100, y + 17, nt, 11, MUT)
    return svg(30 + len(rows) * 32, title, title, b)


def phases(title, items, notes=()):
    """Phase/gate roadmap. items = [(tag, name, "line1\\nline2", STATE, tone, dashed)]
    notes = [(lead, body, tone)]. dashed=True for gated/not-started phases."""
    n = len(items); gap = 16; pw = (W - gap * (n - 1)) / n
    b = ""
    for i, (tag, name, desc, st, tn, dashed) in enumerate(items):
        solid, tint, _, _ = tone(tn); x = i * (pw + gap)
        b += rect(x, 30, pw, 116, tint, solid, rx=11, sw=2.5, dash="7 5" if dashed else None)
        b += text(x + 14, 52, tag, 12.5, solid, 800) + text(x + 14, 70, name, 12, INK, 800)
        for j, line in enumerate(desc.split("\n")):
            b += text(x + 14, 88 + j * 15, line, 10.5, MUT)
        b += rect(x + 14, 120, 76, 19, solid, rx=6) + text(x + 52, 134, st, 10, "#fff", 800, "middle")
        if i < n - 1:
            b += arrow(x + pw + 1, 88, x + pw + gap - 1, 88)
    y = 158
    for lead, body, tn in notes:
        b += note_bar(y, lead, body, tn); y += 42
    return svg(y + 4, title, title, b, arrows=True)


def cycle(title, boxes, loop_label="", chips=(), chip_tone="green", notes=()):
    """A 3-5 stage lifecycle with a feedback loop back to the start.
    boxes = [(heading, "line1\\nline2", tone)]   chips = [text] (e.g. owners)   notes = [(lead, body, tone)]"""
    n = len(boxes); gap = 40; bw = (W - gap * (n - 1)) / n
    b = ""
    for i, (h, d, tn) in enumerate(boxes):
        solid, tint, _, _ = tone(tn); x = i * (bw + gap)
        b += rect(x, 30, bw, 84, tint, solid, rx=10, sw=2) + text(x + 14, 52, h, 12.5, solid, 800)
        for j, line in enumerate(d.split("\n")):
            b += text(x + 14, 72 + j * 16, line, 10.5, INK)
        if i < n - 1:
            b += arrow(x + bw + 3, 72, x + bw + gap - 3, 72)
    last = (n - 1) * (bw + gap) + bw / 2
    b += f'<path d="M{last:.1f} 116 L{last:.1f} 140 L{bw/2:.1f} 140 L{bw/2:.1f} 118" stroke="{MUT}" stroke-width="2" fill="none" stroke-dasharray="5 4" marker-end="url(#ah)"/>'
    if loop_label:
        b += text(W / 2, 136, loop_label, 10.5, MUT, 600, "middle")
    y = 152
    if chips:
        cw = (W - 8 * (len(chips) - 1)) / len(chips); solid, _, border, _ = tone(chip_tone)
        for i, c in enumerate(chips):
            x = i * (cw + 8)
            b += rect(x, y + 4, cw, 26, "#FFFFFF", border, rx=6) + text(x + cw / 2, y + 21, c, 10, solid, 700, "middle")
        y += 40
    for lead, body, tn in notes:
        b += note_bar(y, lead, body, tn); y += 42
    return svg(y + 4, title, title, b, arrows=True)


def targets(title, rows, note=None):
    """Metric | now | target, with optional mini before/after bars.
    rows = [(metric, now_text, target_text, now_frac_0to1 or None, target_frac or None)]"""
    b = text(330, 34, "NOW", 11, tone("red")[0], 800) + text(500, 34, "TARGET", 11, tone("green")[0], 800)
    for i, (m, now, tgt, a, z) in enumerate(rows):
        y = 44 + i * 32
        b += rect(0, y, W, 26, "#FFFFFF" if i % 2 else "#F2F3F6", LINE, rx=6) + text(12, y + 17, m, 12, INK, 700)
        b += text(330, y + 17, now, 12, tone("red")[0], 800) + text(500, y + 17, tgt, 12, tone("green")[0], 800)
        if a is not None:
            b += rect(640, y + 7, 260 * a, 6, tone("red")[0], rx=3) + rect(640, y + 15, 260 * z, 6, tone("green")[0], rx=3)
    y = 44 + len(rows) * 32 + 4
    if note:
        b += note_bar(y, *note); y += 42
    return svg(y + 4, title, title, b)


# ---------------------------------------------------------------- page shell
CSS = """
:root{--bg:#EDEFF3;--ink:#1B2029;--muted:#5B6472;--line:#D6DAE2;--card:#FFFFFF;--accent:#2F6BFF;--green:#0F7B33;--amber:#B45309;--red:#B4231F}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font-family:Manrope,system-ui,sans-serif;line-height:1.55;font-size:15px}
.wrap{max-width:980px;margin:0 auto;padding:40px 24px 80px} h1{font-size:29px;font-weight:800;letter-spacing:-.02em;margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 26px} h2{font-size:20px;font-weight:800;margin:38px 0 12px} h3{font-size:16px;font-weight:800;margin:22px 0 8px}
p{margin:0 0 14px} code{font-family:'JetBrains Mono',monospace;font-size:12px;background:#EEF1F6;padding:1px 5px;border-radius:5px}
a{color:var(--accent)} ol,ul{margin:0 0 14px;padding-left:20px} li{margin:0 0 7px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin:16px 0}
.warn{background:#FFF8EC;border:1px solid #F0DDBB;border-radius:10px;padding:12px 16px;font-size:13.5px;margin:14px 0}
.fault{background:#FBF1F1;border:1px solid #E7C7C7;border-radius:12px;padding:14px 18px;margin:12px 0}
.keep{background:#EFF6F1;border:1px solid #C7E0CF;border-radius:12px;padding:14px 18px;margin:12px 0}
table{width:100%;border-collapse:collapse;font-size:12.5px;margin:10px 0}
th{background:#1B2029;color:#fff;text-align:left;padding:7px 9px;font-size:10.5px;letter-spacing:.04em;text-transform:uppercase}
td{padding:6px 9px;border-bottom:1px solid var(--line);vertical-align:top}
.tablebox{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
.chip{font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:6px;text-transform:uppercase;letter-spacing:.03em;border:1px solid}
.chip.green{background:#DCEFE3;color:#0F7B33;border-color:#BCDDC9}.chip.indigo{background:#E7E9F5;color:#4A47A3;border-color:#CBCEE8}
.chip.red{background:#FBF1F1;color:#B4231F;border-color:#E7C7C7}.chip.amber{background:#FFF1DC;color:#B45309;border-color:#F0DDBB}
.fig{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
.fig svg{display:block;width:100%;height:auto} .figcap{font-size:12px;color:var(--muted);margin:10px 0 0}
details{margin:8px 0} summary{cursor:pointer;font-weight:700;color:var(--accent)}
.nav{font-size:13px;color:var(--muted);margin-bottom:14px}
"""


def fig(svg_str, caption):
    """A figure card. The caption says what to conclude and names the source/caveat."""
    return f'<div class="fig">{svg_str}<p class="figcap">{caption}</p></div>'


def chip(label, tn="indigo"):
    return f'<span class="chip {tn}">{E(label)}</span>'


def details(summary, inner_html):
    return f'<details><summary>{E(summary)}</summary><div class="card">{inner_html}</div></details>'


def page(title, subtitle_html, oneliner_html, sections, nav_links=(), author="", version="", tail_html=""):
    """sections = [(h2_text, [html blocks...])]  nav_links = [(label, url)]  (backlinks are required)"""
    nav = " · ".join(f'<a href="{u}">{E(l)}</a>' for l, u in nav_links)
    meta = " · ".join(x for x in (f"Last updated: {stamp()}", author, version) if x)
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1">'
           f'<title>{E(title)}</title>'
           '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">'
           f'<style>{CSS}</style></head><body><div class="wrap">',
           f'<div class="nav">&#8592; {nav}{" · " if nav else ""}{meta}</div>',
           f'<h1>{E(title)}</h1><p class="sub">{subtitle_html}</p>',
           f'<div class="warn"><b>In one line:</b> {oneliner_html}</div>']
    for h, blocks in sections:
        out.append(f"<h2>{E(h)}</h2>")
        out.extend(blocks)
    out.append(tail_html)
    out.append("</div></body></html>")
    return "\n".join(out)

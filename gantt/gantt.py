#!/usr/bin/env python3
"""gantt — planned-against-actual schedule charts as SVG, in the vispage palette.

gantt(title, rows, start, end, today=None) returns a 920-wide SVG; gantt_phone(...) returns the
same schedule stacked for a 390px screen; gantt_block(...) returns both, switched by CSS.
Each row draws its PLAN as a dashed band and its ACTUAL as a solid bar under it:
  blue = in work, green = done, red = the part that ran past the planned end (labelled "+N d").
A row not started after its planned start shows a hatched amber stub up to today.
Gates are diamonds, milestones are flags, and a blue line marks today.
Drop the SVG into a vispage fig() card, or use page() here for a standalone page.
"""
import datetime as _dt
import html as _html
import subprocess

E = _html.escape
W = 920

INK, MUT, LINE, CARD, BG = "#1B2029", "#5B6472", "#D6DAE2", "#FFFFFF", "#EDEFF3"
TONES = {  # same palette as vispage: tone -> (solid, tint, border)
    "green": ("#0F7B33", "#DCEFE3", "#BCDDC9"), "amber": ("#B45309", "#FFF1DC", "#F0DDBB"),
    "red": ("#B4231F", "#FBF1F1", "#E7C7C7"), "indigo": ("#4A47A3", "#E7E9F5", "#CBCEE8"),
    "blue": ("#2F6BFF", "#E3ECFF", "#C9D8FF"), "grey": ("#8A93A3", "#F2F3F6", "#D6DAE2"),
}
HEAD = "#1E3A8A"  # dark blue: chart titles and the header band
HEAD_SUB = "#C9D8FF"  # light text and dividers on the dark header band
RULE = "#8FA6D8"  # month dividers down the chart body
FONT = 'font-family="Manrope,sans-serif"'


def _t(x, y, s, size=12, fill=INK, weight=400, anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{E(str(s))}</text>')


def _tw(s, size):
    """rough text width in svg units (Manrope)"""
    return len(str(s)) * size * 0.56


def _d(s, d0):
    """'2026-03-02' or '2026-03-02T12:00' -> float days since d0"""
    d = _dt.datetime.fromisoformat(s if "T" in s else s + "T00:00")
    return (d - d0).total_seconds() / 86400


def _days(d):
    d = round(d * 2) / 2
    return f"{d:g} d"


def _diamond(cx, cy, r=7):
    return (f'<path d="M{cx:.1f} {cy - r:.1f}L{cx + r:.1f} {cy:.1f}L{cx:.1f} {cy + r:.1f}L{cx - r:.1f} {cy:.1f}Z" '
            f'fill="{TONES["indigo"][0]}" stroke="{CARD}" stroke-width="2"/>')


def _flag(x, y0, y1):
    return (f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="{TONES["green"][0]}" stroke-width="1.8"/>'
            f'<path d="M{x:.1f} {y0:.1f}l9 3.5l-9 3.5Z" fill="{TONES["green"][0]}"/>')


_N = [0]


def _hid():
    """a fresh pattern id per drawing: a hidden copy's <defs> can't feed a visible one"""
    _N[0] += 1
    return f"gt-hatch-{_N[0]}"


def _defs(hid):
    a = TONES["amber"]
    return (f'<defs><pattern id="{hid}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="6" height="6" fill="{a[1]}"/><line x1="0" y1="0" x2="0" y2="6" stroke="{a[0]}" stroke-width="2"/></pattern></defs>')


def _prep(rows, start, end, today):
    d0 = _dt.datetime.fromisoformat(start + "T00:00")
    span, td = _d(end, d0), (_d(today, d0) if today else None)
    out = []
    for r in rows:
        r = dict(r)
        if r.get("label"):
            r["_ps"], r["_pe"] = _d(r["plan"][0], d0), _d(r["plan"][1], d0)
            a = r.get("actual")
            if a:
                run = a[1] is None
                if run and td is None:
                    raise ValueError(f"row {r['label']!r} is still running: pass today=")
                r["_a"] = (_d(a[0], d0), td if run else _d(a[1], d0), run)
            else:
                r["_a"] = None
            r["_g"] = [(_d(d, d0), lab) for d, lab in r.get("gates", [])]
            r["_f"] = [(_d(d, d0), lab) for d, lab in r.get("flags", [])]
        out.append(r)
    return d0, span, td, out


def status(r, today):
    """(words, tone) for one row: on plan / N d late / in work / not started"""
    ps, pe, a = r["_ps"], r["_pe"], r["_a"]
    if a is None:
        if today is not None and today > ps:
            return ("not started · " + _days(today - ps) + " past start", "amber")
        return ("not started", "grey")
    a0, a1, run = a
    late = a1 - pe
    if run:
        return ("in work", "blue") if late <= 0.05 else (f"in work · +{_days(late)} over plan", "red")
    if late > 0.05:
        return (f"done · {_days(late)} late", "amber" if late <= 3 else "red")
    return ("done · on plan" if late > -0.5 else f"done · {_days(-late)} early", "green")


def _ticks(d0, span, px_per_day, min_px):
    """day ticks thinned to a readable step: 1, 2, 7, 14 or ~30 days"""
    step = next((s for s in (1, 2, 7, 14) if s * px_per_day >= min_px), None)
    out = []
    if step is None:  # long spans: the first of each month
        for i in range(int(span) + 1):
            d = d0 + _dt.timedelta(days=i)
            if d.day == 1:
                out.append((i, f"{d:%b %Y}" if d.month == 1 or not out else f"{d:%b}"))
        return out
    for i in range(0, int(span) + 1, step):
        d = d0 + _dt.timedelta(days=i)
        out.append((i, f"{d.day} {d:%b}"))
    return out


def _months(d0, span):
    """(start_day, end_day, name) for each calendar month the axis touches"""
    out, i = [], 0
    while i < span:
        d = d0 + _dt.timedelta(days=i)
        nxt = (d.replace(day=1) + _dt.timedelta(days=32)).replace(day=1)
        j = min((nxt - d0).days, span)
        out.append((i, j, f"{d:%B %Y}" if j - i > 6 else f"{d:%b}"))
        i = j
    return out


def _group_stats(rs, today):
    """group row id -> (items, items behind plan)"""
    out, cur = {}, None
    for r in rs:
        if r.get("group") and not r.get("label"):
            cur = id(r)
            out[cur] = [0, 0]
        elif cur is not None:
            out[cur][0] += 1
            out[cur][1] += status(r, today)[1] in ("red", "amber")
    return {k: tuple(v) for k, v in out.items()}


def _bars(x, r, gy, ay, today, hid):
    """plan band, actual bar (with overrun), not-started stub, gates and flags for one row"""
    g = []
    ps, pe, a = r["_ps"], r["_pe"], r["_a"]
    solid = lambda t: TONES[t][0]  # noqa: E731
    g.append(f'<rect x="{x(ps):.1f}" y="{gy}" width="{max(x(pe) - x(ps), 4):.1f}" height="9" rx="4.5" fill="{TONES["grey"][1]}" '
             f'stroke="{TONES["grey"][0]}" stroke-width="1.2" stroke-dasharray="4 3"><title>planned</title></rect>')
    if a is not None:
        a0, a1, run = a
        base = "blue" if run else "green"
        cut = min(max(pe, a0), a1)
        g.append(f'<rect x="{x(a0):.1f}" y="{ay}" width="{max(x(cut) - x(a0), 4):.1f}" height="12" rx="6" fill="{solid(base)}"/>')
        if a1 - pe > 0.05:
            g.append(f'<rect x="{x(cut):.1f}" y="{ay}" width="{max(x(a1) - x(cut), 4):.1f}" height="12" rx="6" fill="{solid("red")}">'
                     f'<title>past the planned end</title></rect>')
    elif today is not None and today > ps:
        g.append(f'<rect x="{x(ps):.1f}" y="{ay}" width="{max(x(today) - x(ps), 4):.1f}" height="12" rx="3" fill="url(#{hid})" '
                 f'stroke="{TONES["amber"][2]}"><title>should have started</title></rect>')
    for d, lab in r["_f"]:
        g.append(f'<g><title>{E(lab)}</title>{_flag(x(d), ay - 8, ay + 14)}</g>')
    for d, lab in r["_g"]:
        g.append(f'<g><title>gate: {E(lab)}</title>{_diamond(x(d), ay + 6)}</g>')
    return g


def _row_end(x, r, today):
    a = r["_a"]
    ends = [x(r["_pe"])] + [x(d) for d, _ in r["_g"] + r["_f"]]
    if a:
        ends.append(x(a[1]))
    elif today is not None and today > r["_ps"]:
        ends.append(x(today))
    return max(ends), min([x(r["_ps"])] + ([x(a[0])] if a else []))


def _key(y, items, hid, width=W):
    """key glyphs laid left to right, wrapping at width"""
    g, cx = [], 0
    for glyph, words in items:
        glyph = glyph.replace("HATCH", hid)
        if cx + 22 + _tw(words, 11.5) > width:
            cx, y = 0, y + 22
        g.append(f'<g transform="translate({cx},{y})">{glyph}</g>' + _t(cx + 22, y + 11, words, 11.5, MUT))
        cx += 22 + _tw(words, 11.5) + 22
    return "".join(g), y


KEY = [
    (f'<rect x="0" y="3" width="16" height="9" rx="4.5" fill="{TONES["grey"][1]}" stroke="{TONES["grey"][0]}" stroke-dasharray="3 2"/>', "planned"),
    (f'<rect x="0" y="1" width="16" height="12" rx="6" fill="{TONES["blue"][0]}"/>', "in work"),
    (f'<rect x="0" y="1" width="16" height="12" rx="6" fill="{TONES["green"][0]}"/>', "done"),
    (f'<rect x="0" y="1" width="16" height="12" rx="6" fill="{TONES["red"][0]}"/>', "past plan"),
    (f'<rect x="0" y="1" width="16" height="12" rx="3" fill="url(#HATCH)"/>', "late start"),
    (_diamond(8, 7, 6), "gate"), (_flag(4, 0, 14), "milestone"),
    (f'<line x1="8" y1="0" x2="8" y2="14" stroke="{TONES["blue"][0]}" stroke-width="2"/>', "today"),
]


class _Ctx:
    """one drawing's scale and shared grid: every piece of the chart uses the same x"""

    def __init__(self, rows, start, end, today, width, L, R, min_tick_px):
        self.d0, self.span, self.td, self.rs = _prep(rows, start, end, today)
        self.W, self.L, self.R, self.hid = width, L, R, _hid()
        self.ppd = (width - L - R) / self.span
        self.ticks = _ticks(self.d0, self.span, self.ppd, min_tick_px)
        self.months = _months(self.d0, self.span)

    def x(self, d):
        return self.L + self.ppd * d

    def grid(self, y0, y1, weekends=True):
        """weekend shading, day ticks and month dividers for one horizontal slice"""
        g = []
        if weekends and self.ppd >= 10:
            for i in range(int(self.span) + 1):
                if (self.d0 + _dt.timedelta(days=i)).weekday() >= 5:
                    g.append(f'<rect x="{self.x(i):.1f}" y="{y0}" width="{self.ppd:.1f}" height="{y1 - y0}" fill="{TONES["grey"][1]}"/>')
        for d, _ in self.ticks:
            g.append(f'<line x1="{self.x(d):.1f}" y1="{y0}" x2="{self.x(d):.1f}" y2="{y1}" stroke="{LINE}"/>')
        for i, (m0, _, _) in enumerate(self.months):
            if i:
                g.append(f'<line x1="{self.x(m0):.1f}" y1="{y0}" x2="{self.x(m0):.1f}" y2="{y1}" stroke="{RULE}" stroke-width="1.5"/>')
        return g

    def today_line(self, y0, y1):
        if self.td is None:
            return []
        return [f'<line x1="{self.x(self.td):.1f}" y1="{y0}" x2="{self.x(self.td):.1f}" y2="{y1}" stroke="{TONES["blue"][0]}" stroke-width="2"/>']

    def svg(self, h, label, body, labels=(), cls=""):
        c = f' class="{cls}"' if cls else ""
        return (f'<svg{c} viewBox="0 0 {self.W} {h}" role="img" aria-label="{E(label)}" preserveAspectRatio="xMinYMin meet" '
                f'style="display:block;width:100%;height:auto">{_defs(self.hid)}'
                f'<g {FONT}>{"".join(body)}{"".join(labels)}</g></svg>')


def _rollup(rs, today):
    """a group's summary: (plan start, plan end, actual start, actual end, tone) or None"""
    work = [r for r in rs if r.get("label")]
    if not work:
        return None
    ps, pe = min(r["_ps"] for r in work), max(r["_pe"] for r in work)
    acts = [r["_a"] for r in work if r["_a"]]
    a0 = min(a[0] for a in acts) if acts else None
    a1 = max(a[1] for a in acts) if acts else None
    bad = sum(status(r, today)[1] in ("red", "amber") for r in work)
    open_ = any(r["_a"] is None or r["_a"][2] for r in work)
    tn = "red" if bad else ("blue" if open_ else "green")
    return ps, pe, a0, a1, tn


def _split(rs):
    """[(group_row or None, [work rows])] in display order"""
    out = [(None, [])]
    for r in rs:
        if r.get("group") and not r.get("label"):
            out.append((r, []))
        else:
            out[-1][1].append(r)
    return [(gr, ws) for gr, ws in out if gr is not None or ws]


CHEV = '<path class="gt-chev" d="M{x} {y}l5 5l5-5" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'


def _group_head(c, gr, ws, h, name_y, bar_y, name_x):
    """the group band: chevron, name, items/behind count, and a roll-up bar of the whole group"""
    ind = TONES["indigo"]
    body = [f'<rect x="0" y="2" width="{c.W}" height="{h - 4}" rx="6" fill="{ind[1]}" stroke="{ind[2]}"/>']
    labels = [CHEV.format(x=name_x - 20, y=name_y - 9, c=ind[0])]
    n = len(ws)
    bad = sum(status(r, c.td)[1] in ("red", "amber") for r in ws)
    summ = f"{n} item{'s' if n != 1 else ''}" + (f" · {bad} behind" if bad else " · on track")
    ru = _rollup(ws, c.td)
    room = (c.x(ru[0]) if ru else c.W) - 10  # the summary must end before the roll-up bar starts
    sx = name_x + _tw(gr["group"].upper(), 11) + 14
    if c.L > 40 and sx + _tw(summ, 11) > min(room, c.L - 12):  # wide and no room on one line: stack name over summary
        labels.append(_t(name_x, name_y - 7, gr["group"].upper(), 11, ind[0], 800))
        labels.append(_t(name_x, name_y + 7, summ, 11, TONES["red"][0] if bad else MUT, 600))
    else:
        labels.append(_t(name_x, name_y, gr["group"].upper(), 11, ind[0], 800))
        labels.append(_t(sx, name_y, summ, 11, TONES["red"][0] if bad else MUT, 600))
    if ru:
        ps, pe, a0, a1, tn = ru
        body.append(f'<rect x="{c.x(ps):.1f}" y="{bar_y}" width="{max(c.x(pe) - c.x(ps), 4):.1f}" height="6" rx="3" fill="{CARD}" '
                    f'stroke="{ind[0]}" stroke-width="1.2" stroke-dasharray="4 3"><title>group plan</title></rect>')
        if a0 is not None:
            body.append(f'<rect x="{c.x(a0):.1f}" y="{bar_y + 8}" width="{max(c.x(a1) - c.x(a0), 4):.1f}" height="7" rx="3.5" '
                        f'fill="{TONES[tn][0]}"><title>group actual so far</title></rect>')
    return body + c.today_line(2, h - 2), labels


def _work_rows(c, ws, rh, wide):
    """the rows of one group, zebra-banded"""
    body, labels = [], []
    for i, r in enumerate(ws):
        ry = i * rh
        if i % 2:
            body.append(f'<rect x="0" y="{ry}" width="{c.W}" height="{rh}" fill="{BG}" opacity=".55"/>')
    body += c.grid(0, len(ws) * rh)
    for i, r in enumerate(ws):
        ry = i * rh
        body.append(f'<line x1="0" y1="{ry + rh:.1f}" x2="{c.W}" y2="{ry + rh:.1f}" stroke="{LINE}" stroke-width=".6"/>')
        words, tn = status(r, c.td)
        col = TONES[tn][0] if tn != "grey" else MUT
        if wide:
            labels.append(_t(28, ry + 21, r["label"], 13, INK, 700))
            if r.get("note"):
                labels.append(_t(28, ry + 38, r["note"], 11, MUT))
            body += _bars(c.x, r, ry + 10, ry + 25, c.td, c.hid)
            right, left = _row_end(c.x, r, c.td)
            if right + 12 + _tw(words, 11) <= c.W:
                labels.append(_t(right + 12, ry + 35, words, 11, col, 700))
            else:
                labels.append(_t(left - 10, ry + 35, words, 11, col, 700, "end"))
        else:
            labels.append(_t(c.L + 2, ry + 16, r["label"], 13, INK, 700))
            body += _bars(c.x, r, ry + 24, ry + 37, c.td, c.hid)
            labels.append(_t(c.L + 2, ry + 64, words, 11, col, 700))
    if wide:
        body.append(f'<line x1="{c.L - 8}" y1="0" x2="{c.L - 8}" y2="{len(ws) * rh}" stroke="{RULE}" stroke-width="1.5"/>')
    return body + c.today_line(0, len(ws) * rh), labels


def _assemble(c, title, head, foot, gh, rh, wide):
    """header, then per group a <details> (summary = group band, body = its rows), then the footer"""
    nx, ny, by = (28, 21, 12) if wide else (24, 17, 25)
    parts = [head]
    for gr, ws in _split(c.rs):
        if gr is None:
            b, lab = _work_rows(c, ws, rh, wide)
            parts.append(c.svg(len(ws) * rh, title + ": rows", b, lab))
            continue
        hb, hl = _group_head(c, gr, ws, gh, ny, by, nx)
        rows = ""
        if ws:
            b, lab = _work_rows(c, ws, rh, wide)
            rows = c.svg(len(ws) * rh, f'{title}: {gr["group"]}', b, lab)
        parts.append(f'<details class="gt-grp" open><summary>{c.svg(gh, gr["group"] + " (click to roll up or expand)", hb, hl)}</summary>{rows}</details>')
    parts.append(foot)
    return "".join(parts)


def _footer(c, y_today, key_y, note=None):
    body, labels = [f'<line x1="0" y1="0" x2="{c.W}" y2="0" stroke="{MUT}"/>'], []
    if c.td is not None:
        labels.append(_t(min(max(c.x(c.td), 20), c.W - 20), y_today, "today", 11, TONES["blue"][0], 700, "middle"))
    k, y = _key(key_y, KEY, c.hid, c.W)
    labels.append(k)
    y += 26
    if note:
        lab, txt, tn = note
        body.append(f'<rect x="0" y="{y}" width="{c.W}" height="34" rx="8" fill="{TONES[tn][1]}" stroke="{TONES[tn][2]}"/>')
        labels.append(f'<text x="16" y="{y + 21}" font-size="12" fill="{INK}"><tspan font-weight="800" fill="{TONES[tn][0]}">'
                      f'{E(lab)}</tspan> {E(txt)}</text>')
        y += 34
    return body, labels, y + 6


def gantt(title, rows, start, end, today=None, note=None, label_w=230):
    """Planned against actual, one row per piece of work, desktop width (920). Returns HTML (several aligned SVGs).

    rows, in display order:
      {"group": "Build"}                                              a group heading: click it to roll the group up
      {"label": "API", "note": "team B",                              one work row (note is optional)
       "plan": ("2026-03-02", "2026-03-09"),                          planned start/end (ISO date or datetime)
       "actual": ("2026-03-02", "2026-03-11") | ("2026-03-03", None) | None,   None end = in work; None = not started
       "gates": [("2026-03-09", "design review")], "flags": [("2026-03-11", "beta live")]}
    start/end: the date axis. today: draws the today line and sizes in-work bars.
    note: (label, body, tone) takeaway strip under the chart, ~120 characters.
    Each group band carries a roll-up bar (the group's whole plan, and its actual so far), so a rolled-up group still reads."""
    c = _Ctx(rows, start, end, today, W, label_w, 14, 64)
    top = 84
    hb = [f'<rect x="0" y="28" width="{W}" height="{top - 32}" rx="6" fill="{HEAD}"/>']
    hl = [f'<text x="0" y="16" font-size="15" font-weight="800" fill="{HEAD}">{E(title.upper())}</text>',
          _t(10, 50, "WORK", 11, CARD, 800), _t(10, 68, "click a group to roll it up", 11, HEAD_SUB)]
    for i, (m0, m1, name) in enumerate(c.months):
        if i:
            hb.append(f'<line x1="{c.x(m0):.1f}" y1="32" x2="{c.x(m0):.1f}" y2="{top}" stroke="{HEAD_SUB}" stroke-opacity=".45" stroke-width="1.5"/>')
        if c.x(m1) - c.x(m0) >= _tw(name, 11) + 12:
            hl.append(_t((c.x(m0) + c.x(m1)) / 2, 50, name, 11, CARD, 800, "middle"))
    for d, lab in c.ticks:
        if c.x(d) + _tw(lab, 11) / 2 <= W and c.x(d) - _tw(lab, 11) / 2 >= label_w - 30 and not lab[0].isalpha():
            hl.append(_t(c.x(d), 68, lab, 11, HEAD_SUB, anchor="middle"))
    hb += c.today_line(top - 4, top)
    head = c.svg(top, title + ": planned against actual", hb, hl)
    fb, fl, fh = _footer(c, 16, 34, note)
    foot = c.svg(fh, title + ": key", fb, fl)
    return _assemble(c, title, head, foot, 34, 50, True)


def gantt_phone(title, rows, start, end, today=None):
    """The same schedule for a ~390px screen: each row stacks its name, its bars, then its status in words."""
    c = _Ctx(rows, start, end, today, 360, 4, 8, 56)
    top = 52
    hb = [f'<rect x="0" y="24" width="{c.W}" height="{top - 26}" rx="6" fill="{HEAD}"/>']
    hl = [f'<text x="0" y="16" font-size="15" font-weight="800" fill="{HEAD}">{E(title.upper())}</text>']
    for d, lab in c.ticks:
        if c.x(d) + _tw(lab, 11) / 2 <= c.W and c.x(d) - _tw(lab, 11) / 2 >= 0:
            hl.append(_t(c.x(d), 42, lab, 11, CARD, 700, "middle"))
    head = c.svg(top, title + ": planned against actual", hb, hl)
    fb, fl, fh = _footer(c, 16, 34)
    foot = c.svg(fh, title + ": key", fb, fl)
    return _assemble(c, title, head, foot, 46, 70, False)


def gantt_block(title, rows, start, end, today=None, note=None):
    """Both drawings plus expand-all / roll-up-all buttons; CSS shows the wide one on desktop and the stacked one on phones."""
    tools = ('<div class="gt-tools"><button type="button" onclick="this.closest(\'.gt\').querySelectorAll(\'details\').forEach(d=>d.open=true)">'
             'Expand all</button><button type="button" onclick="this.closest(\'.gt\').querySelectorAll(\'details\').forEach(d=>d.open=false)">'
             'Roll up all</button></div>')
    return (f'<div class="gt">{tools}<div class="gt-wide">{gantt(title, rows, start, end, today, note)}</div>'
            f'<div class="gt-phone">{gantt_phone(title, rows, start, end, today)}</div></div>')


CSS = """
:root{--ink:#1B2029;--muted:#5B6472;--line:#D6DAE2;--card:#FFFFFF;--bg:#EDEFF3;--accent:#4A47A3}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Manrope,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:28px 20px 60px} h1{font-size:30px;margin:6px 0 4px;font-weight:800}
h2{font-size:19px;margin:34px 0 8px;font-weight:800} .sub{color:var(--muted);margin:0 0 16px}
.warn{background:#FFF1DC;border:1px solid #F0DDBB;border-radius:12px;padding:12px 16px}
.nav{font-size:13px;color:var(--muted);margin-bottom:14px} a{color:var(--accent)}
.fig{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
.figcap{font-size:12px;color:var(--muted);margin:10px 0 0}
.gt-phone{display:none} @media (max-width:640px){.gt-wide{display:none}.gt-phone{display:block}}
.gt svg{display:block} .gt details>summary{list-style:none;cursor:pointer} .gt details>summary::-webkit-details-marker{display:none}
.gt .gt-chev{transition:transform .15s;transform-box:fill-box;transform-origin:center}
.gt details:not([open]) .gt-chev{transform:rotate(-90deg)}
.gt-tools{display:flex;gap:8px;justify-content:flex-end;margin:0 0 6px}
.gt-tools button{font:600 12px Manrope,sans-serif;color:#1E3A8A;background:#E3ECFF;border:1px solid #C9D8FF;border-radius:6px;padding:4px 10px;cursor:pointer}
"""


def stamp():
    """The page timestamp. ALWAYS from the clock, never estimated."""
    return subprocess.check_output(["date", "-u", "+%Y-%m-%d · %H:%MZ"]).decode().strip()


def fig(inner, caption):
    return f'<div class="fig">{inner}<p class="figcap">{caption}</p></div>'


def page(title, subtitle_html, oneliner_html, sections, nav_links=()):
    """A standalone page. sections = [(h2_text, [html blocks...])]. Inside a vispage page, use its page() and add CSS above."""
    nav = " · ".join(f'<a href="{u}">{E(l)}</a>' for l, u in nav_links)
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1">'
           f'<title>{E(title)}</title>'
           '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
           f'<style>{CSS}</style></head><body><div class="wrap">',
           f'<div class="nav">&#8592; {nav}{" · " if nav else ""}Last updated: {stamp()}</div>',
           f'<h1>{E(title)}</h1><p class="sub">{subtitle_html}</p>',
           f'<div class="warn"><b>In one line:</b> {oneliner_html}</div>']
    for h, blocks in sections:
        out.append(f"<h2>{E(h)}</h2>")
        out.extend(blocks)
    out.append("</div></body></html>")
    return "\n".join(out)

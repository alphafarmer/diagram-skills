#!/usr/bin/env python3
"""render_check.py <page.html> [shots_dir]

Renders the page in headless Chrome at 1100px and 390px (phone). It FAILS (exit 1) on:
  - OVERFLOW: an SVG <text> extending outside its figure's viewBox
  - OVERLAP:  two <text> elements in the same SVG whose boxes intersect (labels colliding)
  - STAMP:    not exactly one "Last updated:" on the page
It writes shots_dir/figNN.png for every .fig (default ./shots). LOOK at them: the checker
catches geometry, not taste.

Meta-test: `render_check.py --selftest` seeds an overflowing label and an overlapping pair,
and must report both (exit 0 only if both are caught).
"""
import os, sys, tempfile

JS = r"""() => {
  const out = [];
  document.querySelectorAll('svg').forEach((s, si) => {
    const vb = s.viewBox.baseVal; if (!vb || !vb.width) return;
    const ts = [...s.querySelectorAll('text')].map(t => ({t, b: t.getBBox()})).filter(o => o.b.width > 0);
    ts.forEach(o => { if (o.b.x < -1 || o.b.x + o.b.width > vb.width + 1)
      out.push(`OVERFLOW fig-svg#${si}: "${o.t.textContent.slice(0,60)}" ends at ${Math.round(o.b.x+o.b.width)} > ${vb.width}`); });
    for (let i = 0; i < ts.length; i++) for (let j = i + 1; j < ts.length; j++) {
      const a = ts[i].b, b = ts[j].b;
      const ix = Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x);
      const iy = Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y);
      if (ix > 2 && iy > 3) out.push(`OVERLAP fig-svg#${si}: "${ts[i].t.textContent.slice(0,40)}" x "${ts[j].t.textContent.slice(0,40)}"`);
    }
  });
  const stamps = (document.body.innerText.match(/Last updated:/g) || []).length;
  if (stamps !== 1) out.push(`STAMP: found ${stamps} "Last updated:" (need exactly 1)`);
  return out;
}"""


def check(path, shots="shots"):
    from playwright.sync_api import sync_playwright
    os.makedirs(shots, exist_ok=True)
    exe = next((p for p in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser") if os.path.exists(p)), None)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        problems = []
        for width in (1100, 390):
            pg = b.new_page(viewport={"width": width, "height": 900})
            pg.goto("file://" + os.path.abspath(path)); pg.wait_for_timeout(1200)
            if width == 1100:
                figs = pg.query_selector_all(".fig")
                for i, f in enumerate(figs):
                    f.screenshot(path=os.path.join(shots, f"fig{i:02d}.png"))
                problems += pg.evaluate(JS)
            if pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1"):
                problems.append(f"HSCROLL at {width}px: page scrolls horizontally")
            pg.close()
        b.close()
    return problems, len(figs)


def selftest():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import vispage as v
    bad = v.svg(60, "t", "seeded", v.text(880, 40, "this label runs far past the right edge of the figure") +
                v.text(10, 40, "overlap A") + v.text(14, 42, "overlap B"))
    html = v.page("selftest", "", "", [("s", [v.fig(bad, "seeded faults")])])
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "t.html"); open(f, "w").write(html)
        probs, _ = check(f, os.path.join(d, "shots"))
    ok = any(p.startswith("OVERFLOW") for p in probs) and any(p.startswith("OVERLAP") for p in probs)
    print("SELFTEST", "PASS (seeded faults caught)" if ok else "FAIL — checker is decorative", probs)
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    probs, n = check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "shots")
    print(f"{n} figures rendered")
    for p in probs:
        print(" ", p)
    print("RENDER-CHECK", "FAIL" if probs else "PASS")
    sys.exit(1 if probs else 0)

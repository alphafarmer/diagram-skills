#!/usr/bin/env python3
"""/infog generator scaffold — copy, fill FACTS, pick archetypes. See SKILL.md for the method."""
import math, re

INK="#141821"; MUT="#4B5563"; BLUE="#1D4ED8"; GREEN="#0F7B33"; AMBER="#B45309"
RED="#B91C1C"; PURPLE="#6D28D9"; TEAL="#0E7490"; GOLD="#A16207"; GRAY="#6B7280"

SYMBOLS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-term" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M6 9l4 3-4 3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 2l8 3v6c0 5-3.5 8.5-8 11-4.5-2.5-8-6-8-11V5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M8.5 12l2.5 2.5 4.5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-scroll" viewBox="0 0 24 24"><path d="M6 3h12a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V5a2 2 0 012-2z" fill="none" stroke="currentColor" stroke-width="2"/><line x1="8" y1="8" x2="16" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="16" x2="13" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="i-spark" viewBox="0 0 24 24"><path d="M13 2L4 14h6l-1 8 9-12h-6z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></symbol>
<symbol id="i-db" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="8" ry="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" fill="none" stroke="currentColor" stroke-width="2"/></symbol>
<symbol id="i-gauge" viewBox="0 0 24 24"><path d="M4 17a8 8 0 1116 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="12" y1="17" x2="16" y2="10" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17" r="1.6" fill="currentColor"/></symbol>
<symbol id="i-prism" viewBox="0 0 24 24"><path d="M12 3L3 20h18z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><line x1="3" y1="12" x2="9.5" y2="12" stroke="currentColor" stroke-width="1.6"/><line x1="14" y1="10" x2="21" y2="7" stroke="currentColor" stroke-width="1.6"/><line x1="15" y1="13" x2="22" y2="13" stroke="currentColor" stroke-width="1.6"/><line x1="14" y1="16" x2="21" y2="19" stroke="currentColor" stroke-width="1.6"/></symbol>
<symbol id="i-funnel" viewBox="0 0 24 24"><path d="M3 4h18l-7 8v7l-4 2v-9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></symbol>
<symbol id="i-valve" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="2"/><line x1="12" y1="2" x2="12" y2="7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="12" y1="17" x2="12" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="9" y1="12" x2="15" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="i-lens" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><line x1="15" y1="15" x2="21" y2="21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></symbol>
<symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 10V7a4 4 0 018 0v3" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="15" r="1.6" fill="currentColor"/></symbol>
<symbol id="i-switch" viewBox="0 0 24 24"><circle cx="4" cy="18" r="2" fill="currentColor"/><circle cx="20" cy="18" r="2" fill="currentColor"/><line x1="6" y1="18" x2="11" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="11" y1="18" x2="18" y2="9" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></symbol>
<symbol id="i-flask" viewBox="0 0 24 24"><path d="M10 3h4M10 3v6l-6 10a2 2 0 001.8 3h12.4a2 2 0 001.8-3L14 9V3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="7.5" y1="15" x2="16.5" y2="15" stroke="currentColor" stroke-width="2"/></symbol>
<symbol id="i-brain" viewBox="0 0 24 24"><path d="M9 4a3 3 0 00-3 3 3 3 0 00-2 3c0 1 .4 1.9 1 2.5A3.5 3.5 0 006 19a3.5 3.5 0 006 1.5A3.5 3.5 0 0018 19a3.5 3.5 0 001-6.5c.6-.6 1-1.5 1-2.5a3 3 0 00-2-3 3 3 0 00-3-3 3 3 0 00-3 2 3 3 0 00-3-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 6v13" stroke="currentColor" stroke-width="1.6"/></symbol>
<symbol id="i-tag" viewBox="0 0 24 24"><path d="M3 12V4a1 1 0 011-1h8l9 9-9 9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="7.5" cy="7.5" r="1.6" fill="currentColor"/></symbol>
<symbol id="i-star" viewBox="0 0 24 24"><path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17l-6.1 3.6 1.4-6.8L2.2 9.1l6.9-.8z" fill="currentColor"/></symbol>
<symbol id="i-flag" viewBox="0 0 24 24"><line x1="5" y1="3" x2="5" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M5 4h13l-3 4 3 4H5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></symbol>
</defs></svg>'''

STYLE = """<style>
.ig{background:#fff;border:1px solid #CBD5E1;border-radius:16px;padding:20px 24px;margin:26px 0;box-shadow:0 2px 6px rgba(16,24,40,.09);overflow-x:auto}
.ig h2{margin:0 0 2px;border:none;padding:0;font-size:21px}
.ig .cap{color:#4B5563;font-size:13.5px;margin:0 0 12px}
.ig svg{min-width:1160px;display:block}
svg text{font-family:'Manrope',-apple-system,sans-serif}
.keys{columns:2;column-gap:34px;margin:14px 4px 2px;padding:0;list-style:none;font-size:13px;color:#2A2F37}
.keys li{margin:0 0 8px;padding-left:30px;text-indent:-30px;break-inside:avoid}
.keys .kn{display:inline-block;width:21px;height:21px;border-radius:50%;color:#fff;font-weight:800;font-size:12px;text-align:center;line-height:21px;margin-right:8px;text-indent:0}
.legendrow{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:#4B5563;margin-top:8px}
</style>"""

def icon(x,y,sym,color,r=21,ir=24):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<use href="#{sym}" x="{x-ir/2}" y="{y-ir/2}" width="{ir}" height="{ir}" color="#fff"/>')
def label(x,y,t,sub="",anchor="middle",fs=12.5):
    s=f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{fs}" font-weight="800" fill="{INK}">{t}</text>'
    if sub: s+=f'<text x="{x}" y="{y+15}" text-anchor="{anchor}" font-size="11" fill="{MUT}">{sub}</text>'
    return s
_mk=0
def defs():
    global _mk; _mk+=1
    return (f'<defs><marker id="m{_mk}" markerWidth="10" markerHeight="10" refX="7.5" refY="3.5" orient="auto">'
            f'<path d="M0,0 L8,3.5 L0,7 z" fill="{INK}"/></marker></defs>', _mk)
def flow(mk,pts,color=INK,w=3.5,dash="",marker=True):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    m=f' marker-end="url(#m{mk})"' if marker else ""
    path="M"+" L".join(f"{x},{y}" for x,y in pts)
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{d}{m}/>'
def wrap_words(txt,maxch):
    words=txt.split(" "); lines=[""]
    for w in words:
        if lines[-1] and len(lines[-1])+1+len(w)>maxch: lines.append(w)
        else: lines[-1]=(lines[-1]+" "+w).strip()
    return lines
class Col:
    """Collision-proof label column: fixed x, y-cursor. Use for any stacked annotations."""
    def __init__(self,x,y,maxch): self.x=x; self.y=y; self.maxch=maxch; self.out=[]
    def note(self,txt,col=RED,icon_="⚠",fs=11.5):
        for i,l in enumerate(wrap_words(txt,self.maxch)):
            fw=' font-weight="700"' if i==0 else ""
            pre=f"{icon_} " if i==0 else ""
            self.out.append(f'<text x="{self.x+(0 if i==0 else 14)}" y="{self.y}" font-size="{fs}"{fw} fill="{col}">{pre}{l}</text>')
            self.y+=15
        self.y+=7
    def svg(self): return "".join(self.out)
def key_html(items):
    return '<ol class="keys">'+"".join(
        f'<li><span class="kn" style="background:{c}">{n}</span>{t}</li>' for n,c,t in items)+'</ol>'
def donut_arc(cx,cy,r,w,f0,f1,color):
    a0=2*math.pi*f0-math.pi/2; a1=2*math.pi*f1-math.pi/2
    x0,y0=cx+r*math.cos(a0),cy+r*math.sin(a0); x1,y1=cx+r*math.cos(a1),cy+r*math.sin(a1)
    return f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {1 if (f1-f0)>0.5 else 0} 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'

# ==== FILL: fact-sheet constants, panels per SKILL.md archetypes, then assemble ====
# panel = newsvg-like list; finish each with key_html([...]) matching every on-canvas ①②③.
# Assemble: wrap the panels in your page's <head>/<body> (load Manrope); ONE "Last updated:" stamp max.

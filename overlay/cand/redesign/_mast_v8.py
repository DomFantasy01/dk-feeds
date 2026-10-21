# THE DISPATCH MASTHEAD v8 (Dom, Mon Oct 12 2026) - the approved Field Report masthead (prototype v7) on every page:
# navy band, two mountain ranges in fixed deep colors per league (never the league's own color), the title and logo, the
# section line, the data light, four dark glass buttons with the page's own lit in white. Also prints league names
# DK1-DK4 everywhere in the process. Exec'd by _fr_v8.py (league pages) and by global/_mast33.py (the front page).
import math as _m8, random as _r8, re as _re8, os as _os8, json as _j8, glob as _g8, datetime as _d8, sys as _s8
import pandas as _p8
from zoneinfo import ZoneInfo as _Z8
from reportlab.lib.colors import HexColor as _H8, Color as _C8
from reportlab.platypus import Paragraph as _PG8
from reportlab.lib.styles import ParagraphStyle as _PS8
from reportlab.pdfbase import pdfmetrics as _pm8
from reportlab.pdfbase.ttfonts import TTFont as _TT8
import reportlab.pdfgen.textobject as _rto8
if "MTR" not in globals():   # the front page runs in its own process: read the same meter file
    _mf8=sorted(__import__('glob').glob("/home/claude/dksys/data/latest/meter/meter_wk*.json"),key=lambda p:int(p.split("_wk")[1].split(".")[0]))[-1]
    MTR=__import__('json').load(open(_mf8)); WEEKN=MTR["week"]
if "asof_state" not in globals(): exec(open("/home/claude/cand/redesign/_asof.py").read(),globals())

# ---------------------------------------------------------------- league names: DK1-DK4, everywhere on the page
_DKRX = _re8.compile(r"\bDK (IV|III|II|I)\b"); _DKN = {"I": "1", "II": "2", "III": "3", "IV": "4"}
def dkname(s): return _re8.sub(r"\bDK ?([1-4])\b", lambda m: "DK " + {"1": "I", "2": "II", "3": "III", "4": "IV"}[m.group(1)], s) if isinstance(s, str) else s
if not getattr(_rto8.PDFTextObject, "_dk8", False):
    _fmt0 = _rto8.PDFTextObject._formatText
    def _fmt8(self, text): return _fmt0(self, dkname(text))
    _rto8.PDFTextObject._formatText = _fmt8; _rto8.PDFTextObject._dk8 = True

_GF8 = "/usr/share/fonts/truetype/google-fonts/"
for _n, _f in (("PopS", "Poppins-SemiBold"),):
    try: _pm8.getFont(_n)
    except Exception:
        try: _pm8.registerFont(_TT8(_n, _GF8 + _f + ".ttf"))
        except Exception: _pm8.registerFont(_TT8(_n, _GF8 + "Poppins-Bold.ttf"))
from reportlab.lib.fonts import addMapping as _am8
_am8("Pop", 0, 0, "Pop"); _am8("Pop", 1, 0, "PopB"); _am8("Pop", 0, 1, "Pop"); _am8("Pop", 1, 1, "PopB")

K8 = dict(INK=_H8("#14213D"), PAPER=_H8("#FBF7EF"), CARD=_H8("#FFFFFF"), LINE=_H8("#DDD5C5"), GR=_H8("#6B7180"), GR2=_H8("#A9ADB6"),
          GREEN=_H8("#1E9E4A"), GOLD=_H8("#E0A21B"), RED=_H8("#D63A2F"), BAND=_H8("#F6F1E7"), BAR=_H8("#EEF0F4"))
TEAMC8 = {"DK I": _H8("#2F80ED"), "DK II": _H8("#F2711C"), "DK III": _H8("#7B5CE0"), "DK IV": _H8("#2EC4B6")}   # the colors every Dispatch page wears (p12v10 + Oct 10 purple)
# the mountains are fixed decoration: deeper, punchier tones, never the league's own color (Dom, Oct 12)
_FOREST, _BURNT, _DGOLD = _H8("#1F6B43"), _H8("#C2481A"), _H8("#C98A12")
MTN8 = {None: (_DGOLD, _BURNT), "DK I": (_FOREST, _BURNT), "DK II": (_DGOLD, _FOREST), "DK III": (_FOREST, _BURNT), "DK IV": (_DGOLD, _BURNT)}
def _mx8(a, b, t): return _C8(a.red + (b.red - a.red) * t, a.green + (b.green - a.green) * t, a.blue + (b.blue - a.blue) * t)
def _al8(k, a): return _C8(k.red, k.green, k.blue, alpha=a)
def t8(x, y, s, f="Pop", sz=7, col=None, a="l"):
    c.setFont(f, sz); c.setFillColor(col or K8["INK"])
    (c.drawString if a == "l" else c.drawRightString if a == "r" else c.drawCentredString)(x, y, s)
def w8(s, f, sz): return c.stringWidth(dkname(s), f, sz)
def fit8(s, f, sz, wmax):
    while w8(s, f, sz) > wmax and len(s) > 4: s = s[:-2].rstrip(" ,;·") + "…"
    return s
def num8(v, d=1): return "—" if v is None or (isinstance(v, float) and v != v) else f"{v:.{d}f}"
def sgn8(d): return f"{'+' if d >= 0 else '−'}{abs(d):.1f}"
def sfx8(n): return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
def ln8(nm):
    p = [w for w in str(nm).split() if w not in ("Jr.", "Sr.", "II", "III", "IV", "Jr", "Sr")]; return p[-1] if p else str(nm)
def pill8(x, y, s, fill, col=None, f="PopB", sz=5.6, pad=4, stroke=None, r=2.6):
    w = w8(s, f, sz) + 2 * pad
    c.setFillColor(fill); c.setStrokeColor(stroke or fill); c.setLineWidth(.7)
    c.roundRect(x, y - 2.4, w, sz + 4.2, r, stroke=1 if stroke else 0, fill=1); t8(x + pad, y, s, f, sz, col or K8["CARD"]); return w
_PT8 = _Z8("America/Los_Angeles"); _ET8 = _Z8("America/New_York")
_MON8 = {1: "Jan.", 2: "Feb.", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "Aug.", 9: "Sept.", 10: "Oct.", 11: "Nov.", 12: "Dec."}
def _pt_txt8(s):
    """'Mon Oct 12 09:07 AM PT' -> 'Mon Oct. 12, 9:07 AM PT'"""
    m = _re8.search(r"(\w{3}) (\w{3}) (\d{1,2})\D+?(\d{1,2}):(\d{2}) ([AP]M)", str(s or ""))
    if not m: return str(s or "")
    mo = _d8.datetime.strptime(m.group(2), "%b").month
    return f"{m.group(1)} {_MON8[mo]} {int(m.group(3))}, {int(m.group(4))}:{m.group(5)} {m.group(6)} PT"

# ================================================================ THE MASTHEAD (every page)
def _ridge8(x0, x1, y0, bumps, jit, seed, sc):
    rr = _r8.Random(seed); pts = []; x = x0
    while x <= x1:
        t = (x - x0) / (x1 - x0)
        h = sum(a_ * _m8.exp(-((t - m_) / w_) ** 2) for a_, m_, w_ in bumps) * sc + jit * (rr.random() - .5)
        pts.append((x, y0 + max(0, h))); x += 3.2
    return pts
def _area8(pts, x0, x1, y0, fill, edge, lw):
    p = c.beginPath(); p.moveTo(x0, y0 - 1)
    for q in pts: p.lineTo(*q)
    p.lineTo(x1, y0 - 1); p.close(); c.setFillColor(fill); c.drawPath(p, stroke=0, fill=1)
    e = c.beginPath(); e.moveTo(*pts[0])
    for q in pts[1:]: e.lineTo(*q)
    c.setStrokeColor(edge); c.setLineWidth(lw); c.drawPath(e, stroke=1, fill=0)
MH8_TOP = Ht - 8; MH8_BOT = Ht - 84
def _sect8(section):
    s = dkname(section.replace("  ", " ")); lg = None
    m = _re8.search(r"\bDK (IV|III|II|I)\b", s)
    if m: lg = "DK " + m.group(1)
    parts = [p.strip() for p in s.split("·") if p.strip() and not _re8.fullmatch(r"DK (IV|III|II|I)|FANTASY FOOTBALL", p.strip())]
    words = " · ".join(p.title().replace("Post-Mortem", "Post-Mortem").replace("The Marks", "The Marks") for p in parts)
    up = s.upper(); lit = None
    for i, k in enumerate(("OVERVIEW", "CALL", "FIELD REPORT", "POSITIONS")):
        if up.startswith(k): lit = i
    if lit is None and (up.startswith("SCOUT") or "POST-MORTEM" in up): lit = 2
    return words, lg, lit
def masthead(c_, section, sub=""):
    """the v7 masthead: navy, two mountain ranges, title and logo, section line, the data light, four glass buttons"""
    global c
    c = c_
    words, lg, lit = _sect8(section)
    c.setFillColor(K8["PAPER"]); c.rect(0, 0, W, Ht, stroke=0, fill=1)
    x0b, x1b, yb, hb = M, W - M, MH8_BOT, MH8_TOP - MH8_BOT
    c.saveState(); p = c.beginPath(); p.roundRect(x0b, yb, x1b - x0b, hb, 9); c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(K8["INK"]); c.rect(x0b, yb, x1b - x0b, hb, stroke=0, fill=1)
    rs = _r8.Random(11)
    for i in range(34):
        sx, sy = x0b + 160 + rs.random() * (x1b - x0b - 180), yb + hb * .62 + rs.random() * hb * .36
        c.setFillColor(_C8(1, 1, 1, alpha=.2 + .5 * rs.random())); c.circle(sx, sy, .4 + .5 * rs.random(), stroke=0, fill=1)
    back, front = MTN8.get(lg, MTN8[None]); mx0, mx1 = x0b + 196, x1b + 4; sc = hb / 80
    r2 = _ridge8(mx0, mx1, yb, ((16, .20, .09), (14, .48, .10), (48, .78, .10), (40, .98, .06)), 4, 5, sc)
    r1 = _ridge8(mx0, mx1, yb, ((20, .08, .08), (26, .33, .10), (10, .55, .08), (62, .84, .08), (30, .99, .05)), 5, 7, sc)
    _area8(r2, mx0, mx1, yb, _al8(back, .80), _mx8(back, K8["CARD"], .30), 1)
    _area8(r1, mx0, mx1, yb, _al8(front, .92), _mx8(front, K8["CARD"], .38), 1.3)
    for pts in (r1, r2):
        pk = max(pts, key=lambda q: q[1]); c.setFillColor(K8["CARD"]); c.circle(pk[0], pk[1], 1.7, stroke=0, fill=1)
    c.restoreState()
    t8(x0b + 14, yb + 45, "DARK KNIGHT DISPATCH", "Bebas", 32, K8["CARD"])
    if "dk_icon" not in globals(): exec(open("/home/claude/cand/redesign/_dkicon.py").read(), globals())
    dk_icon(c, x0b + 14 + c.stringWidth("DARK KNIGHT DISPATCH", "Bebas", 32) + 8, yb + 42.5, 27)
    sx = x0b + 14; t8(sx, yb + 23, words or "Dispatch", "Bebas", 18, K8["CARD"]); sx += w8(words or "Dispatch", "Bebas", 18) + 7
    if lg:
        tc = TEAMC8[lg]; c.setFillColor(tc); c.circle(sx + 2, yb + 29, 2.2, stroke=0, fill=1); sx += 10
        t8(sx, yb + 23, dkname(lg), "Bebas", 18, tc); sx += w8(dkname(lg), "Bebas", 18) + 10
    bx0 = x1b - 8 - 2 * 84 - 6
    sub2 = _re8.sub(r"\s*·?\s*As of [^·]*", "", sub or "").strip(" ·")   # the data light carries the time
    if WEEKN and not sub2.startswith("Week"): sub2 = f"Week {WEEKN}" + (f"  ·  {sub2}" if sub2 else "")
    t8(sx, yb + 24.5, fit8(sub2, "PopM", 6.8, bx0 - sx - 8), "PopM", 6.8, _H8("#C9CFDB"))
    # the data light: three lamps, the lit one is how fresh the oldest source is; the time is Yahoo's read
    try: _, light, _, _ = asof_state()
    except Exception: light = "amber"
    lx, ly = x0b + 14, yb + 8
    for i, (k, col) in enumerate((("red", K8["RED"]), ("amber", K8["GOLD"]), ("green", K8["GREEN"]))):
        c.setFillColor(col if k == light else _C8(1, 1, 1, alpha=.18)); c.circle(lx + 4 + i * 11, ly + 2.4, 3.5, stroke=0, fill=1)
    yr = MTR["sources"].get("yahoo_matchups", {}).get("pulled_pt")
    t8(lx + 36, ly, "Data  ·  " + (_pt_txt8(yr) if yr else "no Yahoo read"), "PopM", 6.6, K8["CARD"])
    for nm, i, j, k in (("Overview", 0, 1, 0), ("Calls", 1, 1, 1), ("Field", 0, 0, 2), ("Positions", 1, 0, 3)):
        tx, ty = bx0 + i * 90, yb + 9 + j * 30; on = (k == lit)
        c.setFillColor(_C8(.04, .06, .12, alpha=.70) if not on else _C8(.10, .12, .20, alpha=.74))
        c.setStrokeColor(_C8(1, 1, 1, alpha=1 if on else .5)); c.setLineWidth(1.8 if on else .8)
        c.roundRect(tx, ty, 84, 24, 6, stroke=1, fill=1)
        t8(tx + 42, ty + 8, nm.upper(), "Bebas", 13, K8["CARD"], "c")
    c.setFillColor(TEAMC8[lg] if lg else _H8("#F7B32B")); c.rect(x0b, yb - 5, x1b - x0b, 2.2, stroke=0, fill=1)
    _u = dkname(section).upper()
    _dy = (-4 if "FIELD REPORT" in _u else -2 if _u.startswith("SCOUT") else 10 if _u.startswith("POSITIONS") else 11 if "CALIBRATION" in _u
           else 10 if "THE MARKS" in _u else -7 if _u.startswith("OUTLOOK") else 0)
    if _dy: c.translate(0, _dy)   # Oct 12: every page starts 12 pt under the masthead


# OCT12 roman league names

# OCT12 even masthead gap

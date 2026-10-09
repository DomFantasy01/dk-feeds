# THE RADAR v3 — pages (Oct 8 2026). Reads data/latest/radar/radar_wk<W>.json and draws, per league, the three Radar
# jobs: the roster's men in the news, men COMING IN, and the opponent watch — plus a source page that says how old each
# source is and what failed. Dispatch palette and type; square corners; one decimal; every number says whose it is.
import json, glob, os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor as H
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT = os.environ.get('DK_ROOT', '/home/claude')
GF = os.environ.get('DK_GFONTS', '/usr/share/fonts/truetype/google-fonts') + '/'
pdfmetrics.registerFont(TTFont('Bebas', f'{ROOT}/cand/fonts/BebasNeue-Regular.ttf'))
for n, f in (('Pop', 'Poppins-Regular'), ('PopM', 'Poppins-Medium'), ('PopB', 'Poppins-Bold')): pdfmetrics.registerFont(TTFont(n, GF + f + '.ttf'))
BG = H('#0E1628'); BG2 = H('#16213A'); TXT = H('#EEF1F6'); GR = H('#8C94A6'); GR2 = H('#5E6679'); GRID = H('#2A3654'); GOLD = H('#EFD23E')
LC = {'DK I': H('#5B9BF5'), 'DK II': H('#F0763A'), 'DK III': H('#A98BFF'), 'DK IV': H('#4FD6CA')}
MC = {'red': H('#FF5A5F'), 'gold': H('#EFD23E'), 'green': H('#4FD08A'), 'grey': H('#7C8496')}
GC = {'bad': MC['red'], 'caution': MC['gold'], 'good': MC['green'], 'note': MC['grey'], 'opening': MC['gold']}
W, Ht = 612, 792; M = 30
F = sorted(glob.glob(f'{ROOT}/dksys/data/latest/radar/radar_wk*.json'), key=os.path.getmtime)[-1]
R = json.load(open(F)); WK = R['week']
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{ROOT}/dksys/data/latest/radar/DK_Radar_Wk{WK}.pdf'
c = canvas.Canvas(OUT, pagesize=(W, Ht)); c.setTitle(f'The Radar — Week {WK}')

def txt(x, y, s, font='Pop', size=8, col=TXT, align='l'):
    c.setFillColor(col); c.setFont(font, size)
    (c.drawString if align == 'l' else c.drawRightString if align == 'r' else c.drawCentredString)(x, y, s)
def fit(s, font, size, w):
    while s and pdfmetrics.stringWidth(s, font, size) > w: s = s[:-2].rstrip() + '…' if not s.endswith('…') else s[:-2] + '…'
    return s
def wrap(s, font, size, w, lines=2):
    out, cur = [], ''
    for word in s.split():
        t = (cur + ' ' + word).strip()
        if pdfmetrics.stringWidth(t, font, size) <= w: cur = t
        else:
            out.append(cur); cur = word
            if len(out) == lines: break
    if len(out) < lines and cur: out.append(cur)
    if len(out) == lines and ' '.join(out) != s.strip(): out[-1] = fit(out[-1] + ' …', font, size, w)
    return out
def page_bg():
    c.setFillColor(BG); c.rect(0, 0, W, Ht, stroke=0, fill=1)
def head(title, sub, col):
    c.setFillColor(BG2); c.rect(M, Ht - 74, W - 2 * M, 48, stroke=0, fill=1)
    c.setFillColor(col); c.rect(M, Ht - 74, W - 2 * M, 3, stroke=0, fill=1)
    txt(M + 12, Ht - 50, title, 'Bebas', 26, TXT); txt(W - M - 12, Ht - 46, f'THE RADAR · WEEK {WK}', 'Bebas', 13, GOLD, 'r')
    txt(M + 12, Ht - 66, sub, 'Pop', 7.2, GR); txt(W - M - 12, Ht - 66, f"built {R['built']}", 'Pop', 7.2, GR, 'r')
def marker(x, y, mk):
    """the Radar marker: dot + two arcs, colour = the news; left number = items on the newest news day, then the
    days since that day (0 = today). Digits never shrink — the pill widens to fit."""
    col = MC.get(mk['color'], MC['grey'])
    c.setStrokeColor(col); c.setFillColor(col); c.circle(x + 4, y + 3, 1.8, stroke=0, fill=1)
    c.setLineWidth(.9)
    for r in (3.6, 5.6): c.arc(x + 4 - r, y + 3 - r, x + 4 + r, y + 3 + r, -50, 100)
    lab = f"{mk['count']}·{mk['recency']}d" if mk.get('recency') is not None else f"{mk['count']}"
    wpx = pdfmetrics.stringWidth(lab, 'PopB', 7) + 6
    c.setFillColor(BG); c.setStrokeColor(col); c.setLineWidth(.8); c.rect(x + 12, y - 1.5, wpx, 10, stroke=1, fill=1)
    txt(x + 15, y + 1, lab, 'PopB', 7, col)
    return 12 + wpx
def numcells(x, y, r, keys=(('yahoo', 'YAHOO'), ('gotham', 'GOTHAM'), ('sleeper', 'SLEEPER'))):
    for i, (k, lab) in enumerate(keys):
        v = r.get(k); s = '—' if v is None else f'{v:.1f}'
        txt(x + i * 44 + 40, y, s, 'PopB', 8, TXT if v is not None else GR2, 'r')
def colhead(y, x0, cols):
    for x, s, al in cols: txt(x, y, s, 'PopB', 6, GR, al)
    c.setStrokeColor(GRID); c.setLineWidth(.5); c.line(x0, y - 3, W - M, y - 3)

# ---------------------------------------------------------------- page 1: sources and alarms
page_bg(); head('THE RADAR', 'Live news, injury report, Sleeper trending and Yahoo rosters — what changed, per league. It flags; it does not decide.', GOLD)
y = Ht - 100
txt(M, y, 'SOURCES — WHAT WAS PULLED AND HOW OLD IT IS', 'Bebas', 14, GOLD); y -= 16
colhead(y, M, [(M, 'SOURCE', 'l'), (M + 190, 'PULLED', 'l'), (M + 340, 'ITEMS', 'r'), (M + 360, 'NEWEST ITEM', 'l'), (W - M, 'STATE', 'r')]); y -= 14
for k, s in R['sources'].items():
    bad = s.get('failed') or s.get('warn')
    txt(M, y, s['label'], 'PopM', 7.8, TXT)
    txt(M + 190, y, f"{s.get('pulled') or '—'}" + (f"  ({s['pulled_ago']})" if s.get('pulled_ago') else ''), 'Pop', 7, GR)
    txt(M + 340, y, str(s.get('items', '')), 'Pop', 7, GR, 'r'); txt(M + 360, y, s.get('newest') or '—', 'Pop', 7, GR)
    txt(W - M, y, 'FAILED' if s.get('failed') else 'CHECK' if s.get('warn') else 'OK', 'PopB', 7, MC['red'] if s.get('failed') else MC['gold'] if s.get('warn') else MC['green'], 'r')
    y -= 13
y -= 8; txt(M, y, 'ALARMS', 'Bebas', 14, MC['red'] if R['alarms'] else MC['green']); y -= 14
for a in R['alarms'] or ['None — every source answered and is fresh.']:
    for ln in wrap(a, 'PopM', 7.6, W - 2 * M - 14, 2):
        txt(M + 10, y, ln, 'PopM', 7.6, MC['red'] if R['alarms'] else MC['green']); y -= 11
    y -= 2
y -= 10; txt(M, y, 'HOW TO READ IT', 'Bebas', 14, GOLD); y -= 14
rules = [
    'Three jobs per league: the roster’s own men in the news (every grade), men COMING IN (free in that league with good news, an opening, or heavy Sleeper add-trending), and OPPONENT WATCH (this week’s opponent’s starters in the news).',
    'The marker: dot and arcs, colour = the news — red needs action, gold watch, green good, grey gone quiet. The pill reads items on the newest news day · days since that day (0d = today). Grey after 2 quiet days, off after 7.',
    'Numbers are this week, each labelled with its owner: YAHOO (Yahoo’s projection), GOTHAM (the engine), SLEEPER (Sleeper’s projection, priced in that league’s scoring). “Weakest starter” is the lowest GOTHAM number among that league’s starters at the same position.',
    'An OPENING means the man ahead of him on his NFL team has bad or questionable news in the last three days — the value may move before any report says so.',
    'Roundups and listicles that name dozens of players count as mentions, not news, and never light a marker. News window: since the feed began Oct 7 (14 days once it fills).',
    'Free-agent status comes from Yahoo, read in Chrome; every COMING IN man was re-checked one by one with Yahoo’s player search. “Waivers” means he clears on the date Yahoo shows.']
for r in rules:
    for ln in wrap(r, 'Pop', 7.4, W - 2 * M - 14, 3): txt(M + 10, y, ln, 'Pop', 7.4, TXT); y -= 10.5
    y -= 4
c.showPage()

# ---------------------------------------------------------------- a page per league
for lab, L in R['leagues'].items():
    col = LC[lab]; page_bg()
    head(f'{lab} · THE RADAR', f"{L['key']} · opponent this week: {L['opponent']}" + (f" · unread team pages: {', '.join(str(t) for t in L['unread'])}" if L['unread'] else ''), col)
    y = Ht - 96
    # --- COMING IN
    txt(M, y, 'COMING IN — AVAILABLE IN THIS LEAGUE', 'Bebas', 14, col); txt(W - M, y, 'sorted: beats a starter first, then best number', 'Pop', 6.5, GR, 'r'); y -= 14
    colhead(y, M, [(M + 2, 'PLAYER', 'l'), (M + 150, 'HOW', 'l'), (M + 236, 'YAHOO', 'r'), (M + 280, 'GOTHAM', 'r'), (M + 324, 'SLEEPER', 'r'), (M + 334, 'WHY HE IS HERE', 'l')]); y -= 13
    for r in L['in'][:10]:
        if r['beats_floor']:
            c.setFillColor(col); c.rect(M - 6, y - 3, 3, 11, stroke=0, fill=1)
        txt(M + 2, y, fit(f"{r['name']}", 'PopB', 8, 104), 'PopB', 8, TXT); txt(M + 108, y, f"{r['pos']} {r['team']}", 'Pop', 7, GR)
        acq = r.get('acq', 'unverified'); txt(M + 150, y, acq.upper() if acq != 'free agent' else 'FREE AGENT', 'PopB', 6.2, MC['green'] if acq == 'free agent' else MC['gold'])
        numcells(M + 196, y, r)
        why = '; '.join(r['why'])
        fl = r.get('floor'); flt = f" · weakest {r['pos']} starter: {fl['name'].split()[-1]} {fl['gotham']:.1f} GOTHAM" if fl else ''
        lines = wrap(why + flt, 'Pop', 6.6, W - M - (M + 334), 2)
        for i, ln in enumerate(lines): txt(M + 334, y - i * 8.5, ln, 'Pop', 6.6, TXT if i == 0 else GR)
        y -= 8.5 * max(1, len(lines)) + 6
    if not L['in']: txt(M + 2, y, 'Nobody free in this league has news worth raising.', 'Pop', 7.5, GR); y -= 14
    txt(M - 4, y, '▌ beats the weakest starter at his position on at least one number', 'Pop', 6.2, col); y -= 18
    # --- OWN
    txt(M, y, f'{lab} — IN THE NEWS', 'Bebas', 14, col); y -= 14
    colhead(y, M, [(M + 62, 'PLAYER', 'l'), (M + 196, 'SLOT', 'l'), (M + 236, 'NEWEST', 'l')]); y -= 13
    shown = [r for r in L['own'] if r['marker']['color'] != 'grey'] + [r for r in L['own'] if r['marker']['color'] == 'grey']
    for r in shown[:12]:
        if y < 150: break
        marker(M, y, r['marker'])
        txt(M + 62, y, fit(r['name'], 'PopB', 8, 96), 'PopB', 8, TXT); txt(M + 160, y, r['pos'], 'Pop', 7, GR); txt(M + 196, y, r.get('slot') or '', 'Pop', 7, GR)
        n = r['news'][0] if r['news'] else None
        if n:
            g = n['grade']; txt(M + 236, y, g.upper(), 'PopB', 6, GC.get(g, GR))
            ln = wrap(f"{n['title']} — {n['src']}, {n['t'] if isinstance(n['t'], str) else ''}", 'Pop', 6.6, W - M - (M + 268), 2)
            for i, s in enumerate(ln): txt(M + 268, y - i * 8.5, s, 'Pop', 6.6, TXT if i == 0 else GR)
            y -= 8.5 * max(1, len(ln)) + 5
        else: y -= 13
    if not L['own']: txt(M + 2, y, 'Nothing on this roster carries news.', 'Pop', 7.5, GR); y -= 14
    y -= 8
    # --- OPPONENT
    txt(M, y, f"OPPONENT WATCH — {L['opponent'].upper()}", 'Bebas', 14, col); y -= 14
    for r in L['opp'][:6]:
        if y < 50: break
        marker(M, y, r['marker']); txt(M + 62, y, fit(r['name'], 'PopB', 8, 96), 'PopB', 8, TXT); txt(M + 160, y, r['pos'], 'Pop', 7, GR)
        n = r['news'][0]; ln = wrap(f"{n['title']} — {n['src']}", 'Pop', 6.6, W - M - (M + 196), 1)
        txt(M + 196, y, ln[0] if ln else '', 'Pop', 6.6, TXT); y -= 13
    if not L['opp']: txt(M + 2, y, 'No news on the opponent’s starters.', 'Pop', 7.5, GR)
    txt(W / 2, 18, f"Sources and ages on page 1 · built {R['built']}", 'Pop', 6.2, GR2, 'c')
    c.showPage()
c.save(); print('RADAR PAGES', OUT)

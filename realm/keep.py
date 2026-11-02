import base64
import datetime
import json
import math
import os
import random
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "images" / "keep"
USER = "IndrajeethY"

COL = {
    "g": "#c2a565", "g2": "#d8b971", "c": "#e6e0cf", "c2": "#cfc6ae", "m": "#8fa3c8", "md": "#55627e",
    "r": "#a8452f", "w": "#ffb347", "w2": "#e8902f", "wd": "#9a7850", "wb": "#6e5438", "wn": "#574230", "pn": "#3b3529",
    "s1": "#b3b7bf", "s2": "#868a93", "s3": "#585b63", "mo": "#6f8a5a", "gr": "#3f5537", "dk": "#24262c", "rv": "#1b1f2c", "rim": "#3a4258", "wing": "#262c3d", "eye": "#c9b27a",
}

REPOS = [
    ("svbackup", "Keeper of the Vaults", "Server and Postgres backups to local disk and Google Drive.", "Go", 1),
    ("Arch-Portifolio", "The Architect's Gallery", "A portfolio of the realm, built in TypeScript.", "TypeScript", 2),
    ("WhatChatGPT", "The Whispering Oracle", "WhatsApp chatbot that answers through OpenAI.", "Go", 35),
    ("TgStoryDl", "Thief of Stories", "Telegram bot that downloads stories from users.", "Python", 16),
    ("Nova", "The Nova Familiar", "Modular Telegram userbot written in Go with gogram.", "Go", 7),
    ("Yml-AutoFormatter", "Scribe of YAML", "Format, validate and auto-fix YAML syntax instantly.", "TypeScript", 2),
]

STACK = ["Go", "Python", "TypeScript", "Docker", "Postgres", "Redis", "Linux", "Git"]

RAVENS = [("telegram", "➤", "Telegram"), ("twitter", "✕", "X / Twitter"), ("instagram", "◎", "Instagram"),
          ("mail", "✉", "Mail"), ("website", "☾", "indrajeeth.in")]

CHAPTERS = ["THE GATE", "THE SCROLL", "THE EMA WALL", "THE LANTERN ROW", "THE DRAGON'S FLIGHT"]
CHAPTER_NAMES = ["The Gate", "The Scroll", "The Ema Wall", "The Lantern Row", "The Dragon's Flight"]
ROMAN = ["I", "II", "III", "IV", "V"]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def b64(p):
    return base64.b64encode((HERE / "fonts" / p).read_bytes()).decode()


FACES = {
    "mono": "@font-face{font-family:'KeepMono';src:url(data:font/woff2;base64,%s) format('woff2');}" % b64("jbmono.woff2"),
    "monob": "@font-face{font-family:'KeepMono';font-weight:700;src:url(data:font/woff2;base64,%s) format('woff2');}" % b64("jbmono-bold.woff2"),
    "sym": "@font-face{font-family:'KeepSym';src:url(data:font/woff2;base64,%s) format('woff2');}" % b64("freesym.woff2"),
    "title": "@font-face{font-family:'KeepTitle';src:url(data:font/woff2;base64,%s) format('woff2');}" % b64("shippori.woff2"),
    "italic": "@font-face{font-family:'KeepItalic';font-style:italic;src:url(data:font/woff2;base64,%s) format('woff2');}" % b64("cormorant-italic.woff2"),
    "plex": "@font-face{font-family:'KeepPlex';src:url(data:font/woff2;base64,%s) format('woff2');}" % b64("plexmono.woff2"),
}
BASE_CSS = (
    "text{font-family:'KeepMono','KeepSym',ui-monospace,Menlo,monospace;white-space:pre;text-rendering:geometricPrecision;}"
    ".b{font-weight:700;}"
    ".tt{font-family:'KeepTitle','Cormorant Garamond',Georgia,serif;}"
    ".it{font-family:'KeepItalic','Cormorant Garamond',Georgia,serif;font-style:italic;}"
    ".px{font-family:'KeepPlex','KeepSym',ui-monospace,monospace;}"
)
METRICS = json.loads((HERE / "fonts" / "metrics.json").read_text())


def measure(t, size, kind):
    m = METRICS[kind]
    return sum(m.get(ch, 0.5) for ch in t) * size


REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important;}}"
CLS_CSS = "".join(f".{k}{{fill:{v};}}" for k, v in COL.items())


def svg(w, h, body, css="", title="", defs="", fonts=("mono", "monob", "sym")):
    glow = ('<radialGradient id="atmo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#2a3a68" stop-opacity=".26"/>'
            '<stop offset=".6" stop-color="#1c2748" stop-opacity=".1"/><stop offset="1" stop-color="#121a33" stop-opacity="0"/></radialGradient>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title><defs>{glow}{defs}</defs>"
        f"<style>{''.join(FACES[f] for f in fonts)}{BASE_CSS}{CLS_CSS}{css}{REDUCED}</style>{body}</svg>\n"
    )


class Grid:
    def __init__(self, cols, rows, F, x0=0, y0=0):
        self.cols, self.rows, self.F = cols, rows, F
        self.cw, self.lh = F * 0.6, F * 1.32
        self.x0, self.y0 = x0, y0
        self.cells = [[(" ", None)] * cols for _ in range(rows)]

    def put(self, r, c, ch, cls):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.cells[r][c] = (ch, cls)

    def text(self, r, c, s, cls):
        for i, ch in enumerate(s):
            self.put(r, c + i, ch, cls)

    def center(self, r, s, cls, c0=0, c1=None):
        c1 = self.cols if c1 is None else c1
        self.text(r, c0 + (c1 - c0 - len(s)) // 2, s, cls)
        return c0 + (c1 - c0 - len(s)) // 2

    def get(self, r, c):
        return self.cells[r][c][0] if 0 <= r < self.rows and 0 <= c < self.cols else None

    def x(self, c):
        return self.x0 + c * self.cw

    def y(self, r):
        return self.y0 + r * self.lh + self.F * 1.02

    def row_svg(self, r, extra=""):
        spans, cur, buf = [], None, ""
        for ch, cls in self.cells[r] + [("", "__end")]:
            if cls != cur:
                if buf:
                    if buf.strip() and cur:
                        spans.append(f'<tspan class="{cur}">{esc(buf)}</tspan>')
                    else:
                        spans.append(esc(buf))
                buf, cur = "", cls
            buf += ch
        body = "".join(spans).rstrip()
        if not body.strip():
            return ""
        return f'<text x="{self.x0:.2f}" y="{self.y(r):.2f}" font-size="{self.F}"{extra}>{body}</text>'

    def svg(self, r0=0, r1=None):
        r1 = self.rows if r1 is None else r1
        return "".join(self.row_svg(r) for r in range(r0, r1))

    def ov(self, r, c, s, cls, attrs=""):
        return f'<text x="{self.x0:.2f}" y="{self.y(r):.2f}" font-size="{self.F}" class="{cls}"{attrs}>{" " * c}{esc(s)}</text>'


def noise(g, r0, r1, c0, c1, cls, density, rnd, chars=".·:'`,"):
    for r in range(r0, r1):
        for c in range(c0, c1):
            if g.get(r, c) == " " and rnd.random() < density:
                g.put(r, c, rnd.choice(chars), cls)


def gh(token, query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "bearer " + token, "User-Agent": "keep"},
    )
    return json.load(urllib.request.urlopen(req, timeout=30))["data"]


def fetch(token):
    repo_q = "".join(
        f'r{i}: repository(owner:"{USER}", name:"{n}"){{stargazerCount primaryLanguage{{name}}}}'
        for i, (n, *_rest) in enumerate(REPOS)
    )
    q = f"""{{user(login:"{USER}"){{followers{{totalCount}}
      contributionsCollection{{totalCommitContributions totalPullRequestReviewContributions contributionCalendar{{totalContributions}}}}
      pullRequests{{totalCount}} issues{{totalCount}}
      repositories(first:100,ownerAffiliations:OWNER,privacy:PUBLIC){{totalCount nodes{{stargazerCount}}}}}}
      {repo_q}}}"""
    d = gh(token, q)
    u = d["user"]
    cc = u["contributionsCollection"]
    stats = {
        "commits": cc["totalCommitContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "xp": cc["contributionCalendar"]["totalContributions"],
        "prs": u["pullRequests"]["totalCount"],
        "issues": u["issues"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "repos": u["repositories"]["totalCount"],
    }
    repos = []
    for i, (name, title, desc, lang, stars) in enumerate(REPOS):
        r = d.get(f"r{i}") or {}
        repos.append((name, title, desc, (r.get("primaryLanguage") or {}).get("name") or lang, r.get("stargazerCount", stars)))
    return stats, repos


def rank(s):
    exp = lambda x: 1 - 2 ** -x
    logn = lambda x: x / (1 + x)
    parts = [
        (2, exp(s["commits"] / 250)), (3, exp(s["prs"] / 50)), (1, exp(s["issues"] / 25)),
        (1, exp(s["reviews"] / 2)), (4, logn(s["stars"] / 50)), (1, logn(s["followers"] / 10)),
    ]
    score = sum(w * v for w, v in parts) / sum(w for w, _ in parts)
    pct = (1 - score) * 100
    levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]
    th = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    return levels[next(i for i, t in enumerate(th) if pct <= t)], pct


def chapter(i):
    W, H, F = 1100, 64, 17
    g = Grid(int(W / (F * 0.6)), 1, F)
    cols = g.cols
    g.x0 = (W - cols * g.cw) / 2
    g.y0 = (H - g.lh) / 2
    title = CHAPTERS[i]
    TS = 22
    tw_px = measure(f"{ROMAN[i]} · {title}", TS, "title") + len(f"{ROMAN[i]} · {title}") * TS * 0.18
    mid_cols = math.ceil((tw_px + 2 * 3 * g.cw + 2 * g.cw) / g.cw)
    mid = " " * mid_cols
    lw = (cols - len(mid) - 2) // 2 - 2
    left = "".join("┈" if k < lw * 0.3 else "─" if k < lw * 0.62 else "═" for k in range(lw))
    right = "".join("═" if k < lw * 0.38 else "─" if k < lw * 0.7 else "┈" for k in range(lw))
    pad = (cols - (lw * 2 + len(mid) + 4)) // 2
    css = """
.ch{animation:open 1.6s .2s cubic-bezier(.3,.7,.2,1) both;}
@keyframes open{from{clip-path:inset(0 50% 0 50%);}to{clip-path:inset(0 0 0 0);}}
"""
    defs = (
        f'<linearGradient id="shim" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{COL["g"]}"/><stop offset=".5" stop-color="#f3e2b0"/><stop offset="1" stop-color="{COL["g"]}"/>'
        f'<animate attributeName="x1" values="-300;1400" dur="7s" begin="2s" repeatCount="indefinite"/>'
        f'<animate attributeName="x2" values="0;1700" dur="7s" begin="2s" repeatCount="indefinite"/></linearGradient>'
    )
    lpx = g.x0 + (pad + lw + 2) * g.cw
    rpx = lpx + len(mid) * g.cw
    line = (
        f'<text x="{g.x0:.2f}" y="{g.y(0):.2f}" font-size="{F}" class="ch">{" " * pad}'
        f'<tspan fill="url(#shim)">{esc(left)}</tspan>  <tspan class="g2">✦</tspan>{" " * (len(mid) - 2)}<tspan class="g2">✦</tspan>  '
        f'<tspan fill="url(#shim)">{esc(right)}</tspan></text>'
        f'<text x="{g.x0 + (pad + lw + 2 + 0.5 + (len(mid) - 1) / 2) * g.cw + TS * 0.09:.2f}" y="{g.y(0) + 1:.2f}" font-size="{TS}" text-anchor="middle" letter-spacing="{TS * 0.18:.1f}" class="tt ch">'
        f'<tspan class="g2">{ROMAN[i]}</tspan><tspan class="md"> · </tspan><tspan class="c">{esc(title)}</tspan></text>'
    )
    body = f'<ellipse cx="{W / 2}" cy="{H / 2}" rx="430" ry="26" fill="url(#atmo)"/>' + line
    return svg(W, H, body, css, f"Chapter {ROMAN[i]}: {CHAPTER_NAMES[i]}", defs, ("mono", "monob", "sym", "title"))


def bar_str(n, total):
    if n <= 0:
        return ""
    if n <= 3:
        return "╸╴·"[3 - n:] if n < 3 else "━╸╴"
    return "━" * (n - 3) + "╸╴·"


def scroll(s):
    W, F = 1100, 15
    rnd = random.Random(4)
    lvl, pct = rank(s)
    rows = [("Commits this year", s["commits"]), ("Pull requests", s["prs"]), ("Issues raised", s["issues"]),
            ("Public repos", s["repos"]), ("Stars earned", s["stars"]), ("Followers", s["followers"])]
    TOPV = 10 ** max(3, math.ceil(math.log10(max(v for _, v in rows) + 1)))
    lt = math.log10(TOPV)
    cols_all = int(W / (F * 0.6))
    PW = 78
    NR = 27
    g = Grid(cols_all, NR, F)
    g.x0 = (W - cols_all * g.cw) / 2
    g.y0 = 8
    H = int(g.y0 * 2 + NR * g.lh)
    c0 = (cols_all - PW) // 2
    c1 = c0 + PW - 1
    mid = (c0 + c1) // 2
    g.put(0, mid, "◦", "r")
    g.text(1, mid - 1, "╱", "r")
    g.text(1, mid + 1, "╲", "r")
    TOP, BOT = 2, NR - 1
    hang = [(TOP, mid - 2, "╩"), (TOP, mid + 2, "╩")]

    def roller(r):
        g.text(r, c0 - 3, "▐◉", "g2")
        g.text(r, c0 - 1, "═" * (PW + 2), "wd")
        g.text(r, c1 + 2, "◉▌", "g2")

    roller(TOP)
    for rr, cc, ch in hang:
        g.put(rr, cc, ch, "r b")
    for r in range(TOP + 1, BOT):
        g.put(r, c0, "┃", "wd")
        g.put(r, c1, "┃", "wd")
        for c in (c0 + 1, c1 - 1):
            g.put(r, c, "░", "wn")
    ic0, ic1 = c0 + 4, c1 - 4
    header = (TOP + 2, ic0)
    stamp = f"inscribed {datetime.date.today():%d %b %Y}".lower()
    g.text(TOP + 3, ic0, "▸ " + stamp, "g")
    g.text(TOP + 4, ic0, "─" * 30, "md")
    seal_c = ic1 - 9
    LBL = 21
    bc0 = ic0 + LBL
    BL = 33
    vc = ic1
    tick_r = TOP + 6
    ticks = []
    for k in range(int(lt) + 1):
        v = 10 ** k
        col = bc0 + round(BL * k / lt)
        lbl = f"{v // 1000}k" if v >= 1000 else str(v)
        st = col - len(lbl) // 2
        g.text(tick_r, st, lbl, "m")
        ticks.append((st, st + len(lbl)))
    gaps = [(ticks[k][1] + 1, ticks[k + 1][0] - 1) for k in range(len(ticks) - 1)]
    nd = min((b - a + 1) // 2 for a, b in gaps)
    for a, b in gaps:
        span = 2 * nd - 1
        st = a + ((b - a + 1) - span) // 2
        for j in range(nd):
            g.put(tick_r, st + 2 * j, "·", "md")
    overlays = []
    bar_cells = []
    r = tick_r + 2
    t0 = 1.9
    for i, (label, v) in enumerate(rows):
        g.text(r, ic0, label, "c2")
        for c in range(bc0, bc0 + BL + 1):
            g.put(r, c, "┈", "dk")
        for k in range(int(lt) + 1):
            g.put(r, bc0 + round(BL * k / lt), "┊" if False else "·", "md")
        vs = f"{v:,}"
        g.text(r, vc - len(vs) + 1, vs, "c b")
        if v == 0:
            g.put(r, bc0, "•", "g")
        else:
            n = max(1, round(BL * math.log10(v) / lt)) + 1
            bs = bar_str(n, BL)
            d = t0 + i * 0.32
            tot = bc0 + len(bs)
            sp = 100 * len(bs) / tot
            overlays.append(g.ov(r, bc0, bs, "g2 b ink", f' style="--s:{sp:.2f}%;animation-delay:{d:.2f}s;animation-timing-function:steps({len(bs)})"'))
            bar_cells.append({(r + dr, c) for dr in (-1, 0, 1) for c in range(bc0 - 1, bc0 + len(bs) + 1)})
        r += 2
    g.text(r, ic0, "┄" * (ic1 - ic0 + 1), "md")
    foot = f"{s['xp']:,}"
    g.text(r + 1, ic0, foot, "g2 b")
    g.text(r + 1, ic0 + len(foot) + 1, "contributions inscribed this year", "c2")
    tp = f"top {pct:.0f}%"
    g.text(r + 1, ic1 - len(tp) + 1, tp, "m")
    roller(BOT)
    busy = set()
    for rr in range(TOP + 1, BOT):
        for cc in range(c0 + 2, c1 - 1):
            if g.get(rr, cc) != " ":
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        busy.add((rr + dr, cc + dc))
    for spec in bar_cells:
        busy |= spec
    content_rows = {rr for rr in range(TOP + 1, BOT) if any(g.get(rr, cc) not in (" ", None) for cc in range(c0 + 2, c1 - 1))}
    content_rows |= {min(sp)[0] for sp in bar_cells}
    content_rows |= {min(sp)[0] + 1 for sp in bar_cells}
    content_rows |= set(range(TOP + 1, TOP + 6))
    for rr in range(TOP + 1, BOT):
        if rr in content_rows:
            continue
        off = 0 if rr % 4 == 0 else 6
        for cc in range(c0 + 2, c1 - 1):
            if (cc - c0 + off) % 12 in (0, 1) and g.get(rr, cc) == " " and (rr, cc) not in busy:
                g.put(rr, cc, "┄", "pn")
    for k in range(5):
        for cc in range(ic1 - 9, ic1 + 1):
            for dr in (-1, 0, 1):
                g.put(TOP + 1 + k + dr, cc, " ", None) if g.get(TOP + 1 + k + dr, cc) == "┄" else None
    lv = lvl.replace("-", "−")
    seal = ["╔══════╗", "║      ║", "║      ║", "║      ║", "╚══════╝"]
    seal_c = ic1 - 8
    seal_g = "".join(g.ov(TOP + 1 + k, seal_c, ln, "r") for k, ln in enumerate(seal))
    sx = g.x(seal_c) + 4 * g.cw
    sy = g.y(TOP + 3) - F * 0.35
    big = 2 * F
    seal_g += (f'<text x="{g.x0:.2f}" y="{g.y(TOP + 3) + 2:.2f}" font-size="{F}">{" " * (seal_c + 2)}<tspan class="r b" font-size="{big}">{esc(lv)}</tspan></text>'
               f'<text x="{g.x0:.2f}" y="{g.y(TOP + 4) + 1:.2f}" font-size="{F}">{" " * (seal_c + 2)}<tspan class="r" font-size="{F * 0.8:.0f}" letter-spacing="1.2">RANK</tspan></text>')
    css = f"""
.paper{{animation:unroll 1.5s .2s cubic-bezier(.45,.05,.25,1) both;}}
.broll{{animation:drop 1.5s .2s cubic-bezier(.45,.05,.25,1) both;}}
.ink{{animation:ink 1s cubic-bezier(.4,.1,.2,1) both;}}
.seal{{transform-origin:{sx:.1f}px {sy:.1f}px;transform:rotate(-4deg);animation:stamp .45s 4.2s cubic-bezier(.2,1.4,.4,1) both;}}
.fade{{animation:fade .8s 1.6s ease-out both;}}
@keyframes unroll{{from{{clip-path:inset(0 0 100% 0);}}to{{clip-path:inset(0 0 0 0);}}}}
@keyframes drop{{from{{transform:translateY(-{(BOT - TOP) * g.lh:.1f}px);}}to{{transform:translateY(0);}}}}
@keyframes ink{{from{{clip-path:inset(0 var(--s) 0 0);}}to{{clip-path:inset(0 0 0 0);}}}}
@keyframes stamp{{0%{{opacity:0;transform:scale(1.6) rotate(-4deg);}}100%{{opacity:.95;transform:scale(1) rotate(-4deg);}}}}
@keyframes fade{{from{{opacity:0;}}to{{opacity:1;}}}}
"""
    body = (
        f'<ellipse cx="{W / 2}" cy="{H / 2}" rx="520" ry="{H / 2}" fill="url(#atmo)"/>'
        + g.svg(0, TOP + 1)
        + f'<g class="paper">{g.svg(TOP + 1, BOT)}<text x="{g.x(header[1]):.1f}" y="{g.y(header[0]) + 2:.1f}" font-size="25" letter-spacing="4.5" class="tt c">RECORD OF DEEDS</text><g class="fade">{"".join(overlays)}</g><g class="seal">{seal_g}</g></g>'
        + f'<g class="broll">{g.svg(BOT, BOT + 1)}</g>'
    )
    return svg(W, H, body, css, f"Record of deeds: rank {lvl}", "", ("mono", "monob", "sym", "title"))


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:3]


def balanced_wrap(text, width):
    best = None
    for w in range(width, 17, -1):
        lines = wrap(text, w)
        if any(len(l) > width for l in lines):
            continue
        score = (len(lines), max(len(l) for l in lines) - min(len(l) for l in lines))
        if len(lines[-1].split()) == 1 and len(lines) > 1:
            score = (score[0], score[1] + 50)
        if best is None or score < best[0]:
            best = (score, lines)
    return best[1]


def wrap_px(text, maxw, size, kind):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and measure(t, size, kind) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def balanced_px(text, maxw, size, kind):
    best = None
    w = maxw
    while w > maxw * 0.6:
        lines = wrap_px(text, w, size, kind)
        widths = [measure(l, size, kind) for l in lines]
        score = (len(lines), max(widths) - min(widths) + (60 if len(lines) > 1 and len(lines[-1].split()) == 1 else 0))
        if best is None or score < best[0]:
            best = (score, lines)
        w -= 6
    return best[1]


def ema(i, repo):
    name, title, desc, lang, stars = repo
    W, H = 360, 330
    cx = W / 2
    rail_y, apex_y, eave_y, base_y = 12, 46, 100, 318
    left, right = 30, 330
    rnd = random.Random(10 + i)
    wood, wood_lt, grain = "#8a6a46", "#a8845a", "#2e2318"
    board = f"M{cx},{apex_y} L{right},{eave_y} L{right},{base_y} L{left},{base_y} L{left},{eave_y} Z"
    inner_off = 7
    inner = (f"M{cx},{apex_y + inner_off * 1.25:.1f} L{right - inner_off},{eave_y + inner_off * 0.55:.1f} L{right - inner_off},{base_y - inner_off} "
             f"L{left + inner_off},{base_y - inner_off} L{left + inner_off},{eave_y + inner_off * 0.55:.1f} Z")
    grains = []
    for k in range(9):
        y = eave_y + 16 + k * 23 + rnd.uniform(-3, 3)
        x0 = left + 10 + rnd.uniform(0, 30)
        x1 = right - 10 - rnd.uniform(0, 30)
        a1, a2 = rnd.uniform(-2, 2), rnd.uniform(-2, 2)
        grains.append(f'<path d="M{x0:.1f},{y:.1f} C{x0 + (x1 - x0) * .33:.1f},{y + a1:.1f} {x0 + (x1 - x0) * .66:.1f},{y + a2:.1f} {x1:.1f},{y:.1f}" stroke="{grain}" stroke-width=".8" fill="none" opacity=".9"/>')
    for k in range(2):
        y = eave_y - 14 - k * 14
        half = (y - apex_y) / (eave_y - apex_y) * (right - cx) - 22
        if half > 20:
            grains.append(f'<path d="M{cx - half:.1f},{y:.1f} L{cx + half:.1f},{y:.1f}" stroke="{grain}" stroke-width=".8" opacity=".9"/>')
    TS = 23.0
    while measure(title, TS, "title") > 268 and TS > 17:
        TS -= 0.5
    DS = 17.0
    dl = balanced_px(desc, 262, DS, "italic")
    slug = name.upper()
    block = [("slug", 13), ("gap", 9), ("title", TS * 1.05), ("gap", 9), ("rule", 1), ("gap", 12)] + [("desc", DS * 1.22)] * len(dl)
    bh = sum(h for _, h in block)
    foot_y = base_y - 26
    top = eave_y + 6 + ((foot_y - 18) - (eave_y + 6) - bh) / 2
    y = top
    parts = []
    di = 0
    for kind, h in block:
        if kind == "slug":
            sw = len(slug) * 11.5 * 0.6 + len(slug) * 11.5 * 0.16
            parts.append(f'<path d="M{cx - sw / 2 - 14:.1f},{y + h - 8:.1f} l5,3.5 l-5,3.5z" fill="{COL["g2"]}"/>')
            parts.append(f'<text x="{cx}" y="{y + h - 1:.1f}" font-size="11.5" letter-spacing="1.85" text-anchor="middle" class="px g2">{esc(slug)}</text>')
        elif kind == "title":
            parts.append(f'<text x="{cx}" y="{y + h * 0.8:.1f}" font-size="{TS:.1f}" text-anchor="middle" class="tt c">{esc(title)}</text>')
        elif kind == "rule":
            parts.append(f'<path d="M{cx - 34},{y:.1f} H{cx + 34}" stroke="{COL["g"]}" stroke-width="1"/>'
                         f'<path d="M{cx},{y - 3:.1f} l3,3 l-3,3 l-3,-3z" fill="{COL["g"]}"/>')
        elif kind == "desc":
            parts.append(f'<text x="{cx}" y="{y + h * 0.8:.1f}" font-size="{DS}" text-anchor="middle" class="it c2">{esc(dl[di])}</text>')
            di += 1
        y += h
    fx0, fx1 = left + 24, right - 24
    lt = f"◆ {lang}"
    st = f"★ {stars}"
    lw = len(lt) * 12 * 0.6
    sw2 = len(st) * 12 * 0.6
    parts.append(f'<text x="{fx0}" y="{foot_y:.1f}" font-size="12" class="px g">{esc(lt)}</text>')
    parts.append(f'<text x="{fx1}" y="{foot_y:.1f}" font-size="12" text-anchor="end" class="px g2">{esc(st)}</text>')
    parts.append(f'<path d="M{fx0 + lw + 10:.1f},{foot_y - 4:.1f} H{fx1 - sw2 - 10:.1f}" stroke="{wood}" stroke-width=".8" opacity=".7"/>')
    dur = 4.8 + (i % 3) * 0.6
    css = f"""
.hang{{animation:hang .9s {0.15 + i * 0.12:.2f}s cubic-bezier(.2,.9,.3,1.2) both;}}
.sway{{transform-origin:{cx}px {rail_y}px;animation:sway {dur:.2f}s {-i * 1.3:.2f}s ease-in-out infinite alternate;}}
@keyframes hang{{from{{opacity:0;transform:translateY(-12px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes sway{{from{{transform:rotate(-.6deg);}}to{{transform:rotate(.6deg);}}}}
"""
    defs = (f'<clipPath id="bd"><path d="{board}"/></clipPath>'
            '<linearGradient id="bf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1712"/><stop offset="1" stop-color="#14100c"/></linearGradient>')
    body = (
        f'<ellipse cx="{cx}" cy="{H / 2}" rx="{W / 2}" ry="{H / 2}" fill="url(#atmo)"/>'
        f'<path d="M0,{rail_y} H{W}" stroke="#4a4d55" stroke-width="2"/>'
        f'<g class="hang"><g class="sway">'
        f'<path d="M{cx},{rail_y} V{apex_y + 4}" stroke="#a8452f" stroke-width="2.2"/>'
        f'<circle cx="{cx}" cy="{rail_y}" r="4" fill="#2a2c31" stroke="#6a6d75" stroke-width="1"/>'
        f'<path d="{board}" fill="url(#bf)"/>'
        f'<g clip-path="url(#bd)">{"".join(grains)}</g>'
        f'<path d="{board}" fill="none" stroke="{wood}" stroke-width="2.2" stroke-linejoin="miter"/>'
        f'<path d="M{left - 6},{eave_y} H{right + 6}" stroke="{wood_lt}" stroke-width="2.2" stroke-linecap="square"/>'
        f'<path d="{inner}" fill="none" stroke="{COL["g"]}" stroke-width=".7" opacity=".45"/>'
        f'<circle cx="{cx}" cy="{apex_y + 30}" r="7" fill="none" stroke="{COL["g"]}" stroke-width=".9" opacity=".7"/>'
        f'<circle cx="{cx}" cy="{apex_y + 30}" r="2" fill="{COL["g"]}" opacity=".7"/>'
        + "".join(parts)
        + "</g></g>"
    )
    return svg(W, H, body, css, f"{name}: {title}", defs, ("title", "italic", "plex", "sym"))


TORO = [
    ("     ◉     ", "     2     "),
    ("    /^\\    ", "    123    "),
    (" __/===\\__ ", " 112222233 "),
    ("/_________\\", "11122222333"),
    ("  |.---.|  ", "  1222223  "),
    ("  ||   ||  ", "  11   33  "),
    ("  ||   ||  ", "  11   33  "),
    ("  |'---'|  ", "  1222223  "),
    (" _[=====]_ ", " 112222233 "),
    ("    |#|    ", "    123    "),
    ("    |#|    ", "    123    "),
    ("   _|#|_   ", "   11233   "),
    ("  /#####\\  ", "  1122233  "),
    (" /#######\\ ", " 111222333 "),
]
FIRE = (5, 6)
FW = 4


def lanterns():
    W, F = 1100, 13
    cols = int(W / (F * 0.6))
    NR = 24
    g = Grid(cols, NR, F)
    g.x0 = (W - cols * g.cw) / 2
    g.y0 = 4
    H = int(g.y0 * 2 + NR * g.lh)
    rnd = random.Random(9)
    vr = random.Random(31)
    n = len(STACK)
    slot = 17
    m0 = (cols - slot * n) // 2
    TOP = 3
    GROUND = TOP + len(TORO)
    for r in range(0, TOP + 2):
        for c in range(cols):
            if rnd.random() < 0.035:
                g.put(r, c, rnd.choice("·.✧"), "md")
    overlays, glows = [], []
    for c in range(cols):
        g.put(GROUND, c, rnd.choice(",.'`") if rnd.random() < 0.55 else " ", "gr")
    for i, label in enumerate(STACK):
        cx = m0 + slot * i + slot // 2
        lc = cx - 5
        d = 0.5 + i * 0.35
        for k, (art, shade) in enumerate(TORO):
            for j, ch in enumerate(art):
                if ch == " ":
                    continue
                g.put(TOP + k, lc + j, ch, {"1": "s1", "2": "s2", "3": "s3"}[shade[j]])
        for j in range(4, 7):
            for k in FIRE:
                g.put(TOP + k, lc + j, ".", "dk")
        for k in (len(TORO) - 3, len(TORO) - 2, len(TORO) - 1):
            for j in range(11):
                if g.get(TOP + k, lc + j) == "#" and vr.random() < 0.4:
                    g.put(TOP + k, lc + j, "#", "mo")
        frames = [("*%*", "%#%"), ("%#%", "#*#"), ("#*%", "%*#")]
        per = 1.0 + vr.random() * 0.5
        shift = vr.random() * per
        fr_svg = "".join(
            f'<g class="ff" style="animation-duration:{per:.2f}s;animation-delay:{-(f * per / 3) - shift:.2f}s">'
            + g.ov(TOP + FIRE[0], lc + 4, frames[f][0], "w b") + g.ov(TOP + FIRE[1], lc + 4, frames[f][1], "w2 b") + "</g>"
            for f in range(3)
        )
        gx, gy = g.x(cx) + g.cw / 2, g.y(TOP + 5) + 4
        glows.append(f'<ellipse class="lit" style="animation-delay:{d:.2f}s" cx="{gx:.1f}" cy="{gy:.1f}" rx="58" ry="46" fill="url(#halo)"/>'
                     f'<ellipse class="lit" style="animation-delay:{d:.2f}s" cx="{gx:.1f}" cy="{g.y(GROUND) - 4:.1f}" rx="70" ry="13" fill="url(#halo)" opacity=".7"/>')
        overlays.append(f'<g class="lit" style="animation-delay:{d:.2f}s">{fr_svg}</g>')
        for c in range(lc - 3, lc + 14):
            if g.get(GROUND, c) not in (" ", None) and rnd.random() < 0.6:
                g.put(GROUND, c, g.get(GROUND, c), "wd")
        pw = max(9, len(label) + 6)
        if (pw - cx) % 2:
            pass
        pc = cx - pw // 2
        pr = GROUND + 2
        g.put(pr - 1, cx, "│", "r")
        top = "╔" + "═" * (pw - 2) + "╗"
        top = top[: cx - pc] + "╧" + top[cx - pc + 1:]
        g.text(pr, pc, top, "wd")
        g.text(pr + 1, pc, "║", "wd")
        g.text(pr + 1, pc + pw - 1, "║", "wd")
        g.center(pr + 1, label, "g2 b", pc + 1, pc + pw - 1)
        g.text(pr + 2, pc, "╚" + "═" * (pw - 2) + "╝", "wd")
    css = """
.lit{animation:lit 1s ease-out both;}
.ff{animation-name:fl;animation-timing-function:steps(1);animation-iteration-count:infinite;}
@keyframes lit{from{opacity:0;}to{opacity:1;}}
@keyframes fl{0%{opacity:1;}33.33%{opacity:0;}100%{opacity:0;}}
"""
    defs = (f'<radialGradient id="halo"><stop offset="0" stop-color="{COL["w"]}" stop-opacity=".34"/>'
            f'<stop offset=".5" stop-color="{COL["w"]}" stop-opacity=".1"/><stop offset="1" stop-color="{COL["w"]}" stop-opacity="0"/></radialGradient>')
    body = (
        f'<ellipse cx="{W / 2}" cy="{H * 0.4:.0f}" rx="560" ry="{H * 0.45:.0f}" fill="url(#atmo)"/>'
        + "".join(glows) + g.svg() + "".join(overlays)
    )
    return svg(W, H, body, css, "Tech stack: " + ", ".join(STACK), defs)


def raven(i, item):
    key, icon, label = item
    W, F = 200, 14
    cols, NR = 23, 3
    g = Grid(cols, NR, F)
    g.x0 = (W - cols * g.cw) / 2
    g.y0 = 2
    H = int(g.y0 * 2 + NR * g.lh)
    tw = 21
    c0 = 1
    g.text(0, c0, "╔" + "═" * (tw - 2) + "╗", "wd")
    g.text(1, c0, "║", "wd")
    g.text(1, c0 + tw - 1, "║", "wd")
    st = g.center(1, f"{icon}  {label}", "c", c0 + 1, c0 + tw - 1)
    g.put(1, st, icon, "g2 b")
    g.text(2, c0, "╚" + "═" * (tw - 2) + "╝", "wd")
    px, py = g.x(c0 + tw // 2) + g.cw / 2, g.y0
    css = f"""
.sw{{transform-origin:{px:.1f}px {py:.1f}px;animation:swing 1.4s {0.1 + i * 0.14:.2f}s cubic-bezier(.3,1.5,.4,1) both;}}
@keyframes swing{{0%{{opacity:0;transform:rotate(-8deg);}}25%{{opacity:1;}}100%{{opacity:1;transform:rotate(0deg);}}}}
"""
    body = (
        f'<ellipse cx="{W / 2}" cy="{H / 2}" rx="{W / 2}" ry="{H / 2}" fill="url(#atmo)"/>'
        + f'<g class="sw">{g.svg()}</g>'
    )
    return svg(W, H, body, css, f"Contact: {label}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        stats, repos = fetch(token)
    else:
        stats = json.loads((HERE / "sample.json").read_text())
        repos = REPOS
    for i in range(len(CHAPTERS)):
        (OUT / f"chapter-{i + 1}.svg").write_text(chapter(i))
    (OUT / "scroll.svg").write_text(scroll(stats))
    for i, r in enumerate(repos):
        (OUT / f"ema-{r[0]}.svg").write_text(ema(i, r))
    for i, r in enumerate(RAVENS):
        (OUT / f"raven-{r[0]}.svg").write_text(raven(i, r))


if __name__ == "__main__":
    main()

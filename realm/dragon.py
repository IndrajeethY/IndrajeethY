import base64
import datetime
import json
import os
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "images" / "keep" / "dragon.svg"
USER = "IndrajeethY"
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

ROWS, COLS = 7, 53
P, S = 17, 14
GX, GY = 30, 58
W, H = GX * 2 + COLS * P, 236
SHADE = ["#1c2230", "#5a4a28", "#8a6a2e", "#c2943a", "#f2c14e"]
EMPTY = SHADE[0]
BODY = ["#d9573f", "#cc4f3b", "#bf4837", "#b04233", "#a03d30", "#913a2e", "#83372c", "#76352b", "#6a342b"]
GOLD, CREAM, DIM = "#d8b971", "#e6e0cf", "#a89a74"
TARGET_LOOP = 36.0
MAX_LEN, START_LEN = 22, 4


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return json.loads((HERE / "contrib-sample.json").read_text())
    q = """{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions
      weeks{contributionDays{date contributionCount contributionLevel}}}}}}""" % USER
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": "bearer " + token, "User-Agent": "realm"})
    cal = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[[d["contributionCount"], LEVEL[d["contributionLevel"]]] for d in w["contributionDays"]] for w in cal["weeks"]]
    return {"total": cal["totalContributions"], "from": cal["weeks"][0]["contributionDays"][0]["date"], "weeks": weeks}


def font(file, family):
    data = base64.b64encode((HERE / "fonts" / file).read_bytes()).decode()
    return "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2');}" % (family, data)


def cx(c):
    return GX + c * P + S / 2


def cy(r):
    return GY + r * P + S / 2


def plan(level):
    lit = {(c, r) for c in range(COLS) for r in range(ROWS) if level.get((c, r), 0) > 0}
    c, r = -2, 3
    path, eat = [(c, r)], {}

    def go(nc, nr):
        nonlocal c, r
        while (c, r) != (nc, nr):
            if c != nc:
                c += 1 if nc > c else -1
            else:
                r += 1 if nr > r else -1
            path.append((c, r))
            if (c, r) in lit and (c, r) not in eat:
                eat[(c, r)] = len(path) - 1

    for col in range(COLS):
        rows = sorted(rr for (cc, rr) in lit if cc == col)
        if not rows:
            continue
        if abs(r - rows[-1]) < abs(r - rows[0]):
            rows.reverse()
        go(col, r)
        for rr in rows:
            go(col, rr)
    go(COLS + MAX_LEN + 2, r)
    return path, eat


def pct(i, n):
    return f"{100 * i / n:.3f}".rstrip("0").rstrip(".") + "%"


def build(data):
    weeks = data["weeks"]
    level = {(c, r): d[1] for c, w in enumerate(weeks) for r, d in enumerate(w)}
    path, eat = plan(level)
    hold = 26
    n = len(path) + hold
    dt = max(0.06, min(0.12, TARGET_LOOP / n))
    T = n * dt
    Ts = f"{T:.2f}s"
    per = max(1, -(-len(eat) // (MAX_LEN - START_LEN)))
    eat_steps = sorted(eat.values())
    length, j = [], 0
    for i in range(len(path)):
        while j < len(eat_steps) and eat_steps[j] <= i:
            j += 1
        length.append(min(MAX_LEN, START_LEN + j // per))
    first = {k: next((i for i, L in enumerate(length) if L > k), None) for k in range(MAX_LEN + 2)}
    dirs = []
    for i in range(len(path)):
        a = path[i - 1] if i else (path[0][0] - 1, path[0][1])
        dirs.append({(1, 0): "R", (-1, 0): "L", (0, -1): "U", (0, 1): "D"}.get((path[i][0] - a[0], path[i][1] - a[1]), "R"))

    css = [font("plex-dragon.woff2", "DMono"), font("cg-dragon.woff2", "DSerif")]
    css.append(
        "text{font-family:'DMono',monospace;font-weight:500}"
        ".lab{font-size:11px;letter-spacing:.14em;fill:%s}"
        ".ser{font-family:'DSerif',serif;font-weight:600}"
        ".mv{animation:pth %s linear infinite;animation-fill-mode:backwards}"
        ".fx{transform-box:fill-box;transform-origin:center}"
        "@keyframes boom{0%%{opacity:0;transform:scale(.3)}.1%%{opacity:1;transform:scale(1)}1%%{opacity:0;transform:scale(1.7)}100%%{opacity:0}}"
        "@keyframes fl{0%%{transform:scale(1,1)}50%%{transform:scale(.8,1.15)}}"
        % (DIM, Ts)
    )
    frames = [f"{pct(i, n)}{{transform:translate({cx(c):.1f}px,{cy(r):.1f}px)}}" for i, (c, r) in enumerate(path)]
    frames.append(f"100%{{transform:translate({cx(path[-1][0]):.1f}px,{cy(path[-1][1]):.1f}px)}}")
    css.append("@keyframes pth{" + "".join(frames) + "}")
    rot = {"R": "none", "L": "scale(-1,1)", "U": "rotate(-90deg)", "D": "rotate(90deg)"}
    stops, prev = [], None
    for i, d in enumerate(dirs):
        if d != prev:
            stops.append(f"{pct(i, n)}{{transform:{rot[d]}}}")
            prev = d
    css.append("@keyframes hrot{" + "".join(stops) + "}")
    for k in range(START_LEN, MAX_LEN + 1):
        v = first.get(k)
        if v is not None:
            css.append(f"@keyframes g{k}{{0%,{pct(v, n)}{{opacity:0}}{pct(v + 1, n)},99.5%{{opacity:1}}100%{{opacity:0}}}}")

    cells = []
    reset0 = len(path) + 3
    for c, w in enumerate(weeks):
        for r, (_, lv) in enumerate(w):
            x, y = GX + c * P, GY + r * P
            if (c, r) in eat:
                i = eat[(c, r)]
                rs = reset0 + c * (hold - 8) / COLS
                nm = f"c{c}_{r}"
                css.append(f"@keyframes {nm}{{0%,{pct(i, n)}{{fill:{SHADE[lv]}}}{pct(i + 0.6, n)},{pct(rs, n)}{{fill:{EMPTY}}}{pct(rs + 5, n)},100%{{fill:{SHADE[lv]}}}}}")
                cells.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="3" fill="{SHADE[lv]}" style="animation:{nm} {Ts} linear infinite"/>')
            else:
                cells.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="3" fill="{SHADE[lv]}"/>')

    fx = []
    petals = "".join(
        f'<ellipse cx="0" cy="-6" rx="2.6" ry="6" fill="{col}" transform="rotate({a})"/>'
        for a, col in ((0, "#ffd27a"), (72, "#ff9a3a"), (144, "#ffc04a"), (216, "#ff7a2a"), (288, "#ffb347"))
    ) + '<circle r="3.4" fill="#fff3c8"/>'
    for (c, r), i in eat.items():
        fx.append(f'<g transform="translate({cx(c):.1f},{cy(r):.1f})"><g class="fx" style="opacity:0;animation:boom {Ts} linear {i * dt:.2f}s infinite both">{petals}</g></g>')

    segs = []
    for k in range(MAX_LEN - 1, 0, -1):
        if k >= START_LEN and first.get(k) is None:
            continue
        f = k / (MAX_LEN - 1)
        sz = 13 - 6 * f
        col = BODY[min(len(BODY) - 1, int(f * len(BODY)))]
        vis = "" if k + 1 < START_LEN else (f' style="animation:g{k + 1} {Ts} steps(1,end) infinite"' if first.get(k + 1) is not None else ' style="opacity:0"')
        tvis_a = 0 if k < START_LEN else first.get(k)
        tvis_b = first.get(k + 1)
        seg = f'<rect x="{-sz / 2:.1f}" y="{-sz / 2:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="{sz * 0.32:.1f}" fill="{col}"/>'
        seg += f'<circle r="{1 + 1.2 * (1 - f):.1f}" fill="{GOLD}" opacity=".85"/>'
        body = f"<g{vis}>{seg}</g>"
        tail = ""
        if k >= START_LEN - 1 and tvis_a is not None:
            lo = "0%{opacity:1}" if tvis_a == 0 else f"0%,{pct(tvis_a, n)}{{opacity:0}}{pct(tvis_a + 1, n)}{{opacity:1}}"
            hi = f"{pct(tvis_b, n)}{{opacity:1}}{pct(tvis_b + 1, n)},100%{{opacity:0}}" if tvis_b is not None else "99.5%{opacity:1}100%{opacity:0}"
            css.append(f"@keyframes t{k}{{{lo}{hi}}}")
            flame = (
                '<g class="fx" style="animation:fl .3s steps(1) infinite">'
                '<path d="M3,0 Q-2,-6 -11,-1 Q-5,0 -11,2 Q-2,6 3,0 Z" fill="#ff8a3a"/>'
                '<path d="M2,0 Q-2,-3 -6,0 Q-2,3 2,0 Z" fill="#ffd27a"/></g>'
                f'<rect x="-3.5" y="-3.5" width="7" height="7" rx="2.2" fill="{BODY[-1]}"/>'
            )
            tail = f'<g style="animation:t{k} {Ts} steps(1,end) infinite"><g style="animation:hrot {Ts} steps(1,end) infinite;animation-delay:{k * dt:.3f}s">{flame}</g></g>'
        segs.append(f'<g class="mv" style="animation-delay:{k * dt:.3f}s">{body}{tail}</g>')

    head = (
        '<g class="mv"><g style="animation:hrot ' + Ts + ' steps(1,end) infinite"><g transform="scale(1.35)">'
        '<path d="M-3,-7 Q-8,-14 -15,-14 Q-10,-11 -7,-6 Z" fill="#f0dca8"/>'
        '<path d="M-6,-5 Q-12,-10 -17,-8 Q-12,-6 -9,-3 Z" fill="#c9a45c"/>'
        '<rect x="-8" y="-7.5" width="15" height="15" rx="4" fill="#e0603f"/>'
        '<path d="M4,-5.5 L13,-3.2 Q15,-2.6 14,-0.8 L8,-0.4 L14,1 Q15,2.8 12.5,3.6 L4,5.5 Z" fill="#e0603f"/>'
        '<path d="M8,-0.4 L14.5,-0.2 L14.5,1 Z" fill="#2a1410"/>'
        '<rect x="-8" y="-7.5" width="15" height="15" rx="4" fill="none" stroke="#ffb07a" stroke-width=".8" opacity=".6"/>'
        '<circle cx="1.5" cy="-3" r="2.3" fill="#ffd27a"/><circle cx="2" cy="-3" r="1" fill="#2a1410"/>'
        '<circle cx="1.5" cy="-3" r="4" fill="#ffb347" opacity=".25"/>'
        f'<circle cx="-3" cy="2.5" r="1.6" fill="{GOLD}"/>'
        "</g></g></g>"
    )

    start = datetime.date.fromisoformat(data["from"])
    end = start + datetime.timedelta(days=sum(len(w) for w in weeks) - 1)
    labels, lastm = [], None
    for c in range(COLS):
        dd = start + datetime.timedelta(days=7 * c)
        if dd.month != lastm:
            if COLS - c >= 2:
                labels.append(f'<text class="lab" x="{GX + c * P}" y="{GY + ROWS * P + 14}">{dd.strftime("%b").upper()}</text>')
            lastm = dd.month
    total = f"{data['total']:,}"
    ly = GY + ROWS * P + 40
    legend = (
        f'<text class="lab" x="{W - GX - 168}" y="{ly}">LESS</text>'
        + "".join(f'<rect x="{W - GX - 128 + i * 17}" y="{ly - 11}" width="{S}" height="{S}" rx="3" fill="{SHADE[i]}"/>' for i in range(5))
        + f'<text class="lab" x="{W - GX - 38}" y="{ly}">MORE</text>'
        + f'<text class="lab" x="{GX}" y="{ly}" style="letter-spacing:.06em">a dragon devours the year, one day at a time</text>'
    )
    header = (
        f'<text class="ser" x="{GX}" y="34" style="font-size:22px"><tspan fill="{GOLD}">{total}</tspan>'
        f'<tspan fill="{CREAM}"> contributions · the dragon’s hunt</tspan></text>'
        f'<text class="lab" x="{W - GX}" y="34" style="text-anchor:end">{start.strftime("%b %Y").upper()} — {end.strftime("%b %Y").upper()}</text>'
    )
    mask = (
        f'<linearGradient id="fg" x1="{GX - 18}" x2="{W - GX + 18}" y1="0" y2="0" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#000"/><stop offset=".02" stop-color="#fff"/><stop offset=".97" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="mk"><rect x="{GX - 18}" y="{GY - 12}" width="{W - 2 * GX + 36}" height="{ROWS * P + 22}" fill="url(#fg)"/></mask>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="A dragon eats this year\'s {total} contributions on the contribution graph, like the classic snake">'
        f"<style>{''.join(css)}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>"
        f"<defs>{mask}</defs>"
        + header + "".join(cells) + "".join(fx)
        + f'<g mask="url(#mk)">{"".join(segs)}{head}</g>'
        + "".join(labels) + legend + "</svg>"
    ), T, len(path), dt


def main():
    svg, T, steps, dt = build(fetch())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"{OUT} {len(svg.encode()) // 1024} KB loop={T:.1f}s steps={steps} dt={dt:.3f}")


if __name__ == "__main__":
    main()

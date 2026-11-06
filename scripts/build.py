#!/usr/bin/env python3
"""从 papers.json 生成首页 index.html，并检查数据是否一致。

用法：python3 scripts/build.py
检查项（任何一项不过就退出码 1，不写文件）：
  - 每篇 published 的论文都有 papers/<slug>/index.html
  - papers/ 下的每个文件夹都在 papers.json 里登记过
  - id 不重复
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def esc(s):
    return html.escape(str(s or ""))


def check(data):
    errs = []
    ids = [p["id"] for p in data["papers"]]
    if len(ids) != len(set(ids)):
        errs.append("papers.json 里有重复的 id")
    slugs = {p["slug"] for p in data["papers"]}
    for p in data["papers"]:
        if p["status"] == "published" and not (ROOT / "papers" / p["slug"] / "index.html").exists():
            errs.append(f"{p['id']} 标为 published，但没有 papers/{p['slug']}/index.html")
    for d in (ROOT / "papers").iterdir():
        if d.is_dir() and d.name not in slugs:
            errs.append(f"papers/{d.name}/ 没有在 papers.json 里登记")
    return errs


def thumb(p):
    f = ROOT / "papers" / p["slug"] / "thumb.svg"
    if not f.exists():
        return ""
    svg = f.read_text(encoding="utf-8").strip()
    svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', "")
    return f'<div class="thumb">{svg}</div>'


def card(p):
    href = f'papers/{esc(p["slug"])}/index.html'
    return (
        f'<li id="p-{esc(p["id"])}" class="pub"><a class="card" href="{href}">'
        + thumb(p)
        + '<span class="body">'
        f'<span class="meta">{esc(p["id"])} · {esc(p["year"])} · {esc(p["authors"])}</span>'
        f'<span class="short">{esc(p["short"])}</span>'
        + (f'<span class="one">{esc(p["oneliner"])}</span>' if p.get("oneliner") else "")
        + f'<span class="full">{esc(p["title"])}</span>'
        '<span class="go">读这篇 →</span>'
        '</span></a></li>'
    )


def plan(p):
    return (
        f'<li id="p-{esc(p["id"])}" title="{esc(p["title"])} · {esc(p["authors"])}">'
        f'<span class="no">{esc(p["id"])}</span>'
        f'<span class="short">{esc(p["short"])}</span>'
        f'<span class="yr">{esc(p["year"])}</span></li>'
    )


# 地图上的地点：40 个预留位置，按阅读顺序沿一条弯路散布在陆地上（手工摆放，像真地图那样不规整）。
# 每项：(x, y, 标签方位) ；方位 b=下 t=上 l=左 r=右。系列超过 40 篇时在后面续写。
SLOTS = [
    (120, 470, "b"), (205, 405, "r"), (150, 320, "b"), (245, 255, "t"), (345, 305, "t"),
    (300, 410, "b"), (400, 480, "b"), (485, 405, "r"), (450, 315, "r"), (520, 230, "r"),
    (430, 160, "l"), (545, 120, "t"), (640, 175, "r"), (610, 280, "l"), (680, 365, "r"),
    (600, 455, "b"), (720, 500, "b"), (800, 430, "r"), (765, 330, "l"), (835, 250, "t"),
    (760, 165, "t"), (870, 110, "t"), (955, 175, "r"), (930, 285, "r"), (975, 380, "r"),
    (905, 470, "b"), (990, 520, "b"), (1040, 450, "r"), (1060, 340, "r"), (1030, 240, "r"),
    (1060, 130, "t"), (980, 75, "t"), (690, 70, "t"), (350, 80, "t"), (240, 150, "t"),
    (90, 210, "t"), (60, 380, "l"), (200, 540, "b"), (520, 540, "b"), (860, 560, "b"),
]
MAP_W, MAP_H = 1120, 620


def _smooth(pts):
    """Catmull-Rom 曲线穿过各点，转成三次贝塞尔路径。"""
    if len(pts) < 2:
        return ""
    d = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d)


def _blob(cx, cy, rx, ry, seed, n=72):
    """不规则的闭合轮廓（海岸线 / 等高线），用几组正弦叠加出起伏。"""
    import math
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        f = (1 + 0.07 * math.sin(3 * t + seed) + 0.05 * math.sin(5 * t + 2 * seed)
             + 0.035 * math.sin(9 * t + 3 * seed) + 0.02 * math.sin(15 * t + seed))
        pts.append((cx + rx * f * math.cos(t), cy + ry * f * math.sin(t)))
    d = _smooth(pts + pts[:3])
    return d + " Z"


def read_map(papers):
    """阅读地图：读完的地点点亮并一直闪，没读的是暗的；走过的路是蓝色实线，没走的是虚线。"""
    n = len(papers)
    if n > len(SLOTS):
        raise SystemExit(f"FAIL  地图只有 {len(SLOTS)} 个位置，papers.json 有 {n} 篇：去 build.py 的 SLOTS 续加位置")
    pts = [(x, y) for x, y, _ in SLOTS[:n]]
    lit_upto = max((i for i, p in enumerate(papers) if p["status"] == "published"), default=-1)
    out = []
    # 海：几道短浪纹
    for i, (wx, wy) in enumerate([(60, 70), (180, 590), (1040, 590), (1080, 40), (30, 560), (640, 600)]):
        out.append(f'<path class="wave" d="M{wx} {wy} q10 -7 20 0 t20 0 t20 0"/>')
    # 陆地 + 等高线（几座山，各画三圈）
    out.append(f'<path class="land" d="{_blob(560, 305, 455, 250, 0.6)}"/>')
    out.append(f'<path class="coast" d="{_blob(560, 305, 470, 262, 0.6)}"/>')
    for cx, cy, r, sd in [(440, 270, 120, 1.3), (790, 300, 140, 2.1), (210, 360, 80, 3.4), (980, 300, 70, 0.2)]:
        for k in (1.0, 0.68, 0.38):
            out.append(f'<path class="contour" d="{_blob(cx, cy, r * k, r * k * 0.72, sd + k)}"/>')
    # 指北针
    out.append('<g class="compass" transform="translate(1062 560)"><path d="M0 -26 L7 0 L0 -6 L-7 0 Z"/>'
               '<text x="0" y="-32" text-anchor="middle">N</text></g>')
    # 小路：先画全程虚线，再把走过的那段描成蓝色实线
    full = pts + [(pts[-1][0] + 40, pts[-1][1] + 30)] if pts else []
    out.append(f'<path class="trail" d="{_smooth(full)}"/>')
    if lit_upto >= 1:
        out.append(f'<path class="trail done" d="{_smooth(pts[:lit_upto + 1])}" pathLength="1"/>')
    if pts:
        ex, ey = full[-1]
        out.append(f'<text class="more-t" x="{ex + 8:.0f}" y="{ey + 12:.0f}">…</text>')
        sx, sy = pts[0]
        out.append(f'<text class="start-t" x="{sx - 22:.0f}" y="{sy + 6:.0f}" text-anchor="end">起点</text>')
        out.append('<text class="fog-t" x="930" y="300" text-anchor="middle">还没走到的地方</text>')
    for i, p in enumerate(papers):
        x, y, side = SLOTS[i]
        lit = p["status"] == "published"
        dx, dy, anc = {"b": (0, 34, "middle"), "t": (0, -22, "middle"),
                       "l": (-18, 6, "end"), "r": (18, 6, "start")}[side]
        lab = (f'<text class="nm" x="{x + dx}" y="{y + dy}" text-anchor="{anc}">'
               f'<tspan class="id">{esc(p["id"])} </tspan>{esc(p["short"])}</text>')
        if lit:
            out.append(
                f'<a class="node lit" style="--i:{i}" href="papers/{esc(p["slug"])}/index.html">'
                f'<title>{esc(p["id"])} {esc(p["short"])}：已读完，点进去看</title>'
                f'<circle class="pulse" cx="{x}" cy="{y}" r="11"/><circle class="pulse p2" cx="{x}" cy="{y}" r="11"/>'
                f'<circle class="core" cx="{x}" cy="{y}" r="11"/>{lab}</a>')
        else:
            out.append(f'<g class="node" style="--i:{i}"><title>{esc(p["id"])} {esc(p["short"])}：还没读</title>'
                       f'<circle class="dim" cx="{x}" cy="{y}" r="7"/>{lab}</g>')
    n_pub = sum(p["status"] == "published" for p in papers)
    label = f"阅读地图：{n} 篇论文是地图上的 {n} 个地点，已点亮 {n_pub} 个"
    return (f'<svg class="map" viewBox="0 0 {MAP_W} {MAP_H}" role="img" aria-label="{label}">'
            + "".join(out) + "</svg>")


def ver(rel):
    """静态文件加内容指纹，改了样式浏览器立刻拿新的，不吃旧缓存。"""
    import hashlib
    return rel + "?v=" + hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]


def render(data):
    s = data["site"]
    papers = data["papers"]
    pubs = [p for p in papers if p["status"] == "published"]
    todo = [p for p in papers if p["status"] != "published"]
    last = max((p.get("date", "") for p in pubs), default="")
    first = pubs[0] if pubs else None
    lede = "".join(f"<span>{esc(x)}。</span>" for x in s["tagline"].split("。") if x.strip())
    about = "".join(f"<p>{esc(x)}</p>" for x in s.get("about", []))
    start = (f'<a class="start rv" href="papers/{esc(first["slug"])}/index.html">从第一篇读起 →</a>' if first else "")
    cards = "\n".join(card(p) for p in pubs)
    rows = "\n".join(plan(p) for p in todo)
    more = f'<li class="more"><span class="dots">⋯</span><span>{esc(s["more"])}</span></li>' if s.get("more") else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(s["title"])}</title>
<meta name="description" content="{esc(s["tagline"])}">
<script>document.documentElement.classList.add("js")</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="{ver("assets/site.css")}">
</head>
<body>
<main class="wrap">
  <div class="top">
  <header class="hero">
    <h1 class="rv">{esc(s["title"])}</h1>
    <p class="lede rv">{lede}</p>
    {"<div class='about rv'>" + about + "</div>" if about else ""}
    {start}
  </header>

  <section class="sec atlas rv">
    <div class="sec-head"><h2>阅读地图</h2><span class="cnt">已点亮 {len(pubs)} / {len(papers)}</span></div>
    <div class="map-box">
      {read_map(papers)}
    </div>
    <p class="map-hint">← 左右拖动看整张地图 →</p>
    <p class="map-cap">每读完一篇，地图上就点亮一个地方。亮着的可以点进去看，暗着的还没走到。</p>
  </section>
  </div>

  <section class="sec rv">
    <div class="sec-head"><h2>已发布</h2><span class="cnt">{len(pubs)} 篇{f" · 最近更新 {esc(last)}" if last else ""}</span></div>
    <ol class="list">
{cards}
    </ol>
  </section>

  <section class="sec rv">
    <div class="sec-head"><h2>接下来要读的</h2><span class="cnt">按这个顺序陆续更新</span></div>
    <ol class="todo">
{rows}
{more}
    </ol>
  </section>

  <footer class="rv">
    <p class="by">{esc(s["author"])}{f' · <a href="{esc(s["repo"])}">源码</a>' if s.get("repo") else ""}</p>
  </footer>
</main>
<script src="{ver("assets/site.js")}"></script>
</body>
</html>
"""


def main():
    data = json.loads((ROOT / "papers.json").read_text(encoding="utf-8"))
    errs = check(data)
    if errs:
        print("FAIL\n  " + "\n  ".join(errs))
        sys.exit(1)
    (ROOT / "index.html").write_text(render(data), encoding="utf-8")
    n_pub = sum(p["status"] == "published" for p in data["papers"])
    print(f"OK  index.html 已生成：共 {len(data['papers'])} 篇，已发布 {n_pub} 篇")


if __name__ == "__main__":
    main()

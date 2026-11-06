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


def read_map(papers, cols, W, row_h, cls):
    """阅读地图：一条蛇形小路串起每篇论文，读完的地点点亮并一直闪，没读的是暗的。
    坐标全部由数据算出：cols 个一行，奇数行反向走。"""
    margin, top = 84, 56
    step = (W - 2 * margin) / (cols - 1)
    pts = []
    for i, p in enumerate(papers):
        r, c = divmod(i, cols)
        if r % 2:
            c = cols - 1 - c
        wob = 10 * __import__("math").sin(i * 1.7)          # 轻微起伏，像手画的路
        pts.append((margin + c * step, top + r * row_h + wob))
    H = top + (len(pts) - 1) // cols * row_h + 70
    # 小路：起点短桩 → 各点之间平滑曲线；换行处向外绕出一个弯
    x0, y0 = pts[0]
    d = [f"M{x0 - 52:.1f} {y0:.1f} L{x0:.1f} {y0:.1f}"]
    for i in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        if abs(ax - bx) < 1:                                   # 换行
            out = 62 if ax > W / 2 else -62
            d.append(f"C{ax + out:.1f} {ay:.1f} {bx + out:.1f} {by:.1f} {bx:.1f} {by:.1f}")
        else:
            mx = (ax + bx) / 2
            d.append(f"C{mx:.1f} {ay:.1f} {mx:.1f} {by:.1f} {bx:.1f} {by:.1f}")
    ex, ey = pts[-1]
    last_row = (len(pts) - 1) // cols
    dirn = -1 if last_row % 2 else 1
    tail = f"M{ex:.1f} {ey:.1f} L{ex + dirn * 56:.1f} {ey:.1f}"
    out = [
        f'<path class="road" d="{" ".join(d)}" pathLength="1"/>',
        f'<path class="road tail" d="{tail}"/>',
        f'<text class="more-t" x="{ex + dirn * 66:.1f}" y="{ey + 5:.1f}" text-anchor="{"start" if dirn > 0 else "end"}">…</text>',
        f'<text class="start-t" x="{x0 - 52:.1f}" y="{y0 - 12:.1f}">起点</text>',
    ]
    for i, (p, (x, y)) in enumerate(zip(papers, pts)):
        lit = p["status"] == "published"
        name = f'<text class="nm" x="{x:.1f}" y="{y + 30:.1f}" text-anchor="middle">{esc(p["short"])}</text>'
        no = f'<text class="id" x="{x:.1f}" y="{y - 17:.1f}" text-anchor="middle">{esc(p["id"])}</text>'
        if lit:
            out.append(
                f'<a class="node lit" style="--i:{i}" href="papers/{esc(p["slug"])}/index.html">'
                f'<title>{esc(p["id"])} {esc(p["short"])}：已读完，点进去看</title>'
                f'<circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="9"/>'
                f'<circle class="pulse p2" cx="{x:.1f}" cy="{y:.1f}" r="9"/>'
                f'<circle class="core" cx="{x:.1f}" cy="{y:.1f}" r="9"/>{no}{name}</a>')
        else:
            out.append(
                f'<g class="node" style="--i:{i}"><title>{esc(p["id"])} {esc(p["short"])}：还没读</title>'
                f'<circle class="dim" cx="{x:.1f}" cy="{y:.1f}" r="7"/>{no}{name}</g>')
    n_pub = sum(p["status"] == "published" for p in papers)
    label = f"阅读地图：{len(papers)} 篇论文连成一条路，已点亮 {n_pub} 处"
    return (f'<svg class="map {cls}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{label}">'
            + "".join(out) + "</svg>")


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
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<main class="wrap">
  <header class="hero">
    <h1 class="rv">{esc(s["title"])}</h1>
    <p class="lede rv">{lede}</p>
    {"<div class='about rv'>" + about + "</div>" if about else ""}
    {start}
  </header>

  <section class="sec rv">
    <div class="sec-head"><h2>阅读地图</h2><span class="cnt">已点亮 {len(pubs)} / {len(papers)}</span></div>
    <div class="map-box">
      {read_map(papers, 6, 760, 118, "wide")}
      {read_map(papers, 3, 380, 108, "tall")}
    </div>
    <p class="map-cap">每读完一篇，路上就点亮一个地方。亮着的可以点进去看，暗着的还没读到。</p>
  </section>

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
<script src="assets/site.js"></script>
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

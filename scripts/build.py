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


def check_chapters(data):
    errs = []
    chs = data["site"].get("chapters", [])
    nos = [c["no"] for c in chs]
    if nos != list(range(1, len(nos) + 1)):
        errs.append("site.chapters 的章号必须从 1 开始连续递增")
    seq = [p.get("chapter") for p in data["papers"]]
    if any(c not in nos for c in seq):
        errs.append("有论文的 chapter 不在 site.chapters 里")
    elif seq != sorted(seq):
        errs.append("同一章的论文在 papers.json 里必须连续，且按章号排列")
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
        f'<li id="p-{esc(p["id"])}" class="plan" title="{esc(p["title"])} · {esc(p["authors"])}">'
        '<span class="dot" aria-hidden="true"></span>'
        f'<span class="no">{esc(p["id"])}</span>'
        f'<span class="short">{esc(p["short"])}</span>'
        f'<span class="yr">{esc(p["year"])}</span></li>'
    )


def spine(chapters, papers):
    """连载主线：每篇一个点，按章分段。实心 = 已发布，空心 = 计划中。坐标全部由数据算出。"""
    W, x0, gap, chgap, y = 720, 14, 34, 34, 34
    xs, x, prev = {}, x0, None
    for p in papers:
        if prev is not None:
            x += gap + (chgap if p["chapter"] != prev else 0)
        xs[p["id"]] = x
        prev = p["chapter"]
    scale = (W - 2 * x0) / (x - x0)
    for k in xs:
        xs[k] = x0 + (xs[k] - x0) * scale
    out = [f'<line class="ln" x1="{x0}" y1="{y}" x2="{W - x0}" y2="{y}"/>']
    for c in chapters:
        mem = [xs[p["id"]] for p in papers if p["chapter"] == c["no"]]
        mid = (min(mem) + max(mem)) / 2
        out.append(f'<text class="mo sm m" x="{mid:.1f}" y="{y + 32}" text-anchor="middle">{c["no"]:02d}</text>')
    for p in papers:
        cx = xs[p["id"]]
        tip = f'<title>{esc(p["id"])} {esc(p["short"])}</title>'
        if p["status"] == "published":
            out.append(f'<a href="papers/{esc(p["slug"])}/index.html"><circle class="new" cx="{cx:.1f}" cy="{y}" r="7"/>{tip}</a>')
            out.append(f'<text class="ser sm" x="{cx:.1f}" y="{y - 16}" text-anchor="{"start" if cx < 60 else "middle"}">{esc(p["short"])}</text>')
        else:
            out.append(f'<a href="#p-{esc(p["id"])}"><circle class="hole" cx="{cx:.1f}" cy="{y}" r="5.5"/>{tip}</a>')
    n_pub = sum(p["status"] == "published" for p in papers)
    label = f"连载进度：共 {len(papers)} 篇，分 {len(chapters)} 章，已发布 {n_pub} 篇"
    return (f'<svg class="d spine" viewBox="0 0 {W} 76" role="img" aria-label="{label}">'
            + "".join(out) + "</svg>")


def render(data):
    s = data["site"]
    papers = data["papers"]
    chapters = s["chapters"]
    pubs = [p for p in papers if p["status"] == "published"]
    n_pub = len(pubs)
    last = max((p.get("date", "") for p in pubs), default="")
    first = pubs[0] if pubs else None
    lede = "".join(f"<span>{esc(x)}。</span>" for x in s["tagline"].split("。") if x.strip())
    sections = []
    for c in chapters:
        items = [p for p in papers if p["chapter"] == c["no"]]
        lis = "\n".join(card(p) if p["status"] == "published" else plan(p) for p in items)
        sections.append(
            f'<section class="ch"><h2><span class="cno">{c["no"]:02d}</span>{esc(c["title"])}</h2>'
            f'<ol class="list">\n{lis}\n</ol></section>'
        )
    about = "".join(f"<p>{esc(x)}</p>" for x in s.get("about", []))
    start = (f'<a class="start" href="papers/{esc(first["slug"])}/index.html">从第一篇开始：{esc(first["id"])} {esc(first["short"])} →</a>'
             if first else "")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(s["title"])}</title>
<meta name="description" content="{esc(s["tagline"])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<main class="wrap">
  <header class="hero">
    <div class="eyebrow"><span>连载中</span> · <span>已发布 {n_pub} 篇 / 共 {len(papers)} 篇</span>{f" · <span>最近更新 {esc(last)}</span>" if last else ""}</div>
    <h1>{esc(s["title"])}</h1>
    <p class="lede">{lede}</p>
    <figure class="spine-fig">
      {spine(chapters, papers)}
      <figcaption><span class="k"><i class="kd on"></i>已发布</span><span class="k"><i class="kd"></i>计划中</span></figcaption>
    </figure>
    {start}
  </header>
  {"<section class='about'>" + about + "</section>" if about else ""}
{chr(10).join(sections)}
  <footer>
    <p class="legend"><span class="sw n"></span> 蓝色是这篇提出的新方法，<span class="sw o"></span> 赭色是它要替代的旧方法。图都是手写的 SVG。</p>
    <p class="verify">每篇的数字和结论都对照原文核过；标「示意」的是为了讲清机制编的例子。</p>
    <p class="by">{esc(s["author"])}{f' · <a href="{esc(s["repo"])}">源码</a>' if s.get("repo") else ""}</p>
  </footer>
</main>
</body>
</html>
"""


def main():
    data = json.loads((ROOT / "papers.json").read_text(encoding="utf-8"))
    errs = check(data) + check_chapters(data)
    if errs:
        print("FAIL\n  " + "\n  ".join(errs))
        sys.exit(1)
    (ROOT / "index.html").write_text(render(data), encoding="utf-8")
    n_pub = sum(p["status"] == "published" for p in data["papers"])
    print(f"OK  index.html 已生成：共 {len(data['papers'])} 篇，已发布 {n_pub} 篇")


if __name__ == "__main__":
    main()

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


def render(data):
    s = data["site"]
    papers = data["papers"]
    pubs = [p for p in papers if p["status"] == "published"]
    todo = [p for p in papers if p["status"] != "published"]
    last = max((p.get("date", "") for p in pubs), default="")
    first = pubs[0] if pubs else None
    lede = "".join(f"<span>{esc(x)}。</span>" for x in s["tagline"].split("。") if x.strip())
    about = "".join(f"<p>{esc(x)}</p>" for x in s.get("about", []))
    start = (f'<a class="start" href="papers/{esc(first["slug"])}/index.html">从第一篇读起 →</a>' if first else "")
    cards = "\n".join(card(p) for p in pubs)
    rows = "\n".join(plan(p) for p in todo)
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
    <h1>{esc(s["title"])}</h1>
    <p class="lede">{lede}</p>
    {"<div class='about'>" + about + "</div>" if about else ""}
    {start}
  </header>

  <section class="sec">
    <div class="sec-head"><h2>已发布</h2><span class="cnt">{len(pubs)} 篇{f" · 最近更新 {esc(last)}" if last else ""}</span></div>
    <ol class="list">
{cards}
    </ol>
  </section>

  <section class="sec">
    <div class="sec-head"><h2>接下来要读的</h2><span class="cnt">{len(todo)} 篇 · 按这个顺序陆续更新</span></div>
    <ol class="todo">
{rows}
    </ol>
  </section>

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
    errs = check(data)
    if errs:
        print("FAIL\n  " + "\n  ".join(errs))
        sys.exit(1)
    (ROOT / "index.html").write_text(render(data), encoding="utf-8")
    n_pub = sum(p["status"] == "published" for p in data["papers"])
    print(f"OK  index.html 已生成：共 {len(data['papers'])} 篇，已发布 {n_pub} 篇")


if __name__ == "__main__":
    main()

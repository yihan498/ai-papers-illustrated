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


def row(p):
    pub = p["status"] == "published"
    inner = (
        f'<span class="no">{esc(p["id"])}</span>'
        f'<span class="main"><span class="short">{esc(p["short"])}</span>'
        f'<span class="full">{esc(p["title"])}</span>'
        + (f'<span class="one">{esc(p["oneliner"])}</span>' if p.get("oneliner") else "")
        + '</span>'
        f'<span class="side"><span class="yr">{esc(p["year"])}</span>'
        f'<span class="au">{esc(p["authors"])}</span>'
        + ('' if pub else '<span class="soon">待更新</span>')
        + '</span>'
    )
    if pub:
        return f'<li class="pub"><a href="papers/{esc(p["slug"])}/index.html">{inner}</a></li>'
    return f'<li class="plan">{inner}</li>'


def render(data):
    s = data["site"]
    papers = data["papers"]
    n_pub = sum(p["status"] == "published" for p in papers)
    rows = "\n".join(row(p) for p in papers)
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
  <header>
    <div class="eyebrow">Paper by paper · 已更新 {n_pub} 篇</div>
    <h1>{esc(s["title"])}</h1>
    <p class="lede">{esc(s["tagline"])}</p>
  </header>
  <ol class="list">
{rows}
  </ol>
  <footer>{esc(s["author"])} · 每篇的数字和结论都对照原文核过；标「示意」的是为了讲清机制编的例子。</footer>
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

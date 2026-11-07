"""论文页自检：逐张截图 + 机械检查。

用法（必须用 -P，-I 会屏蔽 site-packages 里的 playwright）：
    python3 -P check_page.py <论文页 index.html 路径> <截图输出目录>

做四件事：
1. 每个 SVG 用 XML 解析一遍，抓没闭合的标签
2. 统计 aside/figure/table/ul/ol/div 的开闭数量是否相等
3. 桌面宽度（900px）下逐张截 figure.fig，另外拼成 sheet0.png、sheet1.png… 方便一次看完
4. 手机宽度（390px）下查页面是否横向溢出；查 SVG 里有没有文字超出 viewBox

脚本只能抓「出界、没闭合、溢出」这类机械问题。字形缺失（比如等宽字体没有上标数字，会显示成方块）、
图形被画布裁掉、元素互相压住，这些只能靠看截图发现，所以截图必须看。
"""
import glob
import os
import re
import sys
import xml.dom.minidom

from playwright.sync_api import sync_playwright

TAGS = ["aside", "figure", "table", "ul", "ol", "div"]

OVERFLOW_JS = """()=>{const r=[];document.querySelectorAll('svg.d[viewBox]').forEach((s,i)=>{
const vb=s.viewBox.baseVal;s.querySelectorAll('text').forEach(t=>{const b=t.getBBox();
if(b.x<vb.x-1||b.x+b.width>vb.x+vb.width+1||b.y<vb.y-1||b.y+b.height>vb.y+vb.height+1)
r.push('svg '+i+': '+t.textContent.slice(0,30))})});return r}"""


def static_checks(html):
    ok = True
    svgs = re.findall(r'<svg class="d" viewBox.*?</svg>', html, re.S)
    for i, s in enumerate(svgs):
        try:
            xml.dom.minidom.parseString(s.replace("&lt;", "&#60;").replace("&gt;", "&#62;"))
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"FAIL  SVG {i} 解析失败：{e}")
    print(f"      共 {len(svgs)} 个 SVG")
    for t in TAGS:
        a, b = len(re.findall(rf"<{t}[\s>]", html)), html.count(f"</{t}>")
        if a != b:
            ok = False
            print(f"FAIL  <{t}> 开 {a} 闭 {b}")
    return ok


def contact_sheets(out):
    from PIL import Image

    files = sorted(glob.glob(os.path.join(out, "fig*.png")))
    for k in range(0, len(files), 6):
        ims = [Image.open(f) for f in files[k:k + 6]]
        sheet = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims)), "white")
        y = 0
        for im in ims:
            sheet.paste(im, (0, y))
            y += im.height
        sheet.save(os.path.join(out, f"sheet{k // 6}.png"))


def main():
    page, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    ok = static_checks(open(page, encoding="utf-8").read())
    url = "file://" + page
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 900, "height": 1000})
        ctx.route("**/*", lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())  # 外网字体会卡住加载，直接拦掉
        pg = ctx.new_page()
        pg.goto(url)
        pg.wait_for_timeout(1500)
        for i, f in enumerate(pg.query_selector_all("figure.fig")):
            f.screenshot(path=os.path.join(out, f"fig{i:02d}.png"))
        over = pg.evaluate(OVERFLOW_JS)
        for o in over:
            ok = False
            print(f"FAIL  文字超出 viewBox：{o}")
        ctx2 = b.new_context(viewport={"width": 390, "height": 800})
        ctx2.route("**/*", lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        m = ctx2.new_page()
        m.goto(url)
        m.wait_for_timeout(1000)
        sw = m.evaluate("document.documentElement.scrollWidth")
        if sw > 390:
            ok = False
            print(f"FAIL  手机宽度横向溢出：scrollWidth={sw}（常见原因：<table> 没包在 <div class=\"tbl\"> 里）")
        b.close()
    contact_sheets(out)
    print(("OK    机械检查通过" if ok else "有问题，见上") + f"；截图在 {out}（sheet*.png），必须逐张看")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

"""把网站页面截成小红书内容卡片（1080×1440，3:4）。

用法（在仓库根目录）：
  python3 -P .claude/skills/paper-page/scripts/xhs_cards.py <页面> <输出目录> --list               # 列出所有块和编号，用来挑
  python3 -P .claude/skills/paper-page/scripts/xhs_cards.py <页面> <输出目录> --pick 0-3,10-15,20  # 只截这些块
  python3 -P .claude/skills/paper-page/scripts/xhs_cards.py <页面> <输出目录>                      # 全文（不含 after），用来对照

挑什么（2026-11-10 她定）：只挑主体框架，让人读完有整体印象，不放每个细节的具体介绍。
挑选只在发帖时做，不改网站页面（同日她定）。某一节有块被选中时，这一节的 h2 标题自动带上。

排版（2026-11-10 特辑帖定下）：
- 页面按 600px 宽渲染，SVG 图不用横向滚动；亮色模式；隐藏返回条、目录按钮、目录、「怎么读这一页」、折叠着的延伸框。
- 逐块截图再拼成卡片：图、表、段落不拆开；标题不落在卡片底部，跟着下一块走。
  页面上不相邻的两块之间用固定间距，相邻的保留原间距。
- 装不下时最多缩到约 76%，换来每张尽量填满；单块超过上限的按卡片高度硬切，输出里标「硬切」。
输出 card-NN.png 和总览图 contact.png，并打印每张卡的内容。
"""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

VW = 600                             # 渲染宽度（CSS px）
OUT_W, OUT_H = 1080, 1440
DPR = OUT_W / VW
CARD_H = VW * OUT_H / OUT_W          # 800 CSS px
PAD = 28                             # 卡片上下留白（CSS px）
CAP = CARD_H - 2 * PAD
MIN_SCALE = 0.76
CAP_MAX = CAP / MIN_SCALE
GAP = 22                             # 不相邻的块之间的间距（CSS px）
HEAD = ('H1', 'H2', 'H3', 'H4')

JS_BLOCKS = r"""
(capMax) => {
  for (const el of document.querySelectorAll('body *')) {
    const p = getComputedStyle(el).position;
    if (p === 'fixed' || p === 'sticky') el.style.display = 'none';
  }
  document.querySelectorAll('nav.toc, .howto, nav.eyebrow, footer, details:not([open])')
    .forEach(e => e.style.display = 'none');
  document.querySelectorAll('img').forEach(i => i.loading = 'eager');
  const main = document.querySelector('main.wrap') || document.body;
  const out = []; let sec = 'top';
  const push = (el) => {
    const r = el.getBoundingClientRect();
    if (r.height < 1 || getComputedStyle(el).display === 'none') return;
    // 太高的容器拆成里面的小块，避免硬切和半空卡片
    if (r.height > capMax && ['ASIDE', 'DETAILS', 'DIV', 'SECTION'].includes(el.tagName) && el.children.length > 1) {
      for (const c of el.children) push(c); return;
    }
    if (el.tagName === 'H2') sec = el.id || sec;
    out.push({sec, tag: el.tagName, top: r.top + scrollY, bottom: r.bottom + scrollY,
              text: (el.innerText || '').trim().slice(0, 34).replace(/\s+/g, ' ')});
  };
  for (const el of main.children) {
    if (el.tagName === 'HEADER') { for (const c of el.children) push(c); }
    else push(el);
  }
  return {blocks: out, bg: getComputedStyle(document.body).backgroundColor};
}
"""


def parse_pick(spec):
    out = set()
    for part in spec.split(','):
        a, _, b = part.strip().partition('-')
        out.update(range(int(a), int(b or a) + 1))
    return out


def select(blocks, pick):
    if pick is None:
        return [b for b in blocks if b['sec'] != 'after']
    secs = {blocks[i]['sec'] for i in pick}
    return [b for i, b in enumerate(blocks) if i in pick or (b['tag'] == 'H2' and b['sec'] in secs)]


def gaps(sel, allb):
    """每块和前一块之间的间距：页面上相邻就用原间距，否则用 GAP。"""
    pos = {id(b): i for i, b in enumerate(allb)}
    g = [0]
    for a, b in zip(sel, sel[1:]):
        g.append(b['top'] - a['bottom'] if pos[id(b)] == pos[id(a)] + 1 else GAP)
    return g


def pack(sel, g):
    """贪心装箱：返回 [(start, end_exclusive, hard_cut)]"""
    def h(i, j):
        return sum(sel[k]['bottom'] - sel[k]['top'] + (g[k] if k > i else 0) for k in range(i, j))
    cards, i, n = [], 0, len(sel)
    while i < n:
        j = i
        while j < n and h(i, j + 1) <= CAP:
            j += 1
        if j == i:                       # 第一块就超了：缩放能装就装，否则硬切
            cards.append((i, i + 1, h(i, i + 1) > CAP_MAX)); i += 1; continue
        while j < n and h(i, j + 1) <= CAP_MAX and h(i, j) / CAP < 0.9:
            j += 1                       # 装不满且下一块缩一缩能进来 → 缩放装入
        while j - 1 > i and sel[j - 1]['tag'] in HEAD:
            j -= 1                       # 标题不落在卡片底部
        cards.append((i, j, False)); i = j
    return cards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page'); ap.add_argument('out')
    ap.add_argument('--pick', help='要截的块编号，如 0-3,10-15,20（编号见 --list）')
    ap.add_argument('--list', action='store_true', help='只列出块，不截图')
    a = ap.parse_args()
    page = Path(a.page).resolve(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': VW, 'height': 1000}, device_scale_factor=DPR, color_scheme='light')
        pg.route('**/fonts.g*/**', lambda r: r.abort())
        pg.goto(page.as_uri(), wait_until='domcontentloaded')
        pg.add_style_tag(content='html{scroll-behavior:auto!important}*{animation:none!important;transition:none!important}')
        pg.evaluate(JS_BLOCKS, CAP_MAX)
        for y in range(0, pg.evaluate('document.body.scrollHeight'), 900):
            pg.evaluate(f'scrollTo(0,{y})'); pg.wait_for_timeout(40)
        pg.wait_for_function('[...document.images].every(i => i.complete)', timeout=15000)
        info = pg.evaluate(JS_BLOCKS, CAP_MAX)   # 图片加载后重新量
        allb = info['blocks']

        if a.list:
            for k, x in enumerate(allb):
                print(f'{k:3d} [{x["sec"]}] {x["tag"]:7s} '
                      f'{x["bottom"] - x["top"]:5.0f}px  {x["text"]}')
            b.close(); return

        sel = select(allb, parse_pick(a.pick) if a.pick else None)
        g = gaps(sel, allb)
        bg = tuple(int(v) for v in info['bg'][info['bg'].index('(') + 1:-1].split(',')[:3])
        for f in out.glob('card-*.png'):
            f.unlink()

        def shot(y0, y1):
            tmp = out / '_raw.png'
            pg.screenshot(path=str(tmp), full_page=True, clip={'x': 0, 'y': y0, 'width': VW, 'height': y1 - y0})
            im = Image.open(tmp).convert('RGB'); tmp.unlink(); return im

        avail = OUT_H - 2 * PAD * DPR
        idx, thumbs = 0, []
        for s, e, hard in pack(sel, g):
            if hard:
                y0, y1 = sel[s]['top'], sel[s]['bottom']
                groups = [([shot(y, min(y1, y + CAP))], [0]) for y in range(int(y0), int(y1), int(CAP))]
            else:
                groups = [([shot(sel[k]['top'], sel[k]['bottom']) for k in range(s, e)],
                           [0] + [g[k] for k in range(s + 1, e)])]
            for ims, gl in groups:
                tot = sum(im.height for im in ims) + sum(round(x * DPR) for x in gl)
                stack = Image.new('RGB', (OUT_W, tot), bg); y = 0
                for im, gp in zip(ims, gl):
                    y += round(gp * DPR); stack.paste(im, (0, y)); y += im.height
                sc = min(1.0, avail / stack.height)
                if sc < 1:
                    stack = stack.resize((round(stack.width * sc), round(stack.height * sc)), Image.LANCZOS)
                card = Image.new('RGB', (OUT_W, OUT_H), bg)
                card.paste(stack, ((OUT_W - stack.width) // 2, round(PAD * DPR)))
                idx += 1
                fn = out / f'card-{idx:02d}.png'; card.save(fn); thumbs.append(card.resize((270, 360)))
                print(f'{fn.name}  [{sel[s]["sec"]}] {sel[s]["text"]} … 缩放 {sc:.0%} 填满 {stack.height / avail:.0%}'
                      + ('  硬切，要人看' if hard else ''))
        b.close()

    cols = 6; rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 280, rows * 370), (200, 200, 200))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * 280 + 5, (i // cols) * 370 + 5))
    sheet.save(out / 'contact.png')
    print(f'OK  共 {idx} 张，总览 {out / "contact.png"}')


if __name__ == '__main__':
    main()

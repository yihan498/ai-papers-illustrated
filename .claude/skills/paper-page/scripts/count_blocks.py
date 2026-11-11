"""旧页重排对账：数页面里的内容块，重排前后对比，防止搬的时候丢东西。
用法：python3 count_blocks.py <page.html> [--save base.json | --diff base.json]"""
import json, re, sys
from html.parser import HTMLParser

TAGS = ("svg", "img", "table", "li", "figure", "details", "h2", "h3", "p")

class C(HTMLParser):
    def __init__(s):
        super().__init__(); s.n = {t: 0 for t in TAGS}; s.n["formula"] = 0; s.text = []
        s.skip = 0
    def handle_starttag(s, t, a):
        if t in ("style", "script"): s.skip += 1
        if t in s.n: s.n[t] += 1
        cls = dict(a).get("class") or ""
        if re.search(r"\b(eq|formula|math)\b", cls): s.n["formula"] += 1
    def handle_endtag(s, t):
        if t in ("style", "script"): s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.text.append(d)

def count(path):
    c = C(); c.feed(open(path, encoding="utf-8").read())
    txt = re.sub(r"\s+", "", "".join(c.text))
    c.n["chars"] = len(txt)
    c.n["numbers"] = sorted(set(re.findall(r"\d+(?:\.\d+)?", txt)))
    return c.n

if __name__ == "__main__":
    n = count(sys.argv[1])
    if "--save" in sys.argv:
        json.dump(n, open(sys.argv[sys.argv.index("--save") + 1], "w"), ensure_ascii=False)
    if "--diff" in sys.argv:
        b = json.load(open(sys.argv[sys.argv.index("--diff") + 1]))
        bad = False
        for k in b:
            if k == "numbers":
                lost = sorted(set(b[k]) - set(n[k]), key=lambda x: float(x))
                print(f"数字：重排前 {len(b[k])} 个，丢失 {len(lost)} 个" + (f"：{' '.join(lost)}" if lost else ""))
                bad |= bool(lost)
            else:
                mark = "" if n[k] >= b[k] else "  ← 变少"
                if k == "chars": mark = "" if n[k] >= b[k] * 0.95 else "  ← 少了 5% 以上"
                print(f"{k:8} {b[k]:>6} → {n[k]:<6}{mark}"); bad |= bool(mark) and k not in ("p", "h2", "h3")
        print("FAIL：有内容可能丢了，逐项找回或说明" if bad else "OK：没有内容块变少")
    else:
        print({k: v for k, v in n.items() if k != "numbers"}, "数字", len(n["numbers"]))

---
name: paper-page
description: 把一篇读完的论文解读（learning/reading/ai-foundational-papers/NNN-xxx/explanation.md）做成「AI 论文解读」网站上的一页图解，经用户审核后发布到 GitHub Pages。触发词：第 N 篇读完了做成网页、上新第 N 篇、把 NNN 发到网站、和 self-media 连起来的部分。
---

# paper-page · 解读 → 网站图解页 → 发布

## 要产出什么，为什么
用户读完一篇论文后，`explanation.md` 是**她自己的讲义**，按她的疑问组织。网站页是**给第一次读的人**看的：按原文章节顺序走，概念就地解释，配手绘图。两者内容同源，组织方式不同。

网站是 self-media 的内容底座（见仓库 `NOTES.local.md`）：它积累注意力和信任，小红书从这里取材、往这里导流。所以页面的标准是「宗旨」：别人用同样的 AI 工具一句话做不出来。这一页的辨识度来自**手写 SVG + 只用蓝赭两色的固定图形词汇**，不能用图库图、AI 插画、通用图标。

已做过：001 NPLM（2026-11-06）、002 Seq2Seq（2026-11-07）。以它们为样板。

## 前提
- 用户明确说这篇**读完了**（README 进度表里「读原文」✅）。只有解读、她还没读完的不做。
- 内容只取自 `explanation.md`（以及原文核对数字），不另外加新知识点。

## 流程

### 1 · 读输入
1. 读 `explanation.md` 全文。
2. 读上一篇已发布的页面 `papers/<上一篇>/index.html`，看结构和 CSS（`<head>` 到 `<main class="wrap">` 这一段整体复用）。
3. 弄清原文的章节骨架（解读里引用的「原文 3.3 节」「Table 1」就是线索），页面按这个骨架排。

### 2 · 搭骨架
- 复制上一篇第 1 行到 `<main class="wrap">`，只改 `<title>`（「简称 图解」）和 CSS 顶部注释里「蓝 = … 赭 = …」那一句。CSS、箭头 marker 都不动，保证全站一套系统。
- `<header>`：返回链接「← AI 论文解读 · NNN」→ h1（**一句白话**讲这篇做了什么，不用论文名，如「预测下一个词」「把一句话变成另一句话」）→ lede（一段话：谁、哪年、做了一件什么事、为什么重要，加粗句用蓝色）→ meta（作者 · 会议 · 两个色块图例）→ 图 0（全篇最核心的那张结构图）→ toc → howto「怎么读这一页」。
- 正文 h2 = 原文的大节（`<h2 id="s1"><span class="no">1</span>…`），h3 带编号的和原文章节号一致，不带编号的是为了好读加的分段。最后一个 h2 是 `id="after"` 的「读完之后（原文之外）」：当时背景、后来发展、前后篇衔接。

### 3 · 把解读的内容放进原文骨架
| 解读里的东西 | 放到页面哪里 |
|---|---|
| 第 1 节「技术基础」里的概念 | 拆开，放到原文**第一次用到它**的位置，做成 `<aside class="anno">` 📎 注解 |
| 第 2、3 节问题与方法 | 按原文顺序进对应的 h2/h3 |
| 第 4 节实验 | 原文实验节；「怎么读这些数字」保留成有序列表 |
| 推算、后世评价、历史 | `<aside class="ext">` 🧭 延伸，或「读完之后」 |
| 第 5–7 节 | 「读完之后」 |

写法要求：
- 讲因果不讲结论，和解读一致；作者的假说写明是假说。
- 001 讲过的概念一句话带过，必要时链接 `../001-nplm/index.html`。
- 数字只用解读里有出处的；编的例子标「示意」；推算的标「推算」。
- 解读者补充的观点写成「我补充的」，这是她的站，用她的第一人称。
- 中文行文：短句，不用破折号连缀，不堆形容词。

### 4 · 画图（每篇 10–14 张）
- 每张图用 `<figure class="fig">` + `<span class="tag">图 N · 标题</span>` + `<div class="sv"><svg class="d" viewBox="0 0 680 H" role="img" aria-label="完整描述">` + `<figcaption>`。宽固定 680，高按内容定。
- **只用已有的 class 上色**（填充/描边 `.new .newT .newS .old .oldT .oldS .soft .softS .card .ln .dash .ring .mutS .mutF .ink .inkF`，文字 `.tn .to .on .m .mo`，字号 `.sm .lg .xl`，箭头 `marker-end="url(#ah)"`/`#ahN`/`#ahO`），不写死颜色，暗色模式才会自动跟着变。蓝 = 本文的新方法，赭 = 要被替代的旧方法，其余用灰。
- 选图标准：解读里每个「机制」至少一张（结构、公式的小数字例子、对比），实验的核心表画成柱状图并标出基线。
- 首页缩略图：从页面里挑最代表这篇的一张，简化成 `papers/<slug>/thumb.svg`（viewBox 240×180，同样只用 class），格式照 001、002。

**已经踩过的坑**（画的时候就避开）：
- **等宽字体没有上标数字**：`.mo` 里写「1.1⁵⁰」会显示成方块。用 `<tspan dy="-6" style="font-size:9px">50</tspan><tspan dy="6">…</tspan>`。
- **超出 viewBox 的图形会被直接裁掉**：圆、弧线、箭头的最外沿都要算进画布，比如圆心 y + 半径要小于 viewBox 高度。脚本只查文字出界，查不出图形被裁。
- **点或文字压在虚线圈的描边上**：椭圆要比里面的内容宽出 12px 以上。
- **嵌套弧线的数字标签**会压在外层弧线上：给文字加 `style="paint-order:stroke;stroke:var(--card);stroke-width:5px"` 描一圈底色。
- **`<table>` 要包在 `<div class="tbl">` 里**，否则表格的最小宽度 520px 会在手机上把整页撑宽。

### 5 · 自检（交给用户之前必须做）
```
python3 scripts/build.py                     # 在仓库根目录，看到 OK
python3 -P .claude/skills/paper-page/scripts/check_page.py papers/<slug>/index.html <scratchpad>/shots
```
脚本过了之后，**用 Read 逐张看 `sheet*.png`**，查重叠、裁切、方块字、颜色用错。有问题改完再跑一遍，直到截图没问题。

### 6 · 交给用户审核
- 先在 `papers.json` 里把这篇改成 `"status": "published"`，填 `oneliner`（一句白话，和 001「给每个词一个坐标，再用平滑的函数猜下一个词。」同一种语气）和 `date`，再跑 build 生成首页。**这时候不 commit、不 push。**
- 给她页面的 `file:///D:/...` 链接，说清：标题、配图清单、数字出处、自检结果、首页改了什么。
- 她改意见就改，改完重跑第 5 步。

### 7 · 发布（她说「可以发」之后）
```
git add papers/<slug> papers.json index.html
git commit -m "上新 NNN 简称：图解页、首页卡片缩略图"     # 末尾带 Co-Authored-By
git push
```
GitHub Pages 约 1 分钟后更新，网址 https://yihan498.github.io/ai-papers-illustrated/papers/<slug>/ 。她没说可以发之前，不能 push。

### 8 · 收尾
- 本 skill 里「已经踩过的坑」有新的就融进去（重构，不追加章节）；「已做过」加上这一篇。
- 共用样式稳定了（3 篇以上都一样）再考虑抽到 `assets/`，见 NOTES 的待细化。

## 不做的事
- 小红书配套帖：用户说过不用跟这个流程绑（2026-11-07）。她单独提出时再走 self-media 的流水线。
- 不改 `explanation.md` 和学习区的任何文件；发现解读有错，告诉她，由 paper-reading 流程去改。

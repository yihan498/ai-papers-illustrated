---
name: paper-page
description: 把一篇读完的论文解读（learning/reading/ai-foundational-papers/NNN-xxx/explanation.md）做成「AI 论文解读」网站上的一页图解，经用户审核后发布到 GitHub Pages。也用于跨篇特辑（learning 区 special-xxx/explanation.md）。触发词：第 N 篇读完了做成网页、上新第 N 篇、把 NNN 发到网站、把特辑推到网站、和 self-media 连起来的部分。
---

# paper-page · 解读 → 网站图解页 → 发布

## 要产出什么，为什么
用户读完一篇论文后，`explanation.md` 是**她自己的讲义**，按她的疑问组织。网站页是**给第一次读的人**看的：按原文章节顺序走，概念就地解释，配手绘图。两者内容同源，组织方式不同。

**特辑**是第二种页：跨篇梳理一个主题（如 Transformer），不对应单篇论文。它不按原文章节走，按特辑 explanation.md 自己的论证链排；放在 `specials/<slug>/`，在 `papers.json` 的 `specials` 里登记，首页单独一栏「特辑」，不占阅读地图。下文没特别说明的规则，特辑同样适用。

网站是 self-media 的内容底座（见仓库 `NOTES.local.md`）：它积累注意力和信任，小红书从这里取材。小红书帖里放的是**正文截图卡片，不是链接**：链接在正文里点不了，还有引流嫌疑；她 2026-11-10 发现放正文的帖收藏明显更高，所以每篇发帖前都要出卡片（第 8 步）。所以页面的标准是「宗旨」：别人用同样的 AI 工具一句话做不出来。这一页的辨识度来自**手写 SVG + 只用蓝赭两色的固定图形词汇**，不能用图库图、AI 插画、通用图标。

已做过：001 NPLM（2026-11-06）、002 Seq2Seq（2026-11-07）、003 Bahdanau 注意力（2026-11-07）、004 Transformer（2026-11-09）、005 Adam（2026-11-10）；特辑：Transformer（2026-11-10，`specials/transformer/`）。以它们为样板，003、004 是目前最完整的版本（有原图和公式）。

## 前提
- 用户明确说这篇**读完了**（README 进度表里「读原文」✅）。只有解读、她还没读完的不做。
- 内容只取自 `explanation.md`（以及原文核对数字），不另外加新知识点。
- 特辑不需要「读完」这一步，用户让推就做；但它引用的篇里，只有已发布的能加链接，没上线的只写编号（如「第 007 篇」），并在 howto 里说明。之后每上线一篇，回到特辑页把这篇的编号改成链接，howto 里「还没上线」的范围同步缩小（005 上线时补过）。

## 流程

### 1 · 读输入
1. 读 `explanation.md` 全文。
2. 读上一篇已发布的页面 `papers/<上一篇>/index.html`，看结构和 CSS（`<head>` 到 `<main class="wrap">` 这一段整体复用）。
3. 弄清原文的章节骨架（解读里引用的「原文 3.3 节」「Table 1」就是线索），页面按这个骨架排。

### 2 · 搭骨架
- 复制上一篇第 1 行到 `<main class="wrap">`，只改 `<title>`（「简称 图解」）和 CSS 顶部注释里「蓝 = … 赭 = …」那一句。CSS、箭头 marker 都不动，保证全站一套系统。顶部返回条和章节目录由共用的 `assets/paper-toc.js` 自动生成，页面里不用写；引用它的 `?v=N` 版本号照抄上一篇。改了 `assets/` 里的共用文件，所有页面的 `?v=N` 一起加 1，否则读者的浏览器会继续用缓存的旧版（2026-11-07 踩过：旧的返回按钮删了，用户那边还在）。
- 特辑放在 `specials/<slug>/`，和 `papers/<slug>/` 同样深两层，`../../assets/` 照用；链论文页写 `../../papers/<slug>/index.html`，借用论文页的原图也这样引用，不复制文件。
- `<header>`：返回链接「← AI 论文解读 · NNN」（特辑写「· 特辑」，顶部返回条会显示成「特辑 · 标题」）→ h1（**一句白话**讲这篇做了什么，不用论文名，如「预测下一个词」「把一句话变成另一句话」）→ lede（一段话：谁、哪年、做了一件什么事、为什么重要，加粗句用蓝色）→ meta（作者 · 会议 · 两个色块图例）→ 图 0（全篇最核心的那张结构图）→ toc → howto「怎么读这一页」。
- 正文 h2 = 原文的大节（`<h2 id="s1"><span class="no">1</span>…`），h3 带编号的和原文章节号一致，不带编号的是为了好读加的分段。最后一个 h2 是 `id="after"` 的「读完之后（原文之外）」：当时背景、后来发展、前后篇衔接。

### 3 · 把解读的内容放进原文骨架
| 解读里的东西 | 放到页面哪里 |
|---|---|
| 第 1 节「技术基础」里的概念 | 拆开，放到原文**第一次用到它**的位置，做成 `<aside class="anno">` 📎 注解 |
| 第 2、3 节问题与方法 | 按原文顺序进对应的 h2/h3 |
| 第 4 节实验 | 原文实验节只留**结论**（每条一个 h3 + 一张图），数据集、训练设置、超参数压进一个折叠的 `<details class="ext">` |
| 推算、后世评价、历史 | `<aside class="ext">` 🧭 延伸，或「读完之后」 |
| 第 5–7 节 | 「读完之后」 |

**内容分配：读者是外行，内在逻辑最重要。**用户读 003 时反馈：实验设计和数学公式最容易把人搞混，搞清「为什么这样做」比细节重要。所以：
- 每个机制按「白话逻辑 → 小数字算例图 → 公式 → 符号表」的顺序写。公式**要在正文里给出来**（用户明确要求过，不能为了好读删掉），用 `<div class="formula">`，原文出处写成 `<span class="fsrc">（原文 Eq. N，…）</span>`，手机上会自动换行；公式后面紧跟一张表，逐个解释符号。
- 读懂主线不需要的细节（GRU 门控、maxout 等内部结构）放 `<aside class="ext">`，标明「跳过不影响理解」。
- 实验：正文只留几条结论，细节全部折叠。

写法要求：
- 讲因果不讲结论，和解读一致；作者的假说写明是假说。
- 001 讲过的概念一句话带过，必要时链接 `../001-nplm/index.html`。
- 出处写篇号，不写学习区解读的小节号：explanation.md 里的「004 篇 3.2」是讲义的编号，和网站页的章节对不上。
- 数字只用解读里有出处的；编的例子标「示意」；推算的标「推算」。页面里的表格（尤其解读里没完整列出、需要补全的原文表）要逐格对照原文文本，不凭记忆录入；交给子 agent 做时，主会话交付前要再对一遍（004 的 agent 自报「按记忆录入」，复核后才放心）。
- 解读者补充的观点写成「我补充的」，这是她的站，用她的第一人称。
- 中文行文：短句，不用破折号连缀，不堆形容词。

### 4 · 画图（每篇 10–14 张，含原图）
- 每张图用 `<figure class="fig">` + `<span class="tag">图 N · 标题</span>` + `<div class="sv"><svg class="d" viewBox="0 0 680 H" role="img" aria-label="完整描述">` + `<figcaption>`。宽固定 680，高按内容定。
- **只用已有的 class 上色**（填充/描边 `.new .newT .newS .old .oldT .oldS .soft .softS .card .ln .dash .ring .mutS .mutF .ink .inkF`，文字 `.tn .to .on .m .mo`，字号 `.sm .lg .xl`，箭头 `marker-end="url(#ah)"`/`#ahN`/`#ahO`），不写死颜色，暗色模式才会自动跟着变。蓝 = 本文的新方法，赭 = 要被替代的旧方法，其余用灰。
- 选图标准：解读里每个「机制」至少一张（结构、公式的小数字例子、对比），实验的核心表画成柱状图并标出基线。
- **原文的典型图表放原图**（结构图、核心曲线、可视化结果，每篇 2–3 张），比手画更直观，也让读者能对照原文。做法：用 fitz 从 PDF 截区域 `page.get_pixmap(dpi=200, clip=fitz.Rect(...))`，存成 `papers/<slug>/orig-figN.png`；截完一定打开看，第一次截常会切掉坐标标签、带进图注文字，或者截进上下相邻图的残字（004 附录 Figure 4 截下半幅时顶部带进了上半幅的残字）。原图一般转灰度；靠颜色区分内容的（如不同注意力头的连线、005 实验图里几种优化器的曲线）保留彩色。fitz 在 `python3 -I` 下导入不了，在 scratchpad 目录里用普通 `python3` 跑。页面里写 `<figure class="fig"><span class="tag">原文 Figure N · 标题</span><img class="orig" src="orig-figN.png" alt="完整描述"><figcaption>这张图在说什么：<b>一句结论</b>。怎么看：……图源：作者 年份 原文。</figcaption></figure>`，CSS 照抄 003 的 `.fig img.orig`（白底加内边距，暗色模式下也清楚）。原文 PDF 只读不改。
- **讲解视频**（用户自己另外做的，如 2026-11-10 用豆包为特辑生成的视频）：只放在她指定的那一页，不顺手往别的页、首页加入口。放在 header 的 howto 下面，`<figure class="fig"><span class="tag">视频 · …（时长）</span><video controls preload="metadata" playsinline poster="video-poster.jpg"><source src="xxx-video.mp4" type="video/mp4"></video>`，CSS 加 `.fig video{display:block;width:100%;height:auto;border-radius:6px;background:#000}`；图注写明谁生成的、「画面和旁白以下文为准」。文件改成英文名，超过 50MB 先问她（GitHub 单文件上限 100MB）；检查 moov 在文件开头（能边下边播），不在就 `ffmpeg -c copy -movflags +faststart`；封面用 ffmpeg 取一帧。上线前每 10 秒抽一帧拼图看完，没有转写工具时如实告诉她旁白没逐句核对。视频不代替手画图，它和「辨识度来自手写 SVG」的宗旨有张力，要不要常规化由她定。
- 手画图和原图可以配对：手画的简化版讲原理，原图就放在旁边。照着原图估着画的曲线要标「示意，形状按原文 Figure N 估画」。
- 首页缩略图：从页面里挑最代表这篇的一张，简化成 `papers/<slug>/thumb.svg`（viewBox 240×180，同样只用 class），格式照 001、002。缩略图会内联进首页，首页只加载 `assets/site.css`，那里只有 `.m .sm .mo .ln .new .newT .soft .softS .mutF`，用之前先 grep。其余 class（`.newS`、`.dash`、`.old*` 等）在首页不生效，图形会直接消失，改写成内联变量：蓝线 `style="fill:none;stroke:var(--new)"`，赭色 `stroke:var(--old)`，虚线 `stroke-dasharray:5 4`（2026-11-10 特辑踩过虚线；005 的蓝线用了 `.newS` 没显示，顺带发现 002、003 的缩略图连线也一直缺）。做完要截首页卡片看一眼：首页卡片有动画，元素截图会一直等「稳定」，先注入 `*{animation:none!important}`。

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
脚本会拦掉外网请求（Google Fonts 会让截图一直卡住），截图里用的是本地回退字体，属于正常情况。脚本过了之后，**用 Read 逐张看 `sheet*.png`**，查重叠、裁切、方块字、颜色用错。还要另外截两张：390px 宽的手机版（看公式、长行有没有被截断）和暗色模式（`color_scheme='dark'`，看原图和配色）。自己写的截图脚本同样要拦 Google Fonts（`page.route('**/fonts.g*/**', lambda r: r.abort())`），`goto` 用 `wait_until='domcontentloaded'`，否则会卡在等字体上；截图前先把 `scrollBehavior` 设成 `auto`，否则会截到滚动到一半的画面。原图是 `loading="lazy"`，`sheet*.png` 里可能是一片空白（005 的 Figure 1 就是这样），这时读 `img.naturalWidth` 确认图确实加载了，或在手机版截图里逐段滚动后再看。有问题改完再跑一遍，直到截图没问题。

### 6 · 交给用户审核
- 先在 `papers.json` 里把这篇改成 `"status": "published"`，填 `oneliner`（一句白话，和 001「给每个词一个坐标，再用平滑的函数猜下一个词。」同一种语气）和 `date`，再跑 build 生成首页。特辑则在 `specials` 数组里加一条（slug、short、covers、title、oneliner、status、date），build 会检查 `specials/` 下的文件夹都登记过。**这时候不 commit、不 push。**
- 给她页面的 `file:///D:/...` 链接，说清：标题、配图清单、数字出处、自检结果、首页改了什么。
- 她改意见就改，改完重跑第 5 步。

### 7 · 发布（她说「可以发」之后）
```
git add papers/<slug> papers.json index.html        # 原图 png 在 papers/<slug>/ 里，一起带上；特辑换成 specials/<slug>
git commit -m "上新 NNN 简称：图解页、首页卡片缩略图"     # 末尾带 Co-Authored-By
git push
```
GitHub Pages 约 1 分钟后更新，网址 https://yihan498.github.io/ai-papers-illustrated/papers/<slug>/ 。她没说可以发之前，不能 push。

### 8 · 小红书卡片（她发帖之前必做）
**挑什么（2026-11-10 她定）：只挑主体框架，读完能有整体印象，不放每个细节的具体介绍。挑选只在发帖时做，不为发帖改网站页面。** 一帖 6–10 张为宜，上限 17 张（小红书一帖最多 18 张，封面占 01）。
- 要：标题 + lede + meta + 图 0 → 原文要解决的问题（几个「毛病」各配一张图）→ 核心机制（算法 / 结构图 + 「每个零件对应什么问题」那张表）→ 关键改进的直觉（一段 + 一张图）→ 最核心的一组实验结论 → 原文结论。
- 不要：注解框、延伸框、公式推导与符号表、逐步数值演算、理论证明、次要实验、扩展章节、「读完之后」。
- 先列出全部块和编号，挑好后用 `--pick` 截图（某一节有块被选中，这一节的 h2 自动带上）：
```
python3 -P .claude/skills/paper-page/scripts/xhs_cards.py papers/<slug>/index.html .preview/xhs/<slug> --list
python3 -P .claude/skills/paper-page/scripts/xhs_cards.py papers/<slug>/index.html .preview/xhs/<slug> --pick 0-3,10-15,20
python3 -P .claude/skills/paper-page/scripts/xhs_cards.py papers/<slug>/index.html .preview/xhs/<slug>              # 全文对照
```
- 脚本把页面按 600px 宽、亮色截成 1080×1440 的卡片：逐块截图再拼，图、表、段落不拆开，标题跟着正文走，最多缩到 76% 换填满；目录、howto、折叠的延伸框不进卡片。`.preview/` 在 .gitignore 里，不进仓库。005 帖的 `--pick` 编号记在 self-media 帖子备注里，可以当样板（7 张）。
- 用 Read 看 `contact.png`，有「硬切」标记或半空的卡要逐张看。
- 复制进 self-media 对应帖子的 `images/`，从 `02.png` 起按顺序编号（帖子文件夹用 `desk.py new` 建），在「备注」里记下截自哪个提交、`--pick` 了哪些块。封面 `01.png` 用 self-media 的封面模板（`06-craft/visual/cover-system/`），只换文字。
- 帖子正文里写**这篇论文的地位**（2026-11-10 她要求，突出这篇为什么值得读）：3–4 条，它改变了什么、后来成了什么（谁在用）、出现之前大家怎么做、有什么争议。只取 explanation.md 的「当时的技术背景」「后来发展到什么程度」和原文结论，不写引用数、排名这类讲解里没有的数字。正文不放链接，提网站就写「主页的网站」。最后增删由她定。

### 9 · 收尾
- 本 skill 里「已经踩过的坑」有新的就融进去（重构，不追加章节）；「已做过」加上这一篇。
- 共用样式稳定了（3 篇以上都一样）再考虑抽到 `assets/`，见 NOTES 的待细化。

## 不做的事
- 小红书帖的文字：不跟这个流程绑（2026-11-07），她提出时走 self-media 的流水线。卡片截图例外，见第 8 步（2026-11-10 改）。
- 不改 `explanation.md` 和学习区的任何文件；发现解读有错，告诉她，由 paper-reading 流程去改。

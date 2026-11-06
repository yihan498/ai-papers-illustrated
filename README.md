# AI 论文解读

按技术演进的顺序，一篇一篇读懂今天的大模型是怎么来的。每篇论文一页，文字讲透，图画清楚。

网址：https://yihan498.github.io/ai-papers-illustrated/

## 结构
```
papers.json                唯一的数据源：系列信息 + 每篇论文的条目（状态 planned / published）
index.html                 首页，由脚本生成，不要手改
papers/<slug>/index.html   每篇一页，单文件、样式内联，可以单独打开
assets/site.css            首页样式
assets/paper-toc.css/.js   论文页的章节导航（宽屏左侧栏 / 手机「目录」按钮），从 h2/h3 自动生成
scripts/build.py           生成首页 + 一致性检查
.nojekyll                  让 GitHub Pages 原样发布
```

## 上新一篇
1. 页面放到 `papers/<编号-简称>/index.html`，顶部放「← AI 论文解读」返回链接，链接写到 `../../index.html`（照 001 的写法）。`<head>` 里引用 `../../assets/paper-toc.css`，`</body>` 前引用 `../../assets/paper-toc.js`；正文放在 `<main>` 里，大节用 `<h2><span class="no">1</span>标题</h2>`，小节用 `<h3><span class="no">1.1</span>标题</h3>`，章节导航会自动生成
2. 在 `papers.json` 里把这篇改成 `"status": "published"`，填好 `oneliner` 和 `date`
3. 运行 `python3 scripts/build.py`，看到 OK 才算过
4. commit + push，GitHub Pages 约 1 分钟后更新

## 页面约定
- 蓝色代表本篇的新方法，赭色代表旧方法，全页只用这两种颜色
- 图全部手写 SVG
- 章节导航只认 `<main>` 里的 h2 / h3，别的层级不进目录
- 实验数字、参数量出自原文；为了讲清机制编的数字标「示意」

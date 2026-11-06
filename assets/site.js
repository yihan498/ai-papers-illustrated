// 首页进场动画：元素滚动到视口里时加 .in，CSS 负责渐显。不支持 IntersectionObserver 时直接全部显示。
(function () {
  var els = document.querySelectorAll(".rv, .todo li");
  if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { rootMargin: "0px 0px -8% 0px" });
  els.forEach(function (e, i) { e.style.setProperty("--d", (e.closest(".hero") ? i : 0)); io.observe(e); });
})();

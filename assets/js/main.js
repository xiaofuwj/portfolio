/* =========================================================
   肖辅 · UX 设计师个人网站 — 交互脚本 (v0.1 static)
   依赖：无第三方库。严格尊重 prefers-reduced-motion。
   ========================================================= */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isTouch = window.matchMedia("(hover: none)").matches;

  /* ---------- 1. 导航滚动玻璃态 ---------- */
  var nav = document.getElementById("nav");
  function onScroll() {
    if (!nav) return;
    if (window.scrollY > 80) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- 2. 移动端抽屉 ---------- */
  var burger = document.getElementById("burger");
  var drawer = document.getElementById("drawer");
  if (burger && drawer) {
    burger.addEventListener("click", function () {
      var open = drawer.classList.toggle("open");
      burger.classList.toggle("open", open);
    });
    drawer.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        drawer.classList.remove("open");
        burger.classList.remove("open");
      });
    });
  }

  /* ---------- 3. 数字 count-up ---------- */
  function easeOutQuint(t) { return 1 - Math.pow(1 - t, 5); }
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduceMotion) { el.textContent = target + suffix; return; }
    var dur = 800, start = performance.now();
    function tick(now) {
      var p = Math.min((now - start) / dur, 1);
      var val = Math.round(easeOutQuint(p) * target);
      el.textContent = val + suffix;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  /* ---------- 4. 滚动进场 (reveal + stagger) ---------- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  if (reduceMotion || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        // stagger: 同父节点下前面已出现的 .reveal 个数
        var siblings = Array.prototype.slice.call(el.parentNode.querySelectorAll(":scope > .reveal"));
        var idx = siblings.indexOf(el);
        el.style.transitionDelay = Math.min(idx, 6) * 80 + "ms";
        el.classList.add("in");
        if (el.querySelector("[data-count]") || el.hasAttribute("data-count")) {
          var counter = el.hasAttribute("data-count") ? el : el.querySelector("[data-count]");
          countUp(counter);
        }
        io.unobserve(el);
      });
    }, { threshold: 0.2, rootMargin: "0px 0px -10% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  }
  // 数据带自身可能直接是 .reveal 且带 data-count
  document.querySelectorAll(".stat[data-count]").forEach(function (el) {
    if (reduceMotion) countUp(el);
  });

  /* ---------- 5. 作品筛选 ---------- */
  var filters = document.getElementById("filters");
  var grid = document.getElementById("caseGrid");
  if (filters && grid) {
    var btns = Array.prototype.slice.call(filters.querySelectorAll(".filter"));
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".case-card"));
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        btns.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        var f = btn.getAttribute("data-filter");
        cards.forEach(function (card) {
          var show = f === "all" || card.getAttribute("data-chapter") === f;
          card.style.display = show ? "" : "none";
          if (show && !reduceMotion) {
            card.classList.remove("in");
            requestAnimationFrame(function () { card.classList.add("in"); });
          }
        });
      });
    });
  }

  /* ---------- 6. 案例页侧边进度高亮 ---------- */
  var progressLinks = document.querySelectorAll("#caseProgress a");
  if (progressLinks.length && "IntersectionObserver" in window) {
    var sections = Array.prototype.slice.call(progressLinks).map(function (a) {
      return document.querySelector(a.getAttribute("href"));
    }).filter(Boolean);
    var pio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var id = "#" + entry.target.id;
          progressLinks.forEach(function (a) {
            a.classList.toggle("active", a.getAttribute("href") === id);
          });
        }
      });
    }, { threshold: 0.4 });
    sections.forEach(function (s) { pio.observe(s); });
  }

  /* ---------- 7. Hero 鼠标视差 (仅桌面) ---------- */
  var heroBig = document.querySelector(".hero__big");
  if (heroBig && !reduceMotion && !isTouch) {
    window.addEventListener("mousemove", function (e) {
      var cx = window.innerWidth / 2, cy = window.innerHeight / 2;
      var dx = (e.clientX - cx) / cx, dy = (e.clientY - cy) / cy;
      heroBig.style.transform = "translate(" + dx * 12 + "px," + dy * 8 + "px)";
    });
  }

  /* ---------- 8. 联系页交互 ---------- */
  var copyMail = document.getElementById("copyMail");
  if (copyMail) {
    copyMail.addEventListener("click", function () {
      var mail = "156944098@qq.com";
      if (navigator.clipboard) {
        navigator.clipboard.writeText(mail).then(function () {
          copyMail.textContent = "已复制 ✓";
          setTimeout(function () { copyMail.textContent = "复制邮箱"; }, 1800);
        });
      }
    });
  }
  var showPhone = document.getElementById("showPhone");
  var phoneEl = document.getElementById("phone");
  if (showPhone && phoneEl) {
    showPhone.addEventListener("click", function () {
      phoneEl.textContent = "176 8879 2206";
      phoneEl.style.color = "var(--t-title)";
      showPhone.style.display = "none";
    });
  }
})();

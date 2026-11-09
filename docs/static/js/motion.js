// Lawnix mechanical motion. Needs gsap + ScrollTrigger loaded before this file.
// Every effect degrades: with prefers-reduced-motion, the final assembled state is shown and
// counters display their end values.
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGsap = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";

  // ---------- counters (gauges) ----------
  function runCounters() {
    var els = document.querySelectorAll("[data-count]");
    if (!els.length) return;
    els.forEach(function (el) {
      var end = parseFloat(el.getAttribute("data-count"));
      var decimals = (el.getAttribute("data-count").split(".")[1] || "").length;
      var suffix = el.getAttribute("data-suffix") || "";
      if (reduce || !hasGsap) { el.textContent = end.toFixed(decimals) + suffix; return; }
      var obj = { v: 0 };
      gsap.to(obj, {
        v: end, duration: 1.4, ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 85%", once: true },
        onUpdate: function () { el.textContent = obj.v.toFixed(decimals) + suffix; }
      });
    });
  }

  // ---------- exploded view: parts assemble on scroll ----------
  function runExploded() {
    var section = document.querySelector(".exploded");
    if (!section) return;
    var parts = section.querySelectorAll(".part");
    var labels = section.querySelectorAll(".exploded-label");
    var readout = section.querySelector(".exploded-readout b");
    var dims = section.querySelectorAll(".dim");
    var dimLabels = section.querySelectorAll(".dim-label");

    dims.forEach(function (d) {
      var len = d.getTotalLength();
      d.style.strokeDasharray = len; d.style.strokeDashoffset = reduce ? 0 : len;
    });

    if (reduce || !hasGsap) {
      labels.forEach(function (l) { l.classList.add("on"); });
      dimLabels.forEach(function (l) { l.style.opacity = 1; });
      if (readout) readout.textContent = "100%";
      return;
    }

    // start displaced
    parts.forEach(function (p) {
      var s = (p.getAttribute("data-start") || "0 0").split(" ").map(Number);
      gsap.set(p, { x: s[0], y: s[1], opacity: 0.35 });
    });
    dimLabels.forEach(function (l) { gsap.set(l, { opacity: 0 }); });

    var tl = gsap.timeline({
      scrollTrigger: {
        trigger: section, start: "top 68px", end: "+=" + (parts.length * 420),
        pin: true, scrub: 0.6, anticipatePin: 1, invalidateOnRefresh: true,
        onUpdate: function (st) { if (readout) readout.textContent = Math.round(st.progress * 100) + "%"; }
      }
    });
    parts.forEach(function (p, i) {
      tl.to(p, { x: 0, y: 0, opacity: 1, duration: 1, ease: "power2.inOut" }, i * 0.9);
      if (labels[i]) {
        tl.call(function () { labels.forEach(function (l, j) { l.classList.toggle("on", j === i); }); }, null, i * 0.9 + 0.5);
      }
    });
    var t = parts.length * 0.9;
    dims.forEach(function (d) { tl.to(d, { strokeDashoffset: 0, duration: 0.8, ease: "power2.out" }, t); });
    tl.to(dimLabels, { opacity: 1, duration: 0.4, stagger: 0.1 }, t + 0.4);
    tl.call(function () { labels.forEach(function (l) { l.classList.remove("on"); }); labels[labels.length - 1] && labels[labels.length - 1].classList.add("on"); }, null, t + 0.2);
    // small breathing room at the end so the finished drawing holds
    tl.to({}, { duration: 0.6 });
  }

  // ---------- width comparison bars ----------
  function runBars() {
    var bars = document.querySelectorAll(".wbar-fill");
    if (!bars.length) return;
    bars.forEach(function (b) {
      var pct = parseFloat(b.getAttribute("data-pct")) / 100;
      if (reduce || !hasGsap) { b.style.transform = "scaleX(" + pct + ")"; return; }
      gsap.fromTo(b, { scaleX: 0 }, {
        scaleX: pct, duration: 1.2, ease: "power3.out", transformOrigin: "left center",
        scrollTrigger: { trigger: b, start: "top 85%", once: true }
      });
    });
  }

  // ---------- hero blueprint overlay ----------
  function runHero() {
    var lines = document.querySelectorAll(".hero-bp .bp-line");
    if (!lines.length) return;
    lines.forEach(function (d) {
      var len = d.getTotalLength ? d.getTotalLength() : 400;
      d.style.strokeDasharray = len;
      d.style.strokeDashoffset = reduce ? 0 : len;
    });
    if (reduce || !hasGsap) return;
    gsap.to(lines, { strokeDashoffset: 0, duration: 1.1, ease: "power2.out", stagger: 0.12, delay: 0.3 });
    gsap.fromTo(".hero-bp .bp-tag", { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.12, delay: 1.0, ease: "power2.out" });
  }

  // ---------- section headings: machined slide ----------
  function runHeadings() {
    if (reduce || !hasGsap) return;
    document.querySelectorAll(".mech-head").forEach(function (h) {
      gsap.fromTo(h, { clipPath: "inset(0 100% 0 0)" }, {
        clipPath: "inset(0 0% 0 0)", duration: 0.9, ease: "power3.out",
        scrollTrigger: { trigger: h, start: "top 85%", once: true }
      });
    });
  }

  function init() {
    runCounters(); runExploded(); runBars(); runHero(); runHeadings();
    if (hasGsap) { ScrollTrigger.refresh(); }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.addEventListener("load", function () { if (hasGsap) ScrollTrigger.refresh(); });
})();

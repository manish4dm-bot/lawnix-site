// Lawnix site script: menu, reveal-on-scroll, gallery, signup form.
(function () {
  "use strict";

  // Mobile menu
  var menuBtn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      menuBtn.innerHTML = open ? '<i class="ph ph-x" aria-hidden="true"></i>' : '<i class="ph ph-list" aria-hidden="true"></i>';
    });
  }

  // Reveal on scroll (IntersectionObserver, no scroll listener)
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -5% 0px", threshold: 0 });
    reveals.forEach(function (el) { io.observe(el); });
    // Fail-safe: nothing stays hidden if the observer never fires.
    setTimeout(function () { reveals.forEach(function (el) { el.classList.add("in"); }); }, 2500);
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  // Product gallery thumbnails
  var main = document.querySelector(".gallery-main img");
  var thumbs = document.querySelectorAll(".gallery-thumbs button");
  thumbs.forEach(function (b) {
    b.addEventListener("click", function () {
      thumbs.forEach(function (t) { t.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      var img = b.querySelector("img");
      if (main && img) { main.src = img.getAttribute("data-full") || img.src; main.alt = img.alt; }
    });
  });

  // Signup form: posts to the configured endpoint, else opens an email.
  var form = document.querySelector("form[data-signup]");
  if (form) {
    var msg = form.querySelector(".form-msg");
    var endpoint = form.getAttribute("data-endpoint");
    form.addEventListener("submit", function (ev) {
      var email = form.querySelector('input[type="email"]').value.trim();
      if (!email) { return; }
      if (!endpoint) {
        ev.preventDefault();
        window.location.href = "mailto:" + form.getAttribute("data-mail") + "?subject=Lawnix%20launch%20list&body=Please%20add%20" + encodeURIComponent(email) + "%20to%20the%20launch%20list.";
        if (msg) { msg.textContent = "Opening your email app. Send the message and you are on the list."; }
        return;
      }
      ev.preventDefault();
      var btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      fetch(endpoint, { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(form) })
        .then(function (r) { if (!r.ok) { throw new Error("bad"); } form.reset(); if (msg) { msg.textContent = "You are on the list. Watch your inbox."; } })
        .catch(function () { if (msg) { msg.textContent = "That did not go through. Email " + form.getAttribute("data-mail") + " and we will add you."; } })
        .finally(function () { btn.disabled = false; });
    });
  }

  // ---------- Conversion measurement ----------
  // Every event goes to window.dataLayer (Google Tag Manager format) and a
  // "lawnix:track" DOM event. gtag and Meta pixel are called only if present.
  window.dataLayer = window.dataLayer || [];
  function track(name, data) {
    data = data || {};
    data.event = "lawnix_" + name;
    window.dataLayer.push(data);
    try { document.dispatchEvent(new CustomEvent("lawnix:track", { detail: data })); } catch (e) { /* old browsers */ }
    if (typeof window.gtag === "function") { window.gtag("event", name, data); }
    if (name === "buy_click" && typeof window.fbq === "function") {
      window.fbq("track", "InitiateCheckout", { value: parseFloat(data.value) || 0, currency: "USD", content_ids: [data.product] });
    }
  }
  window.lawnixTrack = track;
  track("page_view", { path: window.location.pathname });
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest ? ev.target.closest("[data-track]") : null;
    if (!el) { return; }
    track(el.getAttribute("data-track"), {
      placement: el.getAttribute("data-placement") || "",
      product: el.getAttribute("data-product") || "",
      value: el.getAttribute("data-value") || "",
      href: el.getAttribute("href") || ""
    });
  });
  var sections = document.querySelectorAll("[data-section]");
  if ("IntersectionObserver" in window && sections.length) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { track("section_view", { section: e.target.getAttribute("data-section") }); seen.unobserve(e.target); }
      });
    }, { threshold: 0.35 });
    sections.forEach(function (s) { seen.observe(s); });
  }

  // ---------- Before / after slider ----------
  document.querySelectorAll("[data-ba]").forEach(function (fig) {
    var stage = fig.querySelector(".ba-stage");
    var range = fig.querySelector(".ba-range");
    if (!stage || !range) { return; }
    var touched = false;
    function set() { stage.style.setProperty("--pos", range.value + "%"); }
    range.addEventListener("input", function () {
      set();
      if (!touched) { touched = true; track("before_after_drag", {}); }
    });
    set();
  });

  // ---------- Mobile sticky buy bar ----------
  var sticky = document.querySelector("[data-sticky]");
  if (sticky && "IntersectionObserver" in window) {
    sticky.hidden = false;
    document.body.classList.add("has-sticky");
    var hero = document.querySelector(".lp-hero");
    var finalCta = document.querySelector(".lp-final");
    var state = { hero: true, final: false };
    var watch = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.target === hero) { state.hero = e.isIntersecting; }
        if (e.target === finalCta) { state.final = e.isIntersecting; }
      });
      sticky.classList.toggle("show", !state.hero && !state.final);
    }, { threshold: 0 });
    if (hero) { watch.observe(hero); }
    if (finalCta) { watch.observe(finalCta); }
  }

  // Mark current nav item
  var path = window.location.pathname.replace(/index\.html$/, "");
  document.querySelectorAll(".nav a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href && href !== "/" && path.indexOf(href) === 0) { a.setAttribute("aria-current", "page"); }
  });
})();

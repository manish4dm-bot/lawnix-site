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

  // Mark current nav item
  var path = window.location.pathname.replace(/index\.html$/, "");
  document.querySelectorAll(".nav a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href && href !== "/" && path.indexOf(href) === 0) { a.setAttribute("aria-current", "page"); }
  });
})();

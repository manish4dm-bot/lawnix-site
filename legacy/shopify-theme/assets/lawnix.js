/* ═══════════════════════════════════════════════════════════
   LAWNIX™ — Animation & Interaction Engine
   Heavy-duty tools · Lawn leveling rake · Living Garden
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ─────────────────────────────────────────
     1. STICKY NAV + SCROLL SHADOW
  ───────────────────────────────────────── */
  const nav = document.querySelector('.site-header');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
  }

  /* ─────────────────────────────────────────
     2. SOIL PARTICLE SYSTEM (hero background)
     — Small glowing specks float up like disturbed earth
  ───────────────────────────────────────── */
  function initParticles() {
    const hero = document.querySelector('.hero');
    if (!hero || window.innerWidth < 768) return;

    const count = window.innerWidth > 1200 ? 28 : 18;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('span');
      const isLeaf = Math.random() > 0.72;
      p.className = `hero-particle${isLeaf ? ' leaf' : ''}`;
      const size = isLeaf ? (5 + Math.random() * 5) : (1.5 + Math.random() * 2.5);
      p.style.setProperty('--x',     `${8 + Math.random() * 84}%`);
      p.style.setProperty('--y',     `${45 + Math.random() * 50}%`);
      p.style.setProperty('--dur',   `${4 + Math.random() * 7}s`);
      p.style.setProperty('--delay', `${Math.random() * 10}s`);
      p.style.setProperty('--drift', `${(Math.random() - 0.5) * 90}px`);
      p.style.setProperty('--size',  `${size}px`);
      hero.appendChild(p);
    }
  }
  initParticles();

  /* ─────────────────────────────────────────
     3. HERO PARALLAX GLOW — follows mouse
  ───────────────────────────────────────── */
  function initParallax() {
    const glow = document.querySelector('.hero-glow');
    if (!glow || window.innerWidth < 900) return;
    let ticking = false;
    document.addEventListener('mousemove', (e) => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const x = (e.clientX / window.innerWidth  - 0.5) * 55;
        const y = (e.clientY / window.innerHeight - 0.5) * 35;
        glow.style.transform = `translateY(-50%) translate(${x}px, ${y}px)`;
        ticking = false;
      });
    }, { passive: true });
  }
  initParallax();

  /* ─────────────────────────────────────────
     4. STATS COUNTER — numbers count up on entry
     — Like a heavy-duty gauge powering up
  ───────────────────────────────────────── */
  function animateCounter(el) {
    const raw     = el.textContent.trim();
    const numStr  = raw.replace(/[^\d.]/g, '');
    const num     = parseFloat(numStr);
    if (!num || el.dataset.counted) return;
    el.dataset.counted = '1';

    const suffix  = raw.replace(/[\d.]/g, '');
    const isFloat = numStr.includes('.');
    const dur     = 1800;
    const start   = performance.now();

    const easeOutCubic = t => 1 - Math.pow(1 - t, 3);

    function update(now) {
      const progress = Math.min((now - start) / dur, 1);
      const eased    = easeOutCubic(progress);
      const current  = isFloat
        ? (eased * num).toFixed(1)
        : Math.floor(eased * num);
      el.textContent = current + suffix;
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = raw;
        el.classList.add('counted');
        setTimeout(() => el.classList.remove('counted'), 600);
      }
    }
    requestAnimationFrame(update);
  }

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        animateCounter(e.target);
        counterObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.6 });

  document.querySelectorAll('.stat-number, .stat-num').forEach(el => {
    counterObserver.observe(el);
  });

  /* ─────────────────────────────────────────
     5. BLADE-CUT HEADING REVEAL
     — Section headings wipe in left-to-right like a rake blade
  ───────────────────────────────────────── */
  const headingObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting && !e.target.classList.contains('blade-visible')) {
        e.target.classList.add('blade-visible');
        headingObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.section-heading').forEach(el => {
    headingObserver.observe(el);
  });

  /* ─────────────────────────────────────────
     6. STAGGERED GRID REVEAL
     — Grid items spring in one by one like tools being laid out
  ───────────────────────────────────────── */
  const gridSelectors = [
    '.features-grid .feat-card',
    '.reviews-grid .review-card',
    '.trust-grid .trust-badge-card',
    '.values-grid .value-card',
    '.products-grid .p-card',
    '.fp-specs .fp-spec-row',
    '.stats-row .stat-block',
  ];

  const staggerObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const container = e.target;
      const items     = Array.from(container.querySelectorAll(
        '.feat-card, .review-card, .trust-badge-card, .value-card, .p-card, .fp-spec-row, .stat-block'
      ));
      items.forEach((item, i) => {
        setTimeout(() => {
          item.style.transitionDelay = `${i * 75}ms`;
          item.classList.add('item-visible');
        }, i * 55);
      });
      staggerObserver.unobserve(container);
    });
  }, { threshold: 0.08 });

  document.querySelectorAll(
    '.features-grid, .reviews-grid, .trust-grid, .values-grid, .products-grid, .fp-specs, .stats-row'
  ).forEach(grid => staggerObserver.observe(grid));

  /* ─────────────────────────────────────────
     7. GENERAL REVEAL (non-grid elements)
  ───────────────────────────────────────── */
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        revealObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  /* ─────────────────────────────────────────
     8. BUTTON RIPPLE — impact wave on click
     — Like a tool striking the ground
  ───────────────────────────────────────── */
  function initRipple() {
    const targets = document.querySelectorAll(
      '.btn-primary, .btn-cart, .sticky-atc-btn, .p-btn-cart, .newsletter-btn, .footer-nl-btn, .quick-add'
    );
    targets.forEach(btn => {
      btn.addEventListener('pointerdown', function(e) {
        const existing = this.querySelector('.btn-ripple');
        if (existing) existing.remove();

        const ripple = document.createElement('span');
        ripple.className = 'btn-ripple';
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2.2;
        ripple.style.cssText = `
          width:${size}px; height:${size}px;
          left:${e.clientX - rect.left - size/2}px;
          top:${e.clientY - rect.top - size/2}px;
        `;
        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 700);
      });
    });
  }
  initRipple();

  /* ─────────────────────────────────────────
     9. MAGNETIC BUTTON — buttons attract cursor
     — Like metal drawn to a powerful tool
  ───────────────────────────────────────── */
  function initMagnetic() {
    if (window.innerWidth < 900) return;
    document.querySelectorAll('.btn-primary, .btn-ghost, .nav-cta').forEach(btn => {
      btn.addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const cx   = rect.left + rect.width  / 2;
        const cy   = rect.top  + rect.height / 2;
        const dx   = (e.clientX - cx) * 0.28;
        const dy   = (e.clientY - cy) * 0.28;
        this.style.transform = `translate(${dx}px, ${dy}px)`;
      });
      btn.addEventListener('mouseleave', function() {
        this.style.transform = '';
      });
    });
  }
  initMagnetic();

  /* ─────────────────────────────────────────
     10. CURSOR GLOW — green aura follows cursor
     — Dew drop on the lawn
  ───────────────────────────────────────── */
  function initCursorGlow() {
    if (window.innerWidth < 900 || window.matchMedia('(pointer: coarse)').matches) return;
    const glow = document.createElement('div');
    glow.style.cssText = `
      position:fixed; pointer-events:none; z-index:9999;
      width:24px; height:24px; border-radius:50%;
      border:1.5px solid rgba(120,190,32,0.5);
      background:rgba(120,190,32,0.06);
      transform:translate(-50%,-50%);
      transition:width 0.3s, height 0.3s, border-color 0.3s, opacity 0.3s;
      mix-blend-mode:screen;
      top:-50px; left:-50px; opacity:0;
    `;
    document.body.appendChild(glow);

    let visible = false;
    document.addEventListener('mousemove', (e) => {
      glow.style.left = e.clientX + 'px';
      glow.style.top  = e.clientY + 'px';
      if (!visible) { glow.style.opacity = '1'; visible = true; }
    }, { passive: true });

    // Expand on hovering interactive elements
    document.querySelectorAll('a, button, .feat-card, .review-card, .p-card').forEach(el => {
      el.addEventListener('mouseenter', () => {
        glow.style.width  = '48px';
        glow.style.height = '48px';
        glow.style.borderColor = 'rgba(120,190,32,0.8)';
        glow.style.background  = 'rgba(120,190,32,0.1)';
      });
      el.addEventListener('mouseleave', () => {
        glow.style.width  = '24px';
        glow.style.height = '24px';
        glow.style.borderColor = 'rgba(120,190,32,0.5)';
        glow.style.background  = 'rgba(120,190,32,0.06)';
      });
    });
  }
  initCursorGlow();

  /* ─────────────────────────────────────────
     11. RAKE TINE CURSOR TRAIL
     — Tiny tine marks follow the cursor like the rake just passed
  ───────────────────────────────────────── */
  function initTineTrail() {
    if (window.innerWidth < 900 || window.matchMedia('(pointer: coarse)').matches) return;
    const hero = document.querySelector('.hero');
    if (!hero) return;

    hero.addEventListener('mousemove', (e) => {
      const rect = hero.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Drop 5 tine marks spread vertically
      for (let i = 0; i < 5; i++) {
        const tine = document.createElement('span');
        tine.style.cssText = `
          position:absolute; pointer-events:none; z-index:2;
          left:${x - 2}px; top:${y - 10 + i * 5}px;
          width:1.5px; height:4px;
          background:rgba(120,190,32,0.4);
          border-radius:1px;
          transform:rotate(15deg);
          animation:soilFloat 1.2s ease forwards;
        `;
        hero.appendChild(tine);
        setTimeout(() => tine.remove(), 1200);
      }
    });
  }
  // Throttled version — only fire every 80ms
  let tineThrottle = 0;
  const hero = document.querySelector('.hero');
  if (hero && window.innerWidth >= 900) {
    hero.addEventListener('mousemove', (e) => {
      if (Date.now() - tineThrottle < 80) return;
      tineThrottle = Date.now();
      initTineTrail._handler && initTineTrail._handler(e);
    }, { passive: true });
  }
  initTineTrail();

  /* ─────────────────────────────────────────
     12. SCROLL PROGRESS RAKE
     — Thin green line at top tracking scroll like a rake making a pass
  ───────────────────────────────────────── */
  function initScrollRake() {
    const bar = document.createElement('div');
    bar.style.cssText = `
      position:fixed; top:0; left:0; height:2px; width:0%; z-index:2000;
      background:linear-gradient(90deg, var(--green-dark, #5a9018), var(--green, #78BE20), var(--green-light, #9fd44a));
      transition:width 0.1s linear;
      pointer-events:none;
    `;
    document.body.appendChild(bar);
    window.addEventListener('scroll', () => {
      const scrollTop  = window.scrollY;
      const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
      const pct        = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width  = pct + '%';
    }, { passive: true });
  }
  initScrollRake();

  /* ─────────────────────────────────────────
     13. SECTION TINE DIVIDERS
     — Decorative rake-tine rule under each section eyebrow
  ───────────────────────────────────────── */
  const eyebrowObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('leveled');
        eyebrowObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.8 });

  document.querySelectorAll('.section-eyebrow').forEach(el => {
    eyebrowObserver.observe(el);
  });

  /* ─────────────────────────────────────────
     14. MOBILE HAMBURGER MENU
  ───────────────────────────────────────── */
  const hamburgerBtn  = document.getElementById('hamburger-btn');
  const mobileMenu    = document.getElementById('mobile-menu');
  const mobileOverlay = document.getElementById('mobile-overlay');

  function openMobileMenu() {
    mobileMenu?.classList.add('open');
    mobileOverlay?.classList.add('open');
    document.body.style.overflow = 'hidden';
    hamburgerBtn?.setAttribute('aria-expanded', 'true');
    hamburgerBtn?.querySelector('.ham-icon')?.style.setProperty('display','none');
    hamburgerBtn?.querySelector('.close-icon')?.style.setProperty('display','block');
  }
  function closeMobileMenu() {
    mobileMenu?.classList.remove('open');
    mobileOverlay?.classList.remove('open');
    document.body.style.overflow = '';
    hamburgerBtn?.setAttribute('aria-expanded', 'false');
    hamburgerBtn?.querySelector('.ham-icon')?.style.setProperty('display','block');
    hamburgerBtn?.querySelector('.close-icon')?.style.setProperty('display','none');
  }
  hamburgerBtn?.addEventListener('click', () => {
    mobileMenu?.classList.contains('open') ? closeMobileMenu() : openMobileMenu();
  });
  mobileOverlay?.addEventListener('click', closeMobileMenu);
  document.querySelectorAll('.mobile-nav-link').forEach(l => l.addEventListener('click', closeMobileMenu));

  /* ─────────────────────────────────────────
     15. FAQ ACCORDION
  ───────────────────────────────────────── */
  document.querySelectorAll('.faq-item').forEach(item => {
    item.querySelector('.faq-q')?.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(o => {
        o.classList.remove('open');
        o.querySelector('.faq-q')?.setAttribute('aria-expanded','false');
      });
      if (!isOpen) {
        item.classList.add('open');
        item.querySelector('.faq-q')?.setAttribute('aria-expanded','true');
      }
    });
  });

  /* ─────────────────────────────────────────
     16. STICKY ADD TO CART
  ───────────────────────────────────────── */
  const stickyAtc  = document.getElementById('sticky-atc');
  const mainAddBtn = document.querySelector('.btn-cart');
  if (stickyAtc && mainAddBtn) {
    new IntersectionObserver(([e]) => {
      stickyAtc.classList.toggle('visible', !e.isIntersecting);
      stickyAtc.setAttribute('aria-hidden', e.isIntersecting ? 'true' : 'false');
    }, { rootMargin: '-60px 0px 0px 0px' }).observe(mainAddBtn);

    document.getElementById('sticky-atc-btn')?.addEventListener('click', () => {
      document.getElementById('product-form')?.querySelector('[type="submit"]')?.click();
    });
  }

  /* ─────────────────────────────────────────
     17. VARIANT OPTION BUTTONS
  ───────────────────────────────────────── */
  document.querySelectorAll('.options-row').forEach(group => {
    group.querySelectorAll('.opt-btn:not(.sold-out)').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.opt-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  });

  /* ─────────────────────────────────────────
     18. QUANTITY ADJUSTER
  ───────────────────────────────────────── */
  document.querySelectorAll('.qty-wrap').forEach(wrap => {
    const input = wrap.querySelector('input');
    wrap.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        const delta = btn.dataset.action === 'minus' ? -1 : 1;
        input.value = Math.max(1, Math.min(99, parseInt(input.value || 1) + delta));
      });
    });
  });

  /* ─────────────────────────────────────────
     19. PRODUCT THUMBNAILS
  ───────────────────────────────────────── */
  document.querySelectorAll('.thumbs').forEach(thumbsEl => {
    thumbsEl.querySelectorAll('.thumb').forEach(thumb => {
      thumb.addEventListener('click', () => {
        thumbsEl.querySelectorAll('.thumb').forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');
        const mainImg = thumb.closest('.product-gallery')?.querySelector('.main-img img');
        if (mainImg && thumb.dataset.src) {
          mainImg.style.opacity = '0';
          mainImg.style.transition = 'opacity 0.25s';
          setTimeout(() => {
            mainImg.src = thumb.dataset.src;
            mainImg.style.opacity = '1';
          }, 200);
        }
      });
    });
  });

  /* ─────────────────────────────────────────
     20. ADD TO CART (AJAX)
  ───────────────────────────────────────── */
  document.querySelectorAll('.btn-cart, .p-btn-cart, .quick-add').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const variantId = btn.dataset.variantId
        || btn.closest('[data-variant-id]')?.dataset.variantId
        || document.getElementById('variant-select')?.value;
      const qty = parseInt(document.querySelector('.qty-wrap input')?.value || 1);
      if (!variantId) return;

      btn.disabled = true;
      const original = btn.innerHTML;
      btn.innerHTML = '<span style="display:inline-block;animation:spin 0.6s linear infinite">⟳</span> Adding...';

      try {
        const res = await fetch('/cart/add.js', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: variantId, quantity: qty })
        });
        if (res.ok) {
          btn.innerHTML = '✓ Added!';
          btn.style.background = 'var(--green-light)';
          updateCartCount();
          setTimeout(() => {
            btn.innerHTML = original;
            btn.style.background = '';
            btn.disabled = false;
          }, 2200);
        } else {
          btn.innerHTML = original;
          btn.disabled = false;
        }
      } catch {
        btn.innerHTML = original;
        btn.disabled = false;
      }
    });
  });

  /* ─────────────────────────────────────────
     21. CART COUNT BADGE
  ───────────────────────────────────────── */
  async function updateCartCount() {
    try {
      const cart   = await (await fetch('/cart.js')).json();
      const bubble = document.querySelector('.cart-bubble');
      if (bubble) {
        bubble.textContent  = cart.item_count;
        bubble.style.display = cart.item_count > 0 ? 'flex' : 'none';
        // Mini bounce animation
        bubble.style.transform = 'scale(1.5)';
        setTimeout(() => bubble.style.transform = '', 300);
      }
    } catch {}
  }
  updateCartCount();

  /* ─────────────────────────────────────────
     22. FILTER BUTTONS + SORT
  ───────────────────────────────────────── */
  document.querySelectorAll('.filter-group').forEach(group => {
    group.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  });
  document.getElementById('sort-by')?.addEventListener('change', function() {
    window.location = window.location.pathname + '?sort_by=' + this.value;
  });

  /* ─────────────────────────────────────────
     23. SIDEBAR CHECKBOXES
  ───────────────────────────────────────── */
  document.querySelectorAll('.check-item').forEach(item => {
    item.addEventListener('click', () => item.classList.toggle('checked'));
  });

  /* ─────────────────────────────────────────
     24. CART PAGE (AJAX update/remove)
  ───────────────────────────────────────── */
  document.querySelectorAll('.qty-wrap button[data-key]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const key   = btn.dataset.key;
      const input = document.querySelector(`input[data-key="${key}"]`);
      if (!input) return;
      const delta  = btn.dataset.action === 'minus' ? -1 : 1;
      const newQty = Math.max(0, parseInt(input.value || 1) + delta);
      input.value  = newQty;
      await cartChange(key, newQty);
    });
  });
  document.querySelectorAll('.cart-remove-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const row = btn.closest('.cart-item');
      if (row) { row.style.opacity = '0.4'; row.style.transform = 'translateX(-20px)'; row.style.transition = '0.3s ease'; }
      await cartChange(btn.dataset.key, 0);
    });
  });
  async function cartChange(key, qty) {
    await fetch('/cart/change.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: key, quantity: qty })
    });
    window.location.reload();
  }

});

/* ─────────────────────────────────────────
   SPIN KEYFRAME (for loading button)
───────────────────────────────────────── */
const spinStyle = document.createElement('style');
spinStyle.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
document.head.appendChild(spinStyle);

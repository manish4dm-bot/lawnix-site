// LAWNIX™ Shared JS — Cart, Search, Nav
// Version 1.0.0

const LAWNIX_PRODUCTS = [
  { id:'lx30', sku:'LX-30', name:'Lawn Leveling Rake LX-30', shortName:'30" Leveling Rake', price:54.99, comparePrice:69.99, url:'product-lx30.html', category:'Lawn Leveler', icon:'🌿', tags:['rake','leveling','stainless','lawn','30 inch'] },
  { id:'lx48', sku:'LX-48', name:'Leveling Rake LX-48', shortName:'48" Leveling Rake', price:74.99, comparePrice:94.99, url:'product-lx48.html', category:'Lawn Leveler', icon:'🌿', tags:['rake','leveling','stainless','lawn','48 inch','wide'] },
  { id:'rc01', sku:'RC-01', name:'Rotary Cultivator & Hand Tiller', shortName:'Rotary Cultivator 2-in-1', price:39.99, comparePrice:52.99, url:'product-cultivator.html', category:'Cultivator', icon:'⚙️', tags:['cultivator','tiller','aerate','weed','garden','rotary'] }
];

/* ─────────────────────────────────────────────────────────────
   CART FUNCTIONS
───────────────────────────────────────────────────────────── */

function lxGetCart() {
  try { return JSON.parse(localStorage.getItem('lawnix_cart') || '[]'); } catch(e) { return []; }
}

function lxSaveCart(cart) {
  localStorage.setItem('lawnix_cart', JSON.stringify(cart));
  lxUpdateCartBadge();
}

function lxAddToCart(id, qty, size) {
  qty = parseInt(qty) || 1;
  const product = LAWNIX_PRODUCTS.find(p => p.id === id);
  if (!product) return;

  const cart = lxGetCart();
  const key = id + (size ? '__' + size : '');
  const existing = cart.find(item => item.id === id && item.size === (size || ''));

  if (existing) {
    existing.qty += qty;
  } else {
    cart.push({
      id: product.id,
      sku: product.sku,
      name: product.name,
      price: product.price,
      comparePrice: product.comparePrice,
      qty: qty,
      size: size || '',
      url: product.url,
      icon: product.icon
    });
  }

  lxSaveCart(cart);
  lxShowAddedToast(product.name, product.url);
}

function lxRemoveFromCart(id, size) {
  let cart = lxGetCart();
  cart = cart.filter(item => !(item.id === id && item.size === (size || '')));
  lxSaveCart(cart);
}

function lxUpdateCartQty(id, size, qty) {
  const cart = lxGetCart();
  const item = cart.find(i => i.id === id && i.size === (size || ''));
  if (item) {
    item.qty = Math.max(1, parseInt(qty) || 1);
    lxSaveCart(cart);
  }
}

function lxGetCount() {
  return lxGetCart().reduce((sum, item) => sum + item.qty, 0);
}

function lxGetSubtotal() {
  return lxGetCart().reduce((sum, item) => sum + (item.price * item.qty), 0);
}

/* ─────────────────────────────────────────────────────────────
   CART BADGE
───────────────────────────────────────────────────────────── */

function lxUpdateCartBadge() {
  const count = lxGetCount();
  document.querySelectorAll('.cart-count-badge').forEach(badge => {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  });
}

/* ─────────────────────────────────────────────────────────────
   TOAST NOTIFICATION
───────────────────────────────────────────────────────────── */

let _toastTimer = null;

function lxShowAddedToast(productName, productUrl) {
  let toast = document.getElementById('lx-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'lx-toast';
    toast.style.cssText = [
      'position:fixed',
      'bottom:28px',
      'right:28px',
      'background:#181818',
      'border:1px solid #78BE20',
      'border-radius:10px',
      'padding:18px 22px',
      'z-index:99999',
      'max-width:320px',
      'width:calc(100vw - 56px)',
      'box-shadow:0 12px 48px rgba(0,0,0,0.7)',
      'font-family:Barlow,sans-serif',
      'transition:opacity 0.35s,transform 0.35s',
      'opacity:0',
      'transform:translateY(16px)',
      'pointer-events:auto'
    ].join(';');
    document.body.appendChild(toast);
  }

  toast.innerHTML = `
    <div style="display:flex;align-items:flex-start;gap:14px;">
      <div style="width:38px;height:38px;background:rgba(120,190,32,0.12);border:1px solid rgba(120,190,32,0.3);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">✓</div>
      <div style="flex:1;min-width:0;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:14px;font-weight:900;letter-spacing:1px;text-transform:uppercase;color:#78BE20;margin-bottom:3px;">Added to Cart!</div>
        <div style="font-size:13px;color:#ccc;margin-bottom:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${productName}</div>
        <a href="${productUrl ? 'cart.html' : 'cart.html'}" style="display:inline-block;background:#78BE20;color:#090909;text-decoration:none;padding:8px 18px;border-radius:4px;font-family:'Barlow Condensed',sans-serif;font-size:13px;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;transition:background 0.2s;" onmouseover="this.style.background='#9fd44a'" onmouseout="this.style.background='#78BE20'">View Cart →</a>
      </div>
      <button onclick="document.getElementById('lx-toast').style.opacity='0';document.getElementById('lx-toast').style.transform='translateY(16px)';" style="background:none;border:none;color:#555;cursor:pointer;font-size:18px;line-height:1;padding:0;flex-shrink:0;margin-top:-2px;" aria-label="Close">×</button>
    </div>
  `;

  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  });

  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(16px)';
  }, 3000);
}

/* ─────────────────────────────────────────────────────────────
   SEARCH OVERLAY
───────────────────────────────────────────────────────────── */

let _searchOverlay = null;

function lxInitSearch() {
  // Create overlay lazily on first open
}

function lxOpenSearch() {
  if (!_searchOverlay) {
    _searchOverlay = document.createElement('div');
    _searchOverlay.id = 'lx-search-overlay';
    _searchOverlay.innerHTML = `
      <div id="lx-search-backdrop" style="position:fixed;inset:0;background:rgba(0,0,0,0.85);backdrop-filter:blur(6px);z-index:100000;" onclick="lxCloseSearch()"></div>
      <div id="lx-search-panel" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:min(640px,calc(100vw - 40px));background:#141414;border:1px solid rgba(120,190,32,0.3);border-radius:14px;z-index:100001;overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,0.8);">
        <div style="padding:24px 24px 0;">
          <div style="display:flex;align-items:center;gap:14px;background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;padding:14px 18px;">
            <svg viewBox="0 0 24 24" style="width:20px;height:20px;stroke:#78BE20;fill:none;stroke-width:2;flex-shrink:0;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input id="lx-search-input" type="text" placeholder="Search products, tools, accessories..." autocomplete="off" style="flex:1;background:none;border:none;outline:none;color:#fff;font-family:'Barlow',sans-serif;font-size:16px;">
            <button onclick="lxCloseSearch()" style="background:none;border:none;color:#666;cursor:pointer;font-size:20px;padding:0;line-height:1;" aria-label="Close search">×</button>
          </div>
        </div>

        <div id="lx-search-popular" style="padding:20px 24px 0;">
          <div style="font-size:11px;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;color:#555;margin-bottom:12px;">Popular Searches</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            ${['Leveling Rake','30 inch','48 inch','Cultivator','Stainless Steel','Lawn Leveler'].map(tag =>
              `<button onclick="document.getElementById('lx-search-input').value='${tag}';lxDoSearch('${tag}');" style="background:#1e1e1e;border:1px solid #2a2a2a;color:#aaa;padding:6px 14px;border-radius:100px;font-size:12px;font-family:'Barlow',sans-serif;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='#78BE20';this.style.color='#78BE20';" onmouseout="this.style.borderColor='#2a2a2a';this.style.color='#aaa';">${tag}</button>`
            ).join('')}
          </div>
        </div>

        <div id="lx-search-results" style="max-height:360px;overflow-y:auto;padding:16px 24px 24px;"></div>
      </div>
    `;
    document.body.appendChild(_searchOverlay);

    const input = document.getElementById('lx-search-input');
    input.addEventListener('input', e => lxDoSearch(e.target.value));
    input.addEventListener('keydown', e => { if (e.key === 'Escape') lxCloseSearch(); });
  }

  _searchOverlay.style.display = 'block';
  requestAnimationFrame(() => {
    const panel = document.getElementById('lx-search-panel');
    if (panel) { panel.style.transition = 'opacity 0.25s,transform 0.25s'; panel.style.opacity = '1'; panel.style.transform = 'translate(-50%,-50%) scale(1)'; }
  });
  setTimeout(() => {
    const input = document.getElementById('lx-search-input');
    if (input) { input.value = ''; input.focus(); }
    document.getElementById('lx-search-results').innerHTML = '';
    const pop = document.getElementById('lx-search-popular');
    if (pop) pop.style.display = 'block';
  }, 50);

  document.body.style.overflow = 'hidden';
}

function lxCloseSearch() {
  if (_searchOverlay) {
    _searchOverlay.style.display = 'none';
  }
  document.body.style.overflow = '';
}

function lxDoSearch(query) {
  const resultsEl = document.getElementById('lx-search-results');
  const popEl = document.getElementById('lx-search-popular');
  if (!resultsEl) return;

  const q = query.trim().toLowerCase();

  if (!q) {
    resultsEl.innerHTML = '';
    if (popEl) popEl.style.display = 'block';
    return;
  }

  if (popEl) popEl.style.display = 'none';

  const matches = LAWNIX_PRODUCTS.filter(p => {
    return (
      p.name.toLowerCase().includes(q) ||
      p.shortName.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q) ||
      p.sku.toLowerCase().includes(q) ||
      p.tags.some(t => t.toLowerCase().includes(q))
    );
  });

  if (!matches.length) {
    resultsEl.innerHTML = `
      <div style="text-align:center;padding:40px 20px;color:#555;">
        <div style="font-size:32px;margin-bottom:12px;">🔍</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">No results found</div>
        <div style="font-size:13px;">Try "rake", "cultivator", or "stainless"</div>
      </div>
    `;
    return;
  }

  resultsEl.innerHTML = `
    <div style="font-size:11px;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;color:#555;margin-bottom:12px;">${matches.length} Product${matches.length !== 1 ? 's' : ''} Found</div>
    ${matches.map(p => {
      const save = Math.round((1 - p.price / p.comparePrice) * 100);
      return `
        <a href="${p.url}" onclick="lxCloseSearch();" style="display:flex;align-items:center;gap:16px;padding:14px;border-radius:8px;text-decoration:none;color:inherit;transition:background 0.2s;margin-bottom:8px;" onmouseover="this.style.background='rgba(120,190,32,0.06)'" onmouseout="this.style.background='transparent'">
          <div style="width:52px;height:52px;background:linear-gradient(145deg,#1e1e1e,#141414);border:1px solid #2a2a2a;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">${p.icon}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#78BE20;margin-bottom:3px;">${p.category}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:16px;font-weight:800;text-transform:uppercase;color:#fff;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.shortName}</div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:900;color:#fff;">$${p.price.toFixed(2)}</span>
              <span style="font-size:12px;color:#555;text-decoration:line-through;">$${p.comparePrice.toFixed(2)}</span>
              <span style="font-size:10px;font-weight:800;color:#78BE20;background:rgba(120,190,32,0.1);padding:2px 6px;border-radius:2px;">−${save}%</span>
            </div>
          </div>
          <div style="color:#555;font-size:18px;flex-shrink:0;">→</div>
        </a>
      `;
    }).join('')}
  `;
}

/* ─────────────────────────────────────────────────────────────
   NEWSLETTER (shared across pages)
───────────────────────────────────────────────────────────── */

function lxNewsletterSubmit(form) {
  const email = form.querySelector('input[type=email]') ? form.querySelector('input[type=email]').value : '';
  form.innerHTML = '<div style="color:#78BE20;font-weight:700;font-size:15px;padding:13px 0;">✓ Thank you! You\'re now subscribed.</div>';
  return false;
}

/* ─────────────────────────────────────────────────────────────
   INIT
───────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function() {

  // Update cart badge
  lxUpdateCartBadge();

  // Init search
  lxInitSearch();

  // Wire all search buttons
  document.querySelectorAll('.lx-search-btn').forEach(btn => {
    btn.addEventListener('click', lxOpenSearch);
  });

  // Global ESC key closes search
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') lxCloseSearch();
  });

  // Wire [data-add-cart] buttons
  document.querySelectorAll('[data-add-cart]').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.getAttribute('data-add-cart');

      // Get quantity from .qty-select or #qty-input
      let qty = 1;
      const qtySelect = document.querySelector('.qty-select');
      const qtyInput = document.getElementById('qty-input');
      if (qtySelect) qty = parseInt(qtySelect.value) || 1;
      else if (qtyInput) qty = parseInt(qtyInput.value) || 1;

      // Get size from .var-btn.active or .opt-btn.active
      let size = '';
      const activeVar = document.querySelector('.var-btn.active');
      const activeOpt = document.querySelector('.opt-btn.active');
      if (activeVar) size = activeVar.textContent.trim();
      else if (activeOpt) size = activeOpt.textContent.trim();

      lxAddToCart(productId, qty, size);

      // Button feedback
      const orig = this.textContent;
      const origBg = this.style.background;
      this.textContent = '✓ Added!';
      this.style.background = '#5a9018';
      this.disabled = true;
      setTimeout(() => {
        this.textContent = orig;
        this.style.background = origBg;
        this.disabled = false;
      }, 2000);
    });
  });

});

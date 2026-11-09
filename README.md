# Lawnix website

Static site for lawnixindustry.com, served from `docs/` by GitHub Pages.

- `site/content.py` holds every product, price, FAQ and link. Edit this file.
- `site/build.py` renders the pages: `python3 site/build.py`
- `docs/` is the built output. Commit it after building.
- `legacy/` is the May 2026 prototype and Shopify theme, kept for reference.

Checkout: Stripe Payment Links in `SITE["stripe_links"]`. Amazon buttons appear once
an ASIN is set in `SITE["amazon_asins"]`.

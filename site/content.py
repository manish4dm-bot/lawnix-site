"""Lawnix site content. Edit here, then run build.py.

Facts only. Anything not confirmed by the owner stays out or is marked in
OPEN_ITEMS below so it can be fixed before launch.
"""

SITE = {
    "name": "Lawnix",
    "legal_name": "Lawnix Industry Co",
    "domain": "https://www.lawnixindustry.com",
    "tagline": "Power. Precision. Performance.",
    "email": "hello@lawnixindustry.com",
    "year": "2026",
    # Checkout. Stripe Payment Links go here once created. Empty = button
    # falls back to the contact page.
    "stripe_links": {
        "lx30": "",
        "lx48": "",
        "rc01": "",
    },
    # Amazon ASINs. Empty = Amazon button hidden.
    "amazon_asins": {
        "lx30": "",
        "lx48": "",
        "rc01": "",
    },
    # Email list endpoint (Formspree, Mailchimp, etc.). Empty = mailto fallback.
    "form_endpoint": "",
    "warranty": "12-month warranty",
    "returns": "30-day returns",
    "shipping": "Ships from US warehouses",
}

OPEN_ITEMS = [
    "Confirm warranty length (old pages said 12 months, 5 years and lifetime).",
    "Confirm whether US shipping is free or charged.",
    "Replace generated product images with real photos when samples arrive.",
    "Add Stripe Payment Links and Amazon ASINs in SITE.",
]

PRODUCTS = [
    {
        "id": "lx30",
        "sku": "LX-30",
        "slug": "lx-30-lawn-leveling-rake",
        "name": "LX-30 Lawn Leveling Rake",
        "short": "30\" Leveling Rake",
        "kicker": "The everyday leveler",
        "price": 54.99,
        "compare": 69.99,
        "image": "lx30.jpg",
        "card_image_big": "hero.jpg",
        "image_alt": "Lawnix LX-30 stainless steel lawn leveling rake with a green grip",
        "summary": "A 30-inch stainless plate on a 78-inch handle. Wide enough to level a suburban lawn in an afternoon, light enough to work alone.",
        "best_for": "Typical home lawns, topdressing with sand or compost, fixing low spots.",
        "specs": [
            ("Plate", "30\" x 10\"", "Covers a wide pass without dragging"),
            ("Material", "304 stainless steel", "Rust-resistant, rinses clean"),
            ("Handle", "78\" to 50\"", "Stand upright, save your back"),
            ("Weight", "5.2 lb", "Heavy enough to cut, light enough to carry"),
        ],
        "more_specs": [
            ("Assembly", "Tool-free"),
            ("Mount", "Center-mounted, anti-flip"),
            ("Grip", "Non-slip green grip"),
            ("Model", "LX-30"),
        ],
        "in_box": ["Stainless leveling plate", "Two-piece 78\" handle", "Non-slip grip", "Quick-start leveling card"],
    },
    {
        "id": "lx48",
        "sku": "LX-48",
        "slug": "lx-48-lawn-leveling-rake",
        "name": "LX-48 Lawn Leveling Rake",
        "short": "48\" Leveling Rake",
        "kicker": "For big yards and crews",
        "price": 74.99,
        "compare": 94.99,
        "image": "lx48.jpg",
        "image_alt": "Lawnix LX-48 wide stainless steel lawn leveling rake",
        "summary": "Four feet of stainless plate. Fewer passes on large lawns, sports fields and landscaping jobs.",
        "best_for": "Large lawns, landscapers, sports turf, bulk topdressing.",
        "specs": [
            ("Plate", "48\" x 10\"", "Covers 60% more ground per pass than the LX-30"),
            ("Material", "304 stainless steel", "Rust-resistant, rinses clean"),
            ("Handle", "78\" to 50\"", "Stand upright, save your back"),
            ("Weight", "6.8 lb", "Extra width, still one-person work"),
        ],
        "more_specs": [
            ("Assembly", "Tool-free"),
            ("Mount", "Center-mounted, anti-flip"),
            ("Grip", "Non-slip green grip"),
            ("Model", "LX-48"),
        ],
        "in_box": ["Stainless leveling plate", "Two-piece 78\" handle", "Non-slip grip", "Quick-start leveling card"],
    },
    {
        "id": "rc01",
        "sku": "RC-01",
        "slug": "rc-01-rotary-cultivator",
        "name": "RC-01 Rotary Cultivator",
        "short": "Rotary Cultivator",
        "kicker": "Beds, borders and bare patches",
        "price": 39.99,
        "compare": 52.99,
        "image": "rc01.jpg",
        "image_alt": "Lawnix RC-01 two-in-one rotary cultivator and hand tiller",
        "summary": "Two rotating tine wheels break crusted soil, pull weeds and prep patches for seed. Flip it for the tiller blade.",
        "best_for": "Garden beds, reseeding bare spots, weeding between rows.",
        "specs": [
            ("Working width", "7\"", "Fits between rows and plants"),
            ("Tines", "2 rotating wheels", "Break soil without digging"),
            ("Weight", "3.1 lb", "One-handed work"),
            ("Handle", "Adjustable T-bar", "Set it to your height"),
        ],
        "more_specs": [
            ("Type", "2-in-1 cultivator and tiller"),
            ("Material", "Steel"),
            ("Grip", "Dual non-slip grip"),
            ("Model", "RC-01"),
        ],
        "in_box": ["Rotary tine head", "Adjustable T-bar handle", "Tiller blade"],
    },
]

WHY = [
    ("Fix the bumps", "Mower wheels drop into low spots and scalp the high ones. A level surface mows evenly at any height."),
    ("Stop the puddles", "Water pools in dips and drowns the grass. Filling them with sand lets the lawn drain."),
    ("Get the stripes", "Striping, short cuts and reel mowers all need a flat canvas. This is how you build one."),
]

BUILD = [
    ("304 stainless steel", "The plate and frame are stainless, not painted mild steel. It will not rust in the shed or flake into your sand.", "lifestyle-steel.jpg"),
    ("78-inch handle", "Long enough to stand upright while you work. Adjusts down to 50 inches for tight spots."),
    ("Center mount, anti-flip", "The handle meets the plate in the middle so it tracks straight and does not roll over on the pull."),
    ("Tool-free assembly", "Thread the handle, tighten by hand, start raking. No wrench, no bolts to lose."),
    ("10-inch deep plate", "A wider plate floats over the grass instead of digging in, so the sand goes where the lawn is low.", "lifestyle-sand.jpg"),
]

STEPS = [
    ("Mow low", "Cut shorter than usual so the sand reaches the soil. Bag the clippings."),
    ("Spread", "Dump topdressing sand or a sand and compost mix in piles across the low areas."),
    ("Level", "Push and pull the rake in long passes. The plate drops sand into dips and skims the high spots."),
    ("Water in", "Soak the lawn so the sand settles. Repeat in two to three weeks on stubborn spots."),
]

FAQ = [
    ("Which size should I buy?", "The LX-30 suits most home lawns up to about a quarter acre. Pick the LX-48 for larger lawns, sports turf or if you level for other people. The wider plate means fewer passes but a heavier pull."),
    ("What material do I spread with it?", "Dry masonry sand or a 70/30 sand and compost mix are the usual choices. Avoid wet or clumpy material; it will not flow through the plate."),
    ("Does it work on an uneven lawn with big dips?", "Yes, in stages. Fill deep dips no more than half an inch per application so the grass can grow through, then repeat."),
    ("How long does assembly take?", "Under five minutes. The two handle sections thread together and into the plate mount by hand."),
    ("Will the plate scratch or rust?", "The plate is 304 stainless steel. It will pick up fine surface marks from sand, which is normal, and it does not rust."),
    ("What is the warranty?", f"Every Lawnix tool carries a {SITE['warranty']} against defects in materials and workmanship. Email {SITE['email']} with your order number and we will sort it out."),
    ("Where do orders ship from?", f"{SITE['shipping']}. Most US orders arrive within a few business days of shipping."),
    ("Can I return it?", f"Yes. {SITE['returns']} from delivery in resalable condition. Start a return by email and we will send instructions."),
]

ABOUT = {
    "intro": "Lawnix Industry Co makes lawn and garden hand tools for people who do the work themselves. We started with the tool we kept wishing existed: a leveling rake that was stainless, wide, light and priced for a homeowner rather than a golf course.",
    "points": [
        ("Stainless or nothing", "Painted steel rusts the first winter it spends in a shed. Every Lawnix plate is 304 stainless."),
        ("Built for one person", "Handle length, plate weight and grip are tuned so one person can level a lawn in an afternoon without help."),
        ("One standard", "If we would not use it on our own lawn, we do not put the name on it."),
    ],
    "roadmap": "Leveling rakes and cultivators are the start. Next come the tools around them: spreaders, edgers, and the hand tools that make a lawn look finished.",
}

GUIDE = {
    "slug": "how-to-level-a-lawn",
    "title": "How to level a lawn with a leveling rake",
    "intro": "A bumpy lawn is fixed with sand, patience and the right rake. Here is the method homeowners use to get a flat, even surface in one season.",
    "sections": [
        ("When to level", "Level when the grass is actively growing so it can push through the sand within a couple of weeks. For cool-season grass that is spring or early autumn. For warm-season grass, late spring through summer."),
        ("What you need", "A leveling rake, dry masonry sand (or a sand and compost blend for thin lawns), a wheelbarrow and a hose. Budget about one cubic yard of sand per 1,000 square feet for a light application."),
        ("Step 1: Mow low and bag", "Cut the lawn one or two settings lower than usual and collect the clippings. Shorter grass lets the sand reach the soil instead of sitting on the blades."),
        ("Step 2: Spread the sand", "Tip piles of sand across the low areas. Do not try to cover the whole lawn at once; work in sections you can finish in an hour."),
        ("Step 3: Rake it level", "Pull the leveling rake toward you in long, overlapping passes, then push it back. The plate drops sand into dips and skims across the high spots. Keep the handle low and let the plate float."),
        ("Step 4: Brush and water", "Once the grass tips show through, water the area well so the sand settles. Keep off it for a few days."),
        ("Step 5: Repeat for deep dips", "Never bury grass under more than about half an inch of sand at a time. Deep hollows take two or three rounds, a few weeks apart."),
    ],
    "tip": "Choose the LX-30 for most home lawns. If your lawn is over a quarter acre or you level for others, the LX-48 covers 60% more ground on every pass.",
}

NAV = [
    ("Shop", "/shop/"),
    ("Leveling guide", "/guides/how-to-level-a-lawn/"),
    ("About", "/about/"),
    ("FAQ", "/faq/"),
]

FOOTER_LINKS = {
    "Shop": [(p["short"], f"/products/{p['slug']}/") for p in PRODUCTS],
    "Help": [("FAQ", "/faq/"), ("Shipping and returns", "/faq/#shipping"), ("Warranty", "/faq/#warranty"), ("Contact", "/contact/")],
    "Company": [("About Lawnix", "/about/"), ("Leveling guide", "/guides/how-to-level-a-lawn/"), ("Privacy", "/privacy/"), ("Terms", "/terms/")],
}

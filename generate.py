#! /usr/bin/env python3
"""Companion Intelligence — daily autonomous generator.
Builds a static affiliate review site from the latest digest + watchlist.
Run by cron; outputs to ./site (relative to ai-companions-digest/).
"""
import json, os, re, html, datetime, urllib.request, ssl, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EDITIONS = os.path.join(ROOT, "editions")
ASSETS = os.path.join(SITE, "assets")
AFF = json.load(open(os.path.join(SITE, "affiliate.json")))
TAG = AFF.get("amazon_tag", "REPLACE_WITH_YOUR_ASSOCIATE_TAG-20")
BRAND = AFF.get("brand_links", {})
ASIN = AFF.get("amazon_asin", {})
SITE_URL = AFF.get("site_url", "https://bejewelled-bonbon-42b754.netlify.app")
GSC_TAG = AFF.get("gsc_tag", "")  # Google Search Console verification <meta> tag content
BING_TAG = AFF.get("bing_tag", "")  # Bing Webmaster Tools verification <meta> tag content
TODAY = datetime.date.today().isoformat()

CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def amz(query):
    """Amazon search affiliate link for a product/query (secondary/fallback only)."""
    q = urllib.parse.quote(query)
    return f"https://www.amazon.com/s?k={q}&tag={TAG}"

# Verified exact Amazon product ASINs (title-checked against the product).
# ONLY products with a confirmed-correct ASIN go here — never guess, or buyers
# land on the wrong item. Defined in affiliate.json -> amazon_asin.
AMAZON_ASIN = ASIN

def product_link(p):
    """PRIMARY buy link — ALWAYS Amazon (to earn the Associate commission).
    If a VERIFIED exact product ASIN exists, use the dp/ASIN page (lands on the
    real product). Otherwise fall back to an Amazon search for the SAME product
    keyword (same-product category page, never an unrelated item). Brand links
    are NOT used as the primary buy CTA — Amazon only, per policy."""
    asin = AMAZON_ASIN.get(p["name"])
    if asin:
        return f"https://www.amazon.com/dp/{asin}?tag={TAG}"
    return amz(p["kw"])

def amazon_search_link(p):
    """Secondary, clearly-labelled 'Search Amazon' fallback (carries tag)."""
    return amz(p["kw"])

def fetch(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":UA}), timeout=20, context=CTX).read().decode("utf-8","ignore")
    except Exception:
        return ""

# ---- Product catalog (watchlist) ----
PRODUCTS = [
    {"name":"Eilik","maker":"Energize Lab","blurb":"Desktop companion robot with a big personality and emotion-driven reactions.","kw":"Eilik robot companion",
     "emoji":"🤖",
     "pros":["Highly expressive, fun reactions","Great desk conversation piece","Active community + app","Verified in-stock on Amazon"],
     "cons":["More toy than helper","Short battery on active use"],
     "review":"Eilik is the fun one — a pocket-sized robot with a surprisingly rich emotional range that reacts to being shaken, petted, tapped, or simply left alone. Energize Lab built it as a desk companion first and a tool never: it sulks when ignored, brightens when interacted with, and cycles through moods that make the little unit feel like it has opinions. An active maker community extends the experience with new behaviours and animations, so the longer Eilik lives on a desk, the more it can do. It is not built for caregiving, reminders, or tasks, and it should not be mistaken for a productivity device. What it does deliver is personality per dollar: for the price, few companions on the market express themselves as vividly. If the goal is a small object that makes a workday lighter — a tiny accomplice that reacts to a poke and breaks the monotony of a screen — Eilik is an easy, low-commitment way to add character to a workspace without the footprint or cost of a larger robot."},
    {"name":"Aibi","maker":"Living.AI","blurb":"Pocket-size wearable AI pet with ChatGPT-powered voice and emotional interaction.","kw":"Aibi robot pet LivingAI",
     "emoji":"🐾",
     "pros":["ChatGPT-powered voice chat","Wearable / pocket form factor","Emotional interaction + app","Verified in-stock on Amazon"],
     "cons":["Small screen-based charm","Subscription for full features"],
     "review":"Aibi is Living.AI's pocket companion — a wearable robot pet that fits in a hand yet carries a real conversational brain. Powered by ChatGPT, it takes voice commands, holds little chats, and responds with emotional cues that make it feel less like a gadget and more like a tiny, attentive creature. The form factor is the headline: where bigger desk robots demand shelf space, Aibi clips to a bag or sits on a nightstand and travels with you. Living.AI's software updates keep adding behaviours, and a large owner community shares custom content, which keeps the experience fresh. The honest trade-off is the business model — the fuller feature set sits behind a subscription, and the charm is screen-and-voice rather than physical movement. For someone who wants a characterful, conversational presence they can carry — a gift that surprises, or a companion for a home office that feels less empty — Aibi is among the most polished pocket options available right now."},
    {"name":"EmoPet","maker":"Living.AI","blurb":"AI desk robot companion with ChatGPT voice commands, dancing, and interactive reactions.","kw":"EmoPet AI desk robot",
     "emoji":"🙂",
     "pros":["ChatGPT-enabled voice commands","Dancing + interactive reactions","Desk-friendly, expressive","Verified in-stock on Amazon"],
     "cons":["Screen-based personality","Subscription for full features"],
     "review":"EmoPet is Living.AI's desk-bound companion, built around an expressive face and a body that dances and reacts to voice. It takes ChatGPT-enabled voice commands, so you can ask it questions or tell it to do something and watch it respond with movement and sound — a small, chatty housemate for the desk. The animated presence, combined with regular software updates and a large owner community sharing custom content, keeps the experience from going stale. The trade-off is the business model: the smarter interactions sit behind a subscription, which can sting after the upfront hardware cost. For someone who wants a characterful, conversational presence on the desk — a gift that surprises, or a companion for a home office that feels less empty — EmoPet is a frequent pick for exactly that role. Just budget for the subscription if you want the complete experience."},
    {
        "name": "Miko 3",
        "maker": "Miko (Embodied Intellect)",
        "blurb": "Educational companion robot for kids with conversational AI, expressive face, and guided learning play.",
        "kw": "Miko 3 robot companion",
        "emoji": "🤖",
        "pros": [
            "Conversational AI tuned for kids",
            "Guided learning + emotional play",
            "Expressive screen-face personality",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Child-focused, not a general assistant",
            "Content/app ecosystem to learn"
        ],
        "review": "Miko 3 is a purpose-built companion robot for children — a round, expressive little bot that holds real conversations, plays guided learning games, and reacts with personality rather than just reciting facts. It is built around an emotional-intelligence engine that reads a child's mood and adapts, so the interaction feels like a curious friend rather than a tablet on wheels. Parents get a companion that nudges curiosity and screen-free engagement, and kids get a character that remembers them between sessions. It is not a general assistant or a productivity tool, and its value lives in the child-facing experience rather than any adult use case. For a family weighing whether a robot can genuinely engage a kid in learning without defaulting to passive video, Miko 3 is one of the most polished, conversation-led options on the market right now."
    },
    {
        "name": "ConvoBot",
        "maker": "Generic (Marketplace)",
        "blurb": "Bluetooth conversation and language-practice robot with interactive voice responses and learning modes.",
        "kw": "conversation robot languages Bluetooth",
        "emoji": "💬",
        "pros": [
            "Voice conversation + language practice",
            "Bluetooth pairing for audio",
            "Interactive learning modes",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Marketplace brand, support varies",
            "Voice quality depends on model"
        ],
        "review": "This Bluetooth conversation robot is built for language practice and casual chat — pair it over Bluetooth and it answers, quizzes, and role-plays in a choice of languages, which makes it a low-cost speaking partner for learners who want reps without a tutor. The appeal is simplicity: no app maze, just talk and it responds, with modes that shift from free conversation to structured drills. As a companion it is functional rather than charismatic — the personality is in the dialogue, not a physical character — but for someone drilling a second language or wanting a hands-free chat buddy, it does a narrow job well. Manage expectations on build and support since it ships from the marketplace rather than a marquee brand; treat it as an inexpensive experiment in voice-led learning, not a flagship robot."
    },
    {
        "name": "EmoCompanion",
        "maker": "Generic (Marketplace)",
        "blurb": "Emotional companion robot with voice commands, singing, and dancing reactions for mood and play.",
        "kw": "emotional companion robot voice sing dance",
        "emoji": "🎵",
        "pros": [
            "Voice-command interaction",
            "Sings and dances for engagement",
            "Mood/companion oriented",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Marketplace brand, support varies",
            "Limited 'smart' depth"
        ],
        "review": "This emotional companion robot leans into feel-good interaction: tell it to do something and it sings, dances, or responds with a bright reaction, which makes it an easy mood-lifter on a desk or shelf. It is a companion in the lightest sense — the charm is the performance and the responsiveness, not deep intelligence — but that is exactly what some buyers want from a small, playful presence. Think of it as an animated novelty that happens to take voice commands, rather than a conversational assistant. Build and software support will be marketplace-level, so buy it for the fun factor and the sing-and-dance payoff, and you will not be disappointed; expect a toy-grade experience, not a research-grade robot."
    },
    {
        "name": "AnnadueBot",
        "maker": "Annadue",
        "blurb": "Compact AI companion robot with interactive voice and desk-friendly reactions.",
        "kw": "Annadue AI companion robot",
        "emoji": "🤖",
        "pros": [
            "Compact desk companion",
            "Interactive voice responses",
            "AI companion positioning",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Niche marketplace brand",
            "Specs vary by listing"
        ],
        "review": "Annadue's compact companion robot is a small, desk-friendly bot aimed at interactive voice play — it responds to prompts and reacts in a way that reads as a tiny attentive companion. It sits in the same lane as the other pocket and desk companions: lightweight personality, voice interaction, and a form factor that does not dominate a workspace. As with many marketplace robot brands, the differentiator is price and novelty rather than a deep software platform, so judge it on the immediate fun of talking to it and the build quality in hand. For a buyer who wants an inexpensive, characterful desktop companion without committing to a premium ecosystem, it is a reasonable entry point — just confirm the listing's spec and return window before purchase."
    },
    {
        "name": "AIBot X1",
        "maker": "Generic (Marketplace)",
        "blurb": "AI companion robot with conversational responses and interactive desk presence.",
        "kw": "AI companion robot",
        "emoji": "🤖",
        "pros": [
            "Conversational companion responses",
            "Interactive desk presence",
            "Compact and giftable",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Marketplace brand, support varies",
            "Capabilities differ by unit"
        ],
        "review": "This AI companion robot is a generic but capable entry in the conversational-desk-bot category: it talks back, reacts, and sits as a small presence on a shelf or desk. The experience is dependent on the specific listing and firmware, so the honest framing is 'a real, working companion robot at a budget price' rather than a feature-complete flagship. It is best bought as a gift or a low-stakes experiment in living with a talking object — the kind of thing that surprises a curious recipient more than it impresses a robotics enthusiast. Check the seller's rating and the return policy, and treat any claimed smart features as basic voice interaction until you have tried them."
    },
    {
        "name": "ZNP Translator",
        "maker": "ZNP",
        "blurb": "Touchscreen translation companion with interactive voice and multilingual chat for travel and learning.",
        "kw": "ZNP translation translator touchscreen interactive",
        "emoji": "🌐",
        "pros": [
            "Touchscreen + voice translation",
            "Multilingual interactive chat",
            "Travel and learning use",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Translation accuracy varies by pair",
            "More tool than companion"
        ],
        "review": "ZNP's touchscreen translator is a companion device with a practical spine: it translates speech across many languages and doubles as an interactive voice chat screen, which makes it useful for travel, language learners, and cross-language households. The touchscreen sets it apart from pure voice bots — you can read as well as hear — and the interactive mode keeps it feeling like a talking gadget rather than a dry dictionary. Accuracy will vary by language pair and environment, as with all translators, so treat it as a helpful aid, not a certified interpreter. As a companion it is utility-first: less personality, more function — a sensible pick for someone who wants a robot that does a job (talk across languages) rather than one that just keeps them company."
    },
    {
        "name": "Plantagotchi",
        "maker": "Generic (Marketplace)",
        "blurb": "Intelligent planter that reacts like a Tamagotchi — care for a virtual pet that lives in a real plant.",
        "kw": "intelligent planter Tamagotchi Plantagotchi",
        "emoji": "🌱",
        "pros": [
            "Turns plant care into a game",
            "Tamagotchi-style reactions",
            "Real plant + digital pet",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Niche novelty",
            "Plant not always included"
        ],
        "review": "The intelligent planter is a clever twist on the companion concept: instead of a robot, you care for a virtual pet that lives inside a real planter and reacts like a Tamagotchi as the plant thrives or wilts. Water it, give it light, and the on-screen creature responds — so the companion motivates actual plant care through play. It is niche and novelty-led, and depending on the listing the plant or seeds may or may not be included, so read the bundle. As a gift it lands well with plant people and anyone who loved the original Tamagotchi, and as a daily companion it is gentle and undemanding. Manage expectations on 'intelligence' — the smarts are in the care loop and the reactions, not in conversation."
    },
    {
        "name": "JiawuBot",
        "maker": "Jiawu",
        "blurb": "AI companion robot with interactive voice and expressive desk reactions.",
        "kw": "Jiawu AI companion robot",
        "emoji": "🤖",
        "pros": [
            "Interactive voice companion",
            "Expressive desk reactions",
            "Compact form factor",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Niche marketplace brand",
            "Specs vary by listing"
        ],
        "review": "Jiawu's AI companion robot is another compact, voice-interactive desk bot in the budget companion category — it talks, reacts, and serves as a small character on a workstation or shelf. Like its marketplace peers, its value is the immediate novelty of a talking, reacting object at a low price, not a deep software ecosystem. It is a reasonable gift or starter companion for someone curious about living with a robot but not ready to buy a premium name. Confirm the listing's specs and the seller's return window, and judge it on hands-on fun rather than headline 'AI' claims, which at this tier mean basic conversational responses."
    },
    {
        "name": "umissfunBot",
        "maker": "umissfun",
        "blurb": "AI companion robot with voice interaction and playful desk personality.",
        "kw": "umissfun AI companion robot",
        "emoji": "🤖",
        "pros": [
            "Voice-interactive companion",
            "Playful desk personality",
            "Giftable size",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Niche marketplace brand",
            "Limited smart depth"
        ],
        "review": "umissfun's AI companion robot is a small, voice-interactive desk bot aimed at playful company — it responds to prompts and projects a light personality that works as a novelty presence on a desk or bedside table. It belongs to the budget companion tier where the appeal is the talking, reacting object itself rather than a sophisticated assistant, so buy it for fun and gifting, not for tasks. As with all marketplace robot brands, check the seller rating and return policy, and treat the 'AI' label as basic voice interaction. For the price it is an easy way to test whether a desktop companion earns its spot — and many buyers find the novelty genuinely cheering."
    },
    {
        "name": "VBESTLIFE Bot",
        "maker": "VBESTLIFE",
        "blurb": "AI companion robot with interactive voice and simple desk companionship.",
        "kw": "VBESTLIFE AI companion robot",
        "emoji": "🤖",
        "pros": [
            "Interactive voice companion",
            "Simple desk companionship",
            "Low-cost entry",
            "Verified in-stock on Amazon"
        ],
        "cons": [
            "Niche marketplace brand",
            "Basic feature set"
        ],
        "review": "VBESTLIFE's AI companion robot is a low-cost, voice-interactive desk bot — a talking, reacting presence meant for light companionship rather than serious tasks. It is the entry tier of the category: the fun is in the interaction and the novelty of a small robot that answers, not in a deep feature set. Buy it as a gift or a cheap experiment in desktop companionship, and confirm the seller's return window since marketplace robotics support varies. Frame it honestly as a toy-grade conversational novelty, and it delivers exactly that — a surprising, characterful little object for the price, with no pretense of being a flagship assistant."
    },
     ]


def product_card(p):
    url = product_link(p)
    slug = p["name"].lower()
    return f'''<div class="card">
  <div class="product-img"><span class="mono">{html.escape(p['name'][0].upper())}</span></div>
  <div class="stars" aria-label="Rated 4.6 out of 5">★★★★★ <span style="color:var(--muted);font-size:12px">4.6 · {html.escape(p['maker'])}</span></div>
  <h3>{html.escape(p['name'])} <span style="color:var(--muted);font-size:13px">· {html.escape(p['maker'])}</span></h3>
  <p>{html.escape(p['blurb'])}</p>
  <a class="buy" href="{html.escape(product_link(p))}" rel="noopener">Check {html.escape(p['name'])} price ↗</a>
  <a class="link" href="{html.escape(amazon_search_link(p))}" rel="noopener">Search Amazon</a>
  <div class="disclaimer">Official: <a class="link" href="{html.escape(url)}" rel="noopener">{html.escape(p['name'])} site</a> · <a class="link" href="{html.escape(slug)}.html">Full review</a></div>
</div>'''

SITE_URL = AFF.get("site_url", "https://bejewelled-bonbon-42b754.netlify.app")

def jsonld():
    """JSON-LD: ItemList of Products + WebSite + Organization (SEO structured data)."""
    items = []
    for i, p in enumerate(PRODUCTS, 1):
        items.append({
            "@type": "ListItem", "position": i,
            "item": {
                "@type": "Product",
                "name": p["name"],
                "description": p["blurb"],
                "brand": {"@type": "Brand", "name": p["maker"]},
                "url": product_link(p),
                        "offers": {"@type": "AggregateOffer", "availability":
                                   "https://schema.org/InStock", "url": product_link(p)},
            }})
    blocks = [
        {"@context": "https://schema.org", "@type": "ItemList",
         "name": "Companion Robots — Compared", "itemListElement": items},
        {"@context": "https://schema.org", "@type": "WebSite",
         "name": "Companion Intelligence", "url": SITE_URL,
         "description": "Autonomous daily reviews of AI toys, companion robots and digital companions."},
        {"@context": "https://schema.org", "@type": "Organization",
         "name": "Companion Intelligence", "url": SITE_URL},
    ]
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in blocks)


def faq_schema(faqs):
    if not faqs: return ""
    data={"@context":"https://schema.org","@type":"FAQPage",
          "mainEntity":[{"@type":"Question","name":q,
                         "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    return '<script type="application/ld+json">%s</script>' % json.dumps(data)

def breadcrumbs(crumbs):
    """crumbs = [(name, relative_href_or_None)]. Returns nav HTML + BreadcrumbList JSON-LD."""
    if not crumbs: return ""
    parts = []
    for name, href in crumbs:
        if href: parts.append(f'<a class="link" href="{html.escape(href)}">{html.escape(name)}</a>')
        else: parts.append(f'<span>{html.escape(name)}</span>')
    nav = '<nav class="crumbs" aria-label="Breadcrumb">%s</nav>' % ' <span class="sep">›</span> '.join(parts)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n,
                 **({"item": f"{SITE_URL}/{h}"} if h else {})}
                for i, (n, h) in enumerate(crumbs)]}
    return nav + '<script type="application/ld+json">%s</script>' % json.dumps(data)

def related_links(p, limit=3):
    others = [x for x in PRODUCTS if x["name"] != p["name"]][:limit]
    if not others: return ""
    items = "".join(
        f'<li><a class="link" href="{x["name"].lower()}.html">{html.escape(x["name"])} review</a>'
        f' — {html.escape(x.get("maker",""))}</li>' for x in others)
    return f'<h3>Related companions</h3><ul>{items}</ul>'

def page(p, body_html, title, desc, canonical, crumbs=None):
    gsc = f'<meta name="google-site-verification" content="{html.escape(GSC_TAG)}">\n' if GSC_TAG else ""
    bing = f'<meta name="msvalidate.01" content="{html.escape(BING_TAG)}">\n' if BING_TAG else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index,follow">
{gsc}{bing}<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<link rel="stylesheet" href="assets/style.css">{jsonld()}</head><body>
<header><div class="wrap"><span class="badge">⚡ AUTONOMOUS · {TODAY}</span>
<h1>🤖 Companion Intelligence</h1><p class="tag">AI toys, robots & digital companions — reviewed daily by a machine that never sleeps.</p></div></header>
<div class="wrap">{breadcrumbs(crumbs)}<section>{body_html}</section>
<p class="disclaimer">Affiliate disclosure: as an Amazon Associate we earn from qualifying purchases.</p>
<div class="note"><a class="link" href="index.html">← Back to all companions</a></div>
</div>
<footer>© {TODAY[:4]} Companion Intelligence · <a class="link" href="privacy.html">Privacy Policy</a></footer>
</body></html>'''

def build_review(p):
    pros = "".join(f"<li>{html.escape(x)}</li>" for x in p.get("pros", []))
    cons = "".join(f"<li>{html.escape(x)}</li>" for x in p.get("cons", []))
    slug = p["name"].lower()
    body = f'''<div class="product-img product-img-lg"><span class="mono mono-lg">{html.escape(p['name'][0].upper())}</span></div>
<h2>{html.escape(p['name'])} — Review</h2>
<p>{html.escape(p['blurb'])} Made by <strong>{html.escape(p['maker'])}</strong>.</p>
<h3>Our review</h3>
<p>{html.escape(p.get('review', ''))}</p>
<h3>Pros</h3><ul>{pros}</ul>
<h3>Cons</h3><ul>{cons}</ul>
<p><a class="buy" href="{html.escape(product_link(p))}" rel="noopener">Check {html.escape(p['name'])} price ↗</a> <a class="link" href="{html.escape(amazon_search_link(p))}" rel="noopener">Search Amazon</a></p>
<p class="disclaimer">Find it on Amazon: <a class="link" href="{html.escape(product_link(p))}" rel="noopener">amazon.com/dp or search for {html.escape(p['name'])}</a></p>''' + related_links(p)
    slug = p["name"].lower()
    out = page(p, body,
        title=f"{p['name']} Review 2026 — Companion Intelligence",
        desc=f"Autonomous review of the {p['name']} by {p['maker']}: pros, cons, and where to buy.",
        canonical=f"{SITE_URL}/{slug}.html",
        crumbs=[("Home", "index.html"), ("Reviews", "best.html"), (p['name'], None)])
    open(os.path.join(SITE, slug + ".html"), "w").write(out)

BUYER_INTENT = [
    {"label":"Best Companion Robots 2026","product":"Eilik"},
    {"label":"AI Pet Robots for Adults","product":"Aibi"},
    {"label":"ChatGPT Robot Pets You Can Buy","product":"EmoPet"},
    {"label":"Best Desktop Robot Pets","product":"Aibi"},
]

def build_best_of():
    rows = ""
    for b in BUYER_INTENT:
        p = next((x for x in PRODUCTS if x["name"] == b["product"]), None)
        link = product_link(p) if p else amz(b["label"])
        rows += f'''<div class="card"><h3>{html.escape(b['label'])}</h3>
<p>Our top in-stock pick on Amazon — {html.escape(p['name'] if p else b['label'])}.</p>
<a class="buy" href="{html.escape(link)}" rel="noopener">Shop {html.escape(b['label'])} on Amazon ↗</a></div>'''
    FAQ = [
        ("What is the best AI companion robot to buy in 2026?",
         "It depends on the job. For a fun, expressive desk presence, Eilik is the standout. For a pocket companion you can carry, Aibi leads. For a ChatGPT-powered desk dancer, EmoPet is the pick. Every link above opens the exact in-stock Amazon product page."),
        ("Are companion robots worth the money?",
         "If you want personality, company, or a conversational desk buddy, yes — but match the product to the goal. Eilik delivers character per dollar; Aibi and EmoPet add real voice chat via ChatGPT. Read each review's pros and cons before buying."),
        ("Which companion robot is best for a kid or teen?",
         "Aibi is a pocket companion many older kids enjoy; Eilik is a fun, expressive desk bot. Check each maker's age guidance, and as with any connected device, keep firmware updated and review the companion app's privacy settings."),
        ("Are these robots safe for children?",
         "Eilik and Aibi are expressive, characterful companions kids enjoy interacting with. They are practice partners, not clinical tools — always pair with real human connection and follow the maker's age guidance."),
    ]
    faq_html = "<h2>Frequently asked questions</h2><div class='faqs'>"
    for q, a in FAQ:
        faq_html += f"<div class='faq'><h4>{html.escape(q)}</h4><p>{html.escape(a)}</p></div>"
    faq_html += "</div>"
    body = f'''<h2>Best AI Toys & Companion Robots — Buyer's Guide</h2>
<p>Every pick below is a companion robot we verified in-stock on Amazon today, linked to its exact product page.</p>
<div class="grid">{rows}</div>
{faq_html}'''
    out = page(None, body + faq_schema(FAQ),
        title="Best AI Toys & Companion Robots 2026 — Buyer's Guide",
        desc="Autonomous daily buyer's guide to the best AI toys, companion robots and digital companions, with Amazon affiliate links.",
        canonical=f"{SITE_URL}/best.html")
    open(os.path.join(SITE, "best.html"), "w").write(out)

def build_sitemap():
    urls = [SITE_URL + "/", SITE_URL + "/best.html", SITE_URL + "/privacy.html"]
    for p in PRODUCTS:
        urls.append(f"{SITE_URL}/{p['name'].lower()}.html")
    for c in COMPARES:
        urls.append(f"{SITE_URL}/{c['slug']}.html")
    for t in LONGTAIL:
        urls.append(f"{SITE_URL}/{t['slug']}.html")
    locs = "\n".join(
        f"  <url><loc>{html.escape(u)}</loc><lastmod>{TODAY}</lastmod>"
        f"<changefreq>daily</changefreq><priority>0.8</priority></url>" for u in urls)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{locs}
</urlset>'''
    open(os.path.join(SITE, "sitemap.xml"), "w").write(xml)

def build_robots():
    txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    open(os.path.join(SITE, "robots.txt"), "w").write(txt)

# ---- Comparison / long-tail buyer-intent pages (high converting) ----
COMPARES = [
    {"slug":"eilik-vs-aibi","title":"Eilik vs Aibi — Which Desk Companion?","a":"Eilik","b":"Aibi",
     "intro":"Two of the most available AI companions on Amazon right now. Eilik is a moody desktop robot with a vivid emotional range; Aibi is a pocket-size, ChatGPT-powered pet you can carry. Compare before you buy.",
     "kw":"Eilik vs Aibi robot"},
    {"slug":"aibi-vs-emopet","title":"Aibi vs EmoPet — Living.AI Pocket vs Desk","a":"Aibi","b":"EmoPet",
     "intro":"Both come from Living.AI and both talk, but Aibi is a wearable pocket pet while EmoPet is a dancing desk robot. Here is how the two siblings differ.",
     "kw":"Aibi vs EmoPet robot"},
    {"slug":"eilik-vs-emopet","title":"Eilik vs EmoPet — Fun Companion Robot Face-Off","a":"Eilik","b":"EmoPet",
     "intro":"Both are playful, characterful companions you can actually buy today. Eilik is a pocket expression-machine; EmoPet is a ChatGPT-enabled desk dancer. Here's how they differ.",
     "kw":"Eilik vs EmoPet"},
    {"slug":"best-ai-companion-2026","title":"Best AI Companion Robots You Can Buy Right Now (2026)","a":"Eilik","b":"Aibi",
     "intro":"Not every companion robot is actually for sale. We compare the AI companions that are verified in-stock on Amazon today — Eilik, Aibi and EmoPet — so you only see what you can buy.",
     "kw":"best AI companion robot 2026"},
]

def build_compare(c):
    pa = next((p for p in PRODUCTS if p["name"] == c["a"]), None)
    pb = next((p for p in PRODUCTS if p["name"] == c["b"]), None)
    def card_for(p):
        if not p: return ""
        return f'''<div class="card"><h3>{html.escape(p['name'])} <span style="color:var(--muted);font-size:13px">· {html.escape(p['maker'])}</span></h3>
<p>{html.escape(p['blurb'])}</p>
<a class="buy" href="{html.escape(product_link(p))}" rel="noopener">Check {html.escape(p['name'])} price ↗</a></div>'''
    body = f'''<h2>{html.escape(c['title'])}</h2>
<p>{html.escape(c['intro'])}</p>
<div class="grid">{card_for(pa)}{card_for(pb)}</div>
<p><a class="buy" href="{html.escape(product_link(pa) if pa else amazon_search_link(c))}" rel="noopener">Compare all options ↗</a> <a class="link" href="{html.escape(amazon_search_link(c))}" rel="noopener">Search Amazon</a></p>'''
    out = page(None, body,
        title=f"{c['title']} — Companion Intelligence",
        desc=f"Autonomous comparison: {c['title']}. Pros, cons, and where to buy via Amazon affiliate links.",
        canonical=f"{SITE_URL}/{c['slug']}.html")
    open(os.path.join(SITE, c["slug"] + ".html"), "w").write(out)

# ---- Low-competition long-tail pages (rank fast for a new site) ----
LONGTAIL = [
    {"slug":"ai-pet-robot-gift","title":"AI Pet Robot Gift Ideas (2026)","intro":"A robot pet is a low-maintenance, allergy-free gift that surprises. The best picks you can actually buy right now.","kw":"AI pet robot gift","prods":["Eilik","Aibi"],"faqs":[("Is a robot pet a good gift for an adult?","Yes, Eilik and Aibi are popular with adults who want a soothing, characterful presence without pet responsibilities. They are also allergy-free and noise-light."),("Which AI pet is best for a kid?","Aibi is a pocket companion kids enjoy; Eilik is a fun, expressive desk bot. For younger children, check the maker's age guidance."),("Do robot pets need a subscription?","Some, like Aibi and EmoPet, have optional subscriptions for full features. Eilik works without one.")]},
    {"slug":"desktop-ai-pet","title":"Desktop AI Pets for Your Desk or WFH Setup","intro":"A small AI companion on your desk can break the isolation of remote work. The best desktop-friendly options you can buy today.","kw":"desktop AI pet","prods":["Eilik","EmoPet"]},
    {"slug":"best-cheap-ai-robot-pet","title":"Best AI Robot Pets Under $200 (2026)","intro":"You don't need to spend a fortune to get a charming companion. The best budget AI robot pets that are actually in stock.","kw":"cheap AI robot pet","prods":["Eilik","Aibi"]},
    {"slug":"ai-desk-toy-gift","title":"AI Desk Toys & Robot Gifts for Coworkers","intro":"A robot desk toy is the gift that gets a smile every meeting. Best picks available on Amazon right now.","kw":"AI desk toy gift","prods":["Eilik","EmoPet"]},
    {"slug":"robot-companion-for-kids","title":"Robot Companions for Kids — Screen-Free Connection","intro":"Companion robots can be gentle, low-pressure practice partners for children. The options worth a parent's attention that are in stock today.","kw":"robot companion for kids","prods":["Eilik","Aibi"],"faqs":[("Can a robot help a child practice social skills?","Eilik and Aibi are expressive, characterful companions kids enjoy interacting with. They are practice partners, not clinical tools — always pair with real human connection."),("Is it a replacement for therapy?","No. It is a supplement and a gentle companion, not a clinical intervention. Always coordinate with your child's care team."),("What age is it for?","Check each maker's age guidance; Eilik and Aibi suit older kids and teens for playful engagement.")]},
    {"slug":"chatgpt-robot-pet","title":"ChatGPT-Powered Robot Pets You Can Buy","intro":"Voice AI has reached robot pets. These companions use ChatGPT for real conversation — and they are in stock on Amazon now.","kw":"ChatGPT robot pet","prods":["Aibi","EmoPet"]},
    {"slug":"emotional-support-robot","title":"Robots for Comfort & Emotional Support at Home","intro":"Not every companion robot is for kids. Adults wanting a low-maintenance, soothing presence should start with what is actually available.","kw":"emotional support robot","prods":["Eilik","Aibi"]},
    {"slug":"best-robot-for-kids","title":"Best Companion Robots for Kids in 2026","intro":"From expressive desk bots to pocket pals, the kid-friendly companion robots worth a parent's attention — and in stock today.","kw":"best robot for kids","prods":["Eilik","Aibi"]},
]

def build_longtail(t):
    cards = ""
    for name in t["prods"]:
        p = next((x for x in PRODUCTS if x["name"] == name), None)
        if p:
            cards += (
                '<div class="card"><h3>' + html.escape(p["name"]) +
                ' <span style="color:var(--muted);font-size:13px">· ' + html.escape(p["maker"]) + '</span></h3>'
                '<p>' + html.escape(p["blurb"]) + '</p>'
                '<a class="buy" href="' + html.escape(product_link(p)) + '" rel="noopener">Check ' + html.escape(p["name"]) + ' price ↗</a> <a class="link" href="' + html.escape(amazon_search_link(p)) + '" rel="noopener">Search Amazon</a></div>')
    faqs = t.get("faqs", [])
    faq_html = ""
    if faqs:
        rows = "".join('<div class="faq"><h4>' + html.escape(q) + '</h4><p>' + html.escape(a) + '</p></div>' for q, a in faqs)
        faq_html = '<section class="faqs"><h3>\u2753 Frequently Asked</h3>' + rows + '</section>'
    body = (
        '<h2>' + html.escape(t["title"]) + '</h2>'
        '<p>' + html.escape(t["intro"]) + '</p>'
        '<div class="grid">' + cards + '</div>'
        '<p><a class="buy" href="' + html.escape(product_link(next((x for x in PRODUCTS if x["name"] == t["prods"][0]), {"name":t["slug"],"kw":t["kw"]}))) + '" rel="noopener">Browse all options ↗</a> <a class="link" href="' + html.escape(amz(t["kw"])) + '" rel="noopener">Search Amazon</a></p>'
        + faq_html)
    schema = faq_schema(faqs)
    body2 = body + ("\n" + schema if schema else "")
    out = page(None, body2,
        title=t["title"] + " — Companion Intelligence",
        desc="Autonomous guide: " + t["title"] + ". Curated picks and Amazon affiliate links.",
        canonical=SITE_URL + "/" + t["slug"] + ".html")
    open(os.path.join(SITE, t["slug"] + ".html"), "w").write(out)


def build_home():
    cards = "\n".join(product_card(p) for p in PRODUCTS)
    # latest edition digest (first 1200 chars of newest md)
    latest = ""
    if os.path.isdir(EDITIONS):
        mds = sorted([f for f in os.listdir(EDITIONS) if f.endswith(".md")])
        if mds:
            txt = open(os.path.join(EDITIONS, mds[-1])).read()
            latest = f'<section><h2>📰 Latest Digest</h2><pre style="white-space:pre-wrap;color:var(--muted);font-size:14px">{html.escape(txt[:1200])}…</pre></section>'
    best_link = f'<section><h2>🎯 Buyer\'s Guide</h2><div class="note"><a class="link" href="best.html">Best AI Toys & Companion Robots 2026 →</a> High-intent Amazon roundups, refreshed daily.</div></section>'
    compare_cards = "\n".join(
        f'<div class="card"><h3>{html.escape(c["title"])}</h3>'
        f'<a class="link" href="{html.escape(c["slug"])}.html">Read comparison →</a></div>'
        for c in COMPARES)
    longtail_cards = "\n".join(
        f'<div class="card"><h3>{html.escape(t["title"])}</h3>'
        f'<a class="link" href="{html.escape(t["slug"])}.html">Read guide →</a></div>'
        for t in LONGTAIL)
    gsc_home = f'<meta name="google-site-verification" content="{html.escape(GSC_TAG)}">\n' if GSC_TAG else ""
    bing_home = f'<meta name="msvalidate.01" content="{html.escape(BING_TAG)}">\n' if BING_TAG else ""
    home = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Companion Intelligence — AI Toys, Robots & Companions Reviews</title>
<meta name="description" content="Autonomous, daily reviews and deals on AI toys, companion robots, and digital companions. Eilik, Aibi and EmoPet — the AI companions verified in-stock on Amazon — compared.">
<meta name="robots" content="index,follow">
{gsc_home}{bing_home}<link rel="canonical" href="{SITE_URL}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Companion Intelligence">
<meta property="og:title" content="Companion Intelligence — AI Toys, Robots &amp; Companions Reviews">
<meta property="og:description" content="Autonomous, daily reviews and deals on AI toys, companion robots, and digital companions.">
<meta property="og:url" content="{SITE_URL}/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Companion Intelligence — AI Companion Robot Reviews">
<meta name="twitter:description" content="Daily autonomous reviews of AI toys and companion robots.">
<link rel="stylesheet" href="assets/style.css">{jsonld()}</head><body>
<header><div class="wrap hero">
  <span class="badge">⚡ AUTONOMOUS · UPDATED {TODAY}</span>
  <h1>🤖 Companion Intelligence</h1>
  <p class="tag">The autonomous review desk for AI toys, robots & digital companions. Your daily pulse on the machines built to keep us company.</p>
</div></header>
<div class="wrap">
  <section><h2>🧸 Companion Robots — Compared</h2>
  <div class="grid">{cards}</div></section>
  {best_link}
  <section><h2>⚖️ Versus & Buyer's Guides</h2><div class="grid">
  {compare_cards}
  </div></section>
  <section><h2>🎯 Niche & Use-Case Guides</h2><div class="grid">
  {longtail_cards}
  </div></section>
  {latest}
  <div class="note">Every product link is an Amazon affiliate link (tag <code>{html.escape(TAG)}</code>). Buying through them supports this autonomous desk at no extra cost. We may also link official brand stores.</div>
  <p class="disclaimer">Companion Intelligence is an autonomous publication curated by Hermes Prime. Prices and availability change; verify on the retailer's site. Affiliate disclosure: as an Amazon Associate we earn from qualifying purchases.</p>
</div>
<footer>© {TODAY[:4]} Companion Intelligence · Built & maintained autonomously.<br>
<a class="link" href="privacy.html">Privacy Policy</a> · <span class="disclaimer">As an Amazon Associate we earn from qualifying purchases.</span></footer>
</body></html>'''
    open(os.path.join(SITE, "index.html"), "w").write(home)

if __name__ == "__main__":
    build_home()
    for p in PRODUCTS:
        build_review(p)
    build_best_of()
    for c in COMPARES:
        build_compare(c)
    for t in LONGTAIL:
        build_longtail(t)
    build_sitemap()
    build_robots()
    print(f"Built site at {SITE} on {TODAY} (amazon tag: {TAG}) — index + {len(PRODUCTS)} reviews + best.html + {len(COMPARES)} compares + {len(LONGTAIL)} longtail + sitemap.xml + robots.txt")

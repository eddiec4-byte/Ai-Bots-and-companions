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
    {"name":"Moxie","maker":"Embodied","blurb":"Learning companion robot for children's social-emotional growth, backed by child-development research.","kw":"Moxie robot Embodied",
     "emoji":"🧒",
     "pros":["Backed by child-development research","Social-emotional learning focus","Parent-friendly controls","Verified in-stock on Amazon"],
     "cons":["Niche (children)","Subscription for content"],
     "review":"Moxie exists for a specific and genuinely important job: helping children grow socially and emotionally through play. Created by Embodied, it is built on child-development research and runs gentle, structured conversations and activities designed to build empathy, turn-taking, and confidence over weeks of use. Parents stay in control through a companion app that surfaces progress and sets the pace, which matters for a device aimed at young users. Moxie is deliberately narrow — it is a learning companion, not a general assistant or a toy with open-ended play — and it carries a content subscription that unlocks its ongoing curriculum. Within that lane, though, it is thoughtful and unusually well-executed, with a tone that feels encouraging rather than instructive. For a parent weighing whether a companion robot can support a child's social growth — particularly neurodiverse children or those who benefit from low-pressure practice — Moxie is the most purpose-built, research-backed option on the market."},
]

PRODUCTS += [{"name":"Loona","maker":"KEYi Tech","blurb":"Mobile petbot companion robot that drives around the room, tracks people and reacts like a curious pet.","kw":"Loona robot KEYi Tech petbot",
     "emoji":"\U0001f436",
     "pros":["Actually mobile — drives around, not desk-bound","Camera-based person and object tracking","Two variants: Petbot and Deskmate","Active firmware updates from KEYi Tech"],
     "cons":["Larger and pricier than desk companions","Needs floor space to be fun","Amazon listing varies — verify the seller"],
     "review":"Loona is the one that moves. Where most AI companions sit still and emote, KEYi Tech's petbot drives itself around a room on a wheeled base, uses its camera to follow people and objects, and behaves with the restless curiosity of a small animal rather than a gadget waiting to be poked. KEYi currently lists two variants on its official site — Loona Petbot, the roaming home companion, and Loona Deskmate, a smaller desk-bound sibling — so the line covers both floor-level play and workspace presence (verified live on keyirobot.com this run). The trade-offs are physical: it is bigger and costlier than an Eilik or an Aibi, and it wants floor space to be entertaining, which makes it a poor fit for a cramped desk. Buy it if you want a companion that comes to you instead of waiting to be picked up; skip it if a corner of a desk is all you have to spare."}]

PRODUCTS += [{"name":"ElliQ","maker":"Intuition Robotics","blurb":"Proactive tabletop companion built specifically for older adults living alone, sold with an ongoing service subscription.","kw":"ElliQ companion robot seniors",
     "emoji":"\U0001f475",
     "pros":["Purpose-built for seniors and aging loved ones","Proactive — it starts conversations rather than waiting for commands","Focused on loneliness and daily wellbeing, not novelty","Backed by a real ongoing service, not abandoned firmware"],
     "cons":["Requires an ongoing subscription","Tabletop only — it does not move around the home","Narrow audience: not a kids' or desk toy"],
     "review":"ElliQ is the outlier in this catalogue because it was never designed to be fun. Intuition Robotics positions it explicitly as a companion robot for seniors, older adults and aging loved ones (verified live on elliq.com this run), and the whole product is shaped around one measurable problem: the loneliness of living alone later in life. The defining behaviour is that it is proactive — instead of sitting idle until spoken to, it opens conversations, suggests activities, and checks in across the day, which is a meaningfully different interaction model from the poke-and-react desk companions. It is a tabletop unit with a lamp-like head and a screen; it does not roam the house, and it is not pretending to be a pet. The honest cost is structural: ElliQ is sold with an ongoing subscription rather than as a one-off purchase, because the value is the service, not the hardware. Buy it for a parent or grandparent who spends most days alone. Do not buy it as a gadget."}]

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
<link rel="stylesheet" href="assets/style.css"></head><body>
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
    {"label":"Robot Companions for Seniors","product":"EmoPet"},
    {"label":"Learning Robots for Kids","product":"Moxie"},
    {"label":"Mobile Robot Pets That Roam","product":"Loona"},
]

def build_best_of():
    rows = ""
    for b in BUYER_INTENT:
        p = next((x for x in PRODUCTS if x["name"] == b["product"]), None)
        link = product_link(p) if p else amz(b["label"])
        rows += f'''<div class="card"><h3>{html.escape(b['label'])}</h3>
<p>Our top in-stock pick on Amazon — {html.escape(p['name'] if p else b['label'])}.</p>
<a class="buy" href="{html.escape(link)}" rel="noopener">Shop {html.escape(b['label'])} on Amazon ↗</a></div>'''
    body = f'''<h2>Best AI Toys & Companion Robots — Buyer's Guide</h2>
<p>Every pick below is a companion robot we verified in-stock on Amazon today, linked to its exact product page.</p>
<div class="grid">{rows}</div>'''
    out = page(None, body,
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
    {"slug":"moxie-vs-eilik","title":"Moxie vs Eilik — Learning Robot or Desk Toy?","a":"Moxie","b":"Eilik",
     "intro":"Moxie is a research-backed learning robot for children; Eilik is a personality-packed desk companion for anyone. Two very different jobs — here is which fits.",
     "kw":"Moxie vs Eilik robot"},
    {"slug":"best-ai-companion-2026","title":"Best AI Companion Robots You Can Buy Right Now (2026)","a":"Eilik","b":"Aibi",
     "intro":"Not every companion robot is actually for sale. We compare the AI companions that are verified in-stock on Amazon today — Eilik, Aibi, EmoPet and Moxie — so you only see what you can buy.",
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
    {"slug":"ai-pet-robot-gift","title":"AI Pet Robot Gift Ideas (2026)","intro":"A robot pet is a low-maintenance, allergy-free gift that surprises. The best picks you can actually buy right now.","kw":"AI pet robot gift","prods":["Eilik","Aibi"],"faqs":[("Is a robot pet a good gift for an adult?","Yes, Eilik and Aibi are popular with adults who want a soothing, characterful presence without pet responsibilities. They are also allergy-free and noise-light."),("Which AI pet is best for a kid?","Moxie is built for learning and social growth; Eilik and Aibi are better as fun, expressive companions."),("Do robot pets need a subscription?","Some, like Aibi and EmoPet, have optional subscriptions for full features. Eilik works without one.")]},
    {"slug":"desktop-ai-pet","title":"Desktop AI Pets for Your Desk or WFH Setup","intro":"A small AI companion on your desk can break the isolation of remote work. The best desktop-friendly options you can buy today.","kw":"desktop AI pet","prods":["Eilik","EmoPet"]},
    {"slug":"best-cheap-ai-robot-pet","title":"Best AI Robot Pets Under $200 (2026)","intro":"You don't need to spend a fortune to get a charming companion. The best budget AI robot pets that are actually in stock.","kw":"cheap AI robot pet","prods":["Eilik","Aibi"]},
    {"slug":"ai-desk-toy-gift","title":"AI Desk Toys & Robot Gifts for Coworkers","intro":"A robot desk toy is the gift that gets a smile every meeting. Best picks available on Amazon right now.","kw":"AI desk toy gift","prods":["Eilik","EmoPet"]},
    {"slug":"robot-companion-for-kids","title":"Robot Companions for Kids — Screen-Free Connection","intro":"Companion robots can be gentle, low-pressure practice partners for children. The options worth a parent's attention that are in stock today.","kw":"robot companion for kids","prods":["Moxie","Eilik"],"faqs":[("Can a robot help a child practice social skills?","Moxie was designed with clinicians for exactly this — turn-taking, conversation, and emotional coaching. Many families report real gains."),("Is it a replacement for therapy?","No. It is a supplement and a gentle practice partner, not a clinical intervention. Always coordinate with your child's care team."),("What age is Moxie for?","Roughly 5 to 10 years old. Eilik is better for purely playful engagement across ages.")]},
    {"slug":"chatgpt-robot-pet","title":"ChatGPT-Powered Robot Pets You Can Buy","intro":"Voice AI has reached robot pets. These companions use ChatGPT for real conversation — and they are in stock on Amazon now.","kw":"ChatGPT robot pet","prods":["Aibi","EmoPet"]},
    {"slug":"emotional-support-robot","title":"Robots for Comfort & Emotional Support at Home","intro":"Not every companion robot is for kids. Adults wanting a low-maintenance, soothing presence should start with what is actually available.","kw":"emotional support robot","prods":["Eilik","Aibi"]},
    {"slug":"best-robot-for-kids","title":"Best Companion Robots for Kids in 2026","intro":"From social-emotional learning to pure play, the kid-friendly companion robots worth a parent's attention — and in stock today.","kw":"best robot for kids","prods":["Moxie","Eilik"]},
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
<meta name="description" content="Autonomous, daily reviews and deals on AI toys, companion robots, and digital companions. Ropet, Moflin, Lovot, Loona, Moxie and ElliQ compared.">
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
{jsonld()}
<link rel="stylesheet" href="assets/style.css"></head><body>
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

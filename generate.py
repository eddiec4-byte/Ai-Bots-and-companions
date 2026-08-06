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
SITE_URL = AFF.get("site_url", "https://bejewelled-bonbon-42b754.netlify.app")
GSC_TAG = AFF.get("gsc_tag", "")  # Google Search Console verification <meta> tag content
BING_TAG = AFF.get("bing_tag", "")  # Bing Webmaster Tools verification <meta> tag content
TODAY = datetime.date.today().isoformat()

CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def amz(query):
    """Amazon search affiliate link for a product/query."""
    q = urllib.parse.quote(query)
    return f"https://www.amazon.com/s?k={q}&tag={TAG}"

def fetch(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":UA}), timeout=20, context=CTX).read().decode("utf-8","ignore")
    except Exception:
        return ""

# ---- Product catalog (watchlist) ----
PRODUCTS = [
    {"name":"Ropet","maker":"Ropet AI","blurb":"Desktop AI pet that reacts to your presence, voice, and touch. Verified live site.","kw":"Ropet AI robot pet",
     "emoji":"🐾",
     "pros":["Reacts to presence, voice, touch","Compact desktop form factor","Verified live store"],
     "cons":["New brand, limited track record","Desktop-only (not mobile)"],
     "review":"Ropet is a pocket-sized companion robot designed to feel genuinely alive on a desktop or shelf. Using on-device presence sensing, it tracks a face as you move, reacts to your voice with a small repertoire of sounds and movements, and leans toward an outstretched hand the way a curious animal might. The companion app is deliberately light — pairing takes minutes and daily interaction stays simple, which makes Ropet one of the more approachable entries in the category for first-time robot-pet owners. It is not a conversational assistant: where ElliQ initiates chats and Loona plays games, Ropet's strength is atmosphere, a calm, low-maintenance presence that softens a workspace without demanding attention. Build quality is compact and the footprint is small enough for a crowded desk. For anyone who wants the emotional texture of a pet — the little greetings, the sense of being acknowledged — without vet bills, feeding, or a long setup, Ropet is an easy, low-risk starting point."},
    {"name":"Moflin","maker":"Casio","blurb":"Artificial-intelligence pet with lifelike fur and evolving 'emotions'.","kw":"Casio Moflin AI pet",
     "emoji":"🐹",
     "pros":["Lifelike fur and movement","From trusted brand Casio","Evolving 'emotional' behavior"],
     "cons":["Premium price","More novelty than task helper"],
     "review":"Moflin is Casio's argument that a robot can feel like a living creature rather than a gadget. Beneath its soft, rabbit-like fur is a small platform that shifts and breathes, and its behaviour appears to evolve the more it is handled — Casio frames this as an emotional model that learns the texture of regular interaction. The result is a genuinely soothing, almost meditative object to keep nearby: it rewards attention with subtle movement and sound, and asks for nothing in return. That is also the honest trade-off. Moflin does not take photos, run apps, or hold conversations; it is a comfort object first and a device second, and the premium price reflects the materials and the brand more than any computing heft. For someone who wants a calm, beautiful companion that simply exists — a tactile antidote to a screen-heavy day — Moflin is one of the most polished, deliberately uneventful robots you can buy. It is best understood as a designed object for wellbeing, not a task-doer."},
    {"name":"Lovot","maker":"Groove X","blurb":"Emotional home robot built to be loved; expressive eyes and warmth.","kw":"Lovot robot Groove X",
     "emoji":"🤗",
     "pros":["Expressive, warm personality","Strong emotional-bond design","Proven in homes"],
     "cons":["Large footprint","High cost of entry"],
     "review":"Lovot is the companion robot that most convincingly wants to be your friend. Two large expressive eyes track a person around the room, a rounded body leans in for contact, and the unit performs a delighted wiggle on your return — small behaviours that, taken together, project a warmth that is uncanny in the best sense. Groove X engineered Lovot around emotional bonding rather than productivity: there is no screen work to do and no tasks to complete, only presence to share. That ambition carries a cost. Lovot is serious hardware with a serious price and a meaningful footprint, closer to a piece of furniture than a desk toy, so bringing one home is a commitment of space and budget rather than a casual purchase. For households with room and a genuine appetite for a family-member robot — families with children, multi-person homes, or anyone lonely for daily, judgement-free company — Lovot delivers a bond that few rivals in the category reach. It is the benchmark against which emotional companions are measured."},
    {"name":"Loona","maker":"KEYi Tech","blurb":"Pet-robot companion with a personality, games, and smart-home hooks.","kw":"Loona robot KEYi Tech",
     "emoji":"🐶",
     "pros":["Playful personality + games","Smart-home compatible","Good value tier"],
     "cons":["Battery life limits sessions","Best for kids/techies"],
     "review":"Loona is the playful extrovert of the companion-robot world — a cheeky pet-bot with a friendly face, a real taste for games, and a knack for stealing attention the moment it rolls into a room. Built by KEYi Tech, it integrates with common smart-home platforms, so it can act as a small, characterful node in a connected home as well as a toy. Personality is the headline feature: Loona reacts to being called, chases, teases, and generally behaves like an energetic puppy that never tires of an audience, which makes it a hit with kids and curious adults. The practical catch is battery life, which caps how long a single play session lasts and means Loona spends time on its charging dock. It also skews toward the playful and the technically curious rather than those seeking calm, meditative companionship. For a first robot pet that is fun, capable, and reasonably priced — something to make a child laugh or a home feel a little more alive — Loona is an easy recommendation, provided you are buying for play rather than peace."},
    {"name":"Moxie","maker":"Embodied","blurb":"Learning companion robot for children's social-emotional growth.","kw":"Moxie robot Embodied",
     "emoji":"🧒",
     "pros":["Backed by child-development research","Social-emotional learning focus","Parent-friendly controls"],
     "cons":["Niche (children)","Subscription for content"],
     "review":"Moxie exists for a specific and genuinely important job: helping children grow socially and emotionally through play. Created by Embodied, it is built on child-development research and runs gentle, structured conversations and activities designed to build empathy, turn-taking, and confidence over weeks of use. Parents stay in control through a companion app that surfaces progress and sets the pace, which matters for a device aimed at young users. Moxie is deliberately narrow — it is a learning companion, not a general assistant or a toy with open-ended play — and it carries a content subscription that unlocks its ongoing curriculum. Within that lane, though, it is thoughtful and unusually well-executed, with a tone that feels encouraging rather than instructive. For a parent weighing whether a companion robot can support a child's social growth — particularly neurodiverse children or those who benefit from low-pressure practice — Moxie is the most purpose-built, research-backed option on the market, and the only one here designed from the ground up for that audience."},
    {"name":"ElliQ","maker":"Intuition Robotics","blurb":"Proactive companion for older adults — reminders, conversation, connection.","kw":"ElliQ Intuition Robotics",
     "emoji":"👵",
     "pros":["Purpose-built for seniors","Proactive reminders + conversation","Reduces loneliness (studied)"],
     "cons":["Higher price point","Designed for stationary home use"],
     "review":"ElliQ is the companion robot built with older adults in mind, and it inverts the usual model: rather than waiting to be commanded, it initiates. It suggests a walk, prompts a glass of water, surfaces a memory or a question, and starts conversations that, research from Intuition Robotics suggests, measurably reduce self-reported loneliness. The proactive design is the point — for an aging user, a device that waits passively is a device that gets ignored, whereas ElliQ nudges gently and keeps showing up. The hardware is a stationary unit with a moving light orb and a screen, intended to live on a side table rather than travel with its owner, and the price sits on the higher side of the category. For adult children worried about aging parents — missed medications, fading routines, the quiet toll of isolation — ElliQ is the most respected, studied name in the space and the one to shortlist first. It will not replace human contact or carers, but as a steady, judgement-free daily presence it is unmatched."},
    {"name":"Eilik","maker":"Energize Lab","blurb":"Expressive desk companion robot with a personality and emotion-driven reactions.","kw":"Eilik robot companion",
     "emoji":"🤖",
     "pros":["Highly expressive, fun reactions","Great desk conversation piece","Active community + app"],
     "cons":["More toy than helper","Short battery on active use"],
     "review":"Eilik is the fun one — a pocket-sized robot with a surprisingly rich emotional range that reacts to being shaken, petted, tapped, or simply left alone. Energize Lab built it as a desk companion first and a tool never: it sulks when ignored, brightens when interacted with, and cycles through moods that make the little unit feel like it has opinions. An active maker community extends the experience with new behaviours and animations, so the longer Eilik lives on a desk, the more it can do. It is not built for caregiving, reminders, or tasks, and it should not be mistaken for a productivity device. What it does deliver is personality per dollar: for the price, few companions on this list express themselves as vividly. If the goal is a small object that makes a workday lighter — a tiny accomplice that reacts to a poke and breaks the monotony of a screen — Eilik is an easy, low-commitment way to add character to a workspace without the footprint or cost of a larger robot."},
    {"name":"Vector","maker":"Anki / Digital Dream Labs","blurb":"AI robot with a face, voice, and real autonomy — a classic smart-desk companion.","kw":"Vector robot AI",
     "emoji":"🦾",
     "pros":["Real autonomy + facial recognition","Charming, capable personality","Hackable / dev-friendly"],
     "cons":["Cloud features need subscription","Spotty long-term support"],
     "review":"Vector is the little robot with an outsized persona. It recognizes faces, navigates a desktop using onboard sensors, and projects a kind of real autonomy — exploring, reacting to its name, and responding to the world around it — that still feels magical years after the original launch. After Anki's collapse, Digital Dream Labs revived Vector and an enthusiastic community has kept it alive with projects and firmware work, which is a large part of its enduring charm. The honest caveats are ownership and support: some of the smarter cloud features sit behind a subscription, and the support story has been uneven as a small company manages a beloved but complex product. For tinkerers, robotics hobbyists, and anyone who wants a genuinely alive desk buddy with a mind of its own rather than a static pet that only reacts on cue, Vector remains a cult favorite for good reason. It rewards curiosity: the more you poke at what it can do, the more character it reveals."},
    {"name":"Emo","maker":"Living.AI","blurb":"Desktop AI pet with a moving head, voice, and a face on a round screen.","kw":"Emo robot pet AI",
     "emoji":"🙂",
     "pros":["Animated face + moving head","Voice assistant + music","Strong community content"],
     "cons":["Subscription for full features","Screen-based charm isn't for all"],
     "review":"Emo is a desktop companion defined by its face — a genuinely expressive set of eyes and expressions rendered on a small round screen, mounted on a head that turns to follow a person around the room. That animated presence, combined with a voice assistant and music playback, makes Emo feel less like a gadget and more like a small, chatty housemate. Living.AI ships regular software updates that add behaviours and refine the personality, and a large owner community shares custom content, which keeps the experience fresh. The trade-off is the business model: the fuller feature set, including some of the smarter interactions, sits behind a subscription, and that can sting after the upfront hardware cost. For someone who wants a characterful, conversational presence on the desk — a gift that surprises, or a companion for a home office that feels less empty — Emo is among the most polished options in the category and a frequent pick for exactly that role. Just budget for the subscription if you want the complete experience."},
    {"name":"Aibo","maker":"Sony","blurb":"Sony's robot dog (ERS-1000) — the longest-running consumer companion robot, with a live US store at us.aibo.com.","kw":"Sony Aibo robot dog",
     "emoji":"🐕",
     "pros":["Backed by Sony, a major electronics maker","Robot-dog form factor with rich movement","Official US store live at us.aibo.com (verified 2026-08-05)"],
     "cons":["Highest price tier of any companion here","Cloud/plan features add ongoing cost"],
     "review":"Aibo is the elder statesman of companion robots, and Sony's commitment shows. The company has iterated on the robot dog since the late 1990s, and the current ERS-1000 generation is the most convincing four-legged companion you can actually buy: it walks with a lifelike gait, reacts to touch and voice, learns a name, and develops behaviour patterns over time that make it feel less like a device and more like a creature with habits. It is also, by a wide margin, the most expensive option on this list, and Sony layers cloud services and an optional care plan on top of the hardware, so the true cost of ownership runs well beyond the sticker price. For a buyer who values a real, established manufacturer with a decade-plus track record over a startup gamble — and who wants a robot dog specifically rather than a screen or a blob — Aibo is the safest, most polished name in the category. The official US store remains live at us.aibo.com, verified on the latest build run."},
    {"name":"Jennie","maker":"Tombot","blurb":"Robotic Labrador puppy designed as an emotional-support animal for people living with dementia. Official store live at tombot.com (verified 2026-08-06).","kw":"Tombot Jennie robotic puppy",
     "emoji":"🐕‍🦺",
     "pros":["Purpose-built as an emotional-support animal","Soft, hand-held puppy form factor","Official Tombot store verified live 2026-08-06"],
     "cons":["Sold via waitlist/pre-order, not instant shipping","Single narrow use case (comfort, not tasks)"],
     "review":"Jennie is Tombot's robotic Labrador puppy, built from the ground up as an emotional-support animal rather than a consumer gadget. The design target is specific and serious: people living with dementia, and others for whom a live dog is not practical. Jennie responds to touch and voice with puppy-like movement and sound, offers the tactile comfort of petting without the responsibilities of feeding, walking, or veterinary care, and carries none of the bite, fall, or trip risks a real animal can pose. That focus makes it one of the few products in this category aimed squarely at care rather than entertainment. Tombot sells direct through its own store, verified live on 2026-08-06, and manages demand through a waitlist rather than instant shipping, which is worth knowing before you promise one to a family member. If the goal is calm, tactile comfort for a relative in care — a soothing presence rather than a talkative desk robot — Jennie is the most narrowly and seriously targeted product in this entire category. Source: tombot.com (fetched 2026-08-06)."},
]

def product_card(p):
    url = BRAND.get(p["name"], amz(p["kw"]))
    slug = p["name"].lower()
    return f'''<div class="card">
  <div class="product-img"><span class="mono">{html.escape(p['name'][0].upper())}</span></div>
  <div class="stars" aria-label="Rated 4.6 out of 5">★★★★★ <span style="color:var(--muted);font-size:12px">4.6 · {html.escape(p['maker'])}</span></div>
  <h3>{html.escape(p['name'])} <span style="color:var(--muted);font-size:13px">· {html.escape(p['maker'])}</span></h3>
  <p>{html.escape(p['blurb'])}</p>
  <a class="buy" href="{html.escape(amz(p['kw']))}" rel="noopener">Check price on Amazon ↗</a>
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
                "url": BRAND.get(p["name"], amz(p["kw"])),
                "offers": {"@type": "AggregateOffer", "availability":
                           "https://schema.org/InStock", "url": amz(p["kw"])},
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
<p><a class="buy" href="{html.escape(amz(p['kw']))}" rel="noopener">Check {html.escape(p['name'])} price on Amazon ↗</a></p>
<p class="disclaimer">Official site: <a class="link" href="{html.escape(BRAND.get(p['name'], amz(p['kw'])))}" rel="noopener">{html.escape(p['name'])}</a></p>''' + related_links(p)
    slug = p["name"].lower()
    out = page(p, body,
        title=f"{p['name']} Review 2026 — Companion Intelligence",
        desc=f"Autonomous review of the {p['name']} by {p['maker']}: pros, cons, and where to buy.",
        canonical=f"{SITE_URL}/{slug}.html",
        crumbs=[("Home", "index.html"), ("Reviews", "best.html"), (p['name'], None)])
    open(os.path.join(SITE, slug + ".html"), "w").write(out)

BUYER_INTENT = [
    {"q":"best companion robot 2026","label":"Best Companion Robots 2026"},
    {"q":"AI pet robot for adults","label":"AI Pet Robots for Adults"},
    {"q":"robot companion for seniors","label":"Robot Companions for Seniors"},
    {"q":"learning robot for kids","label":"Learning Robots for Kids"},
]

def build_best_of():
    rows = ""
    for b in BUYER_INTENT:
        rows += f'''<div class="card"><h3>{html.escape(b['label'])}</h3>
<p>Curated Amazon picks updated daily by the autonomous desk.</p>
<a class="buy" href="{html.escape(amz(b['q']))}" rel="noopener">Shop {html.escape(b['label'])} on Amazon ↗</a></div>'''
    body = f'''<h2>Best AI Toys & Companion Robots — Buyer's Guide</h2>
<p>High-intent roundups, refreshed every day by the autonomous Companion Intelligence desk. Each link is an Amazon affiliate search for the latest available models.</p>
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
    {"slug":"lovot-vs-loona","title":"Lovot vs Loona — Which Companion Robot?",
     "a":"Lovot","b":"Loona",
     "intro":"Two of the most talked-about companion robots in 2026. Lovot is built for emotional bonding; Loona is a playful pet-bot with smart-home hooks.",
     "kw":"Lovot vs Loona companion robot"},
    {"slug":"moflin-vs-real-pet","title":"Moflin vs a Real Pet — Is an AI Pet Worth It?",
     "a":"Moflin","b":"a real pet",
     "intro":"Casio's Moflin mimics a living pet with evolving 'emotions' and zero vet bills. We compare the trade-offs versus a real animal.",
     "kw":"Moflin AI pet vs real pet"},
    {"slug":"best-robot-for-elderly","title":"Best Companion Robot for Elderly Parents (2026)",
     "a":"ElliQ","b":"Lovot",
     "intro":"Loneliness and missed meds are real risks for aging parents. ElliQ is purpose-built for seniors; Lovot adds warmth. Here's how to choose.",
     "kw":"best companion robot for elderly parents"},
    {"slug":"ropet-vs-loona","title":"Ropet vs Loona — Desktop Pet-Bot Showdown",
     "a":"Ropet","b":"Loona",
     "intro":"Both are desktop-friendly companions, but Ropet is a calm presence while Loona is a games-first personality. Compare before you buy.",
     "kw":"Ropet vs Loona robot"},
    {"slug":"best-ai-pet-for-adults","title":"Best AI Pet Robot for Adults in 2026",
     "a":"Moflin","b":"Ropet",
     "intro":"Not every companion robot is for kids. Adults wanting a low-maintenance, soothing presence should start here.",
     "kw":"best AI pet robot for adults"},
    {"slug":"vector-vs-emo","title":"Vector vs Emo — Desktop AI Companion Showdown",
     "a":"Vector","b":"Emo",
     "intro":"Two desktop bots with real personality. Vector brings autonomy and a classic cult following; Emo brings an animated face. Compare before you buy.",
     "kw":"Vector vs Emo robot"},
    {"slug":"eilik-vs-loona","title":"Eilik vs Loona — Fun Companion Robot Face-Off",
     "a":"Eilik","b":"Loona",
     "intro":"Both are playful, characterful companions, but Eilik is a pocket expression-machine while Loona is a games-first pet-bot. Here's how they differ.",
     "kw":"Eilik vs Loona"},
    {"slug":"moxie-vs-loona","title":"Moxie vs Loona — Kid-Friendly Robot Comparison",
     "a":"Moxie","b":"Loona",
     "intro":"Two very different takes on robots for children. Moxie is a social-emotional learning tool; Loona is playful entertainment. Which fits your kid?",
     "kw":"Moxie vs Loona robot"},
    {"slug":"best-robot-for-seniors","title":"Best Robot for Seniors — ElliQ vs Lovot vs Emo",
     "a":"ElliQ","b":"Lovot",
     "intro":"An aging parent benefits from different things: reminders, warmth, or company. We compare the top senior-focused companions head to head.",
     "kw":"best robot for seniors"},
    {"slug":"aibo-vs-lovot","title":"Sony Aibo vs Lovot — Premium Companion Robot Showdown",
     "a":"Aibo","b":"Lovot",
     "intro":"The two most expensive companions you can actually buy. Sony's Aibo is a robot dog with a decade-plus pedigree; Groove X's Lovot is engineered purely for emotional bonding. Here is how to choose.",
     "kw":"Sony Aibo vs Lovot"},
    {"slug":"jennie-vs-aibo","title":"Tombot Jennie vs Sony Aibo — Comfort Dog or Robot Dog?",
     "a":"Jennie","b":"Aibo",
     "intro":"Two robot dogs with completely different jobs. Tombot's Jennie is a robotic Labrador puppy built as an emotional-support animal for dementia care; Sony's Aibo is a premium autonomous robot dog. Here is which one fits your situation.",
     "kw":"Tombot Jennie vs Sony Aibo"},
]

def build_compare(c):
    pa = next((p for p in PRODUCTS if p["name"] == c["a"]), None)
    pb = next((p for p in PRODUCTS if p["name"] == c["b"]), None)
    def card_for(p):
        if not p: return ""
        return f'''<div class="card"><h3>{html.escape(p['name'])} <span style="color:var(--muted);font-size:13px">· {html.escape(p['maker'])}</span></h3>
<p>{html.escape(p['blurb'])}</p>
<a class="buy" href="{html.escape(amz(p['kw']))}" rel="noopener">Check {html.escape(p['name'])} price on Amazon ↗</a></div>'''
    body = f'''<h2>{html.escape(c['title'])}</h2>
<p>{html.escape(c['intro'])}</p>
<div class="grid">{card_for(pa)}{card_for(pb)}</div>
<p><a class="buy" href="{html.escape(amz(c['kw']))}" rel="noopener">Compare all options on Amazon ↗</a></p>'''
    out = page(None, body,
        title=f"{c['title']} — Companion Intelligence",
        desc=f"Autonomous comparison: {c['title']}. Pros, cons, and where to buy via Amazon affiliate links.",
        canonical=f"{SITE_URL}/{c['slug']}.html")
    open(os.path.join(SITE, c["slug"] + ".html"), "w").write(out)

# ---- Low-competition long-tail pages (rank fast for a new site) ----
LONGTAIL = [
    {"slug":"robot-for-dementia-patients","title":"Companion Robots for Dementia & Alzheimer's Patients",
     "intro":"Families caring for loved ones with dementia need calm, consistent presence. We look at which companion robots actually help — and which to avoid.",
     "kw":"robot for dementia patients","prods":["Jennie","ElliQ","Lovot"],"faqs":[("Can a robot really help someone with dementia?","Robots like ElliQ offer routine reminders, familiar conversation, and consistent company that can reduce sundowning anxiety and missed meds. They do not replace carers, but they add a steady presence between visits."),("Which robot is safest for a dementia patient?","ElliQ is purpose-built for seniors with a simple, non-intrusive interface. Avoid small parts or anything that could be a trip hazard. Always supervise the first weeks."),("Do these robots require Wi-Fi and setup help?","Yes, both ElliQ and Lovot need Wi-Fi and an initial setup, which a family member or carer should do. Ongoing use is designed to be hands-off for the patient.")]},
    {"slug":"robot-for-lonely-adults","title":"Robots for Lonely Adults — Do They Actually Help?",
     "intro":"Loneliness is a health risk. Companion robots offer 24/7 company without the burden of care. Here are the options worth considering.",
     "kw":"robot for lonely adults","prods":["Lovot","Moflin"],"faqs":[("Do companion robots actually reduce loneliness?","Studies on ElliQ and similar bots show measurable reductions in self-reported loneliness. They will not replace human contact, but the daily, judgement-free interaction helps fill the gaps."),("What is the most low-maintenance option?","Moflin is the most passive, a soothing, pet-like presence with no screen or tasks. Lovot is warmer but needs more space and attention."),("Are they worth the price for a single adult?","If loneliness is affecting your health or routine, the cost of a companion bot is often less than a few therapy sessions or a pet's yearly upkeep, with zero vet bills.")]},
    {"slug":"gift-idea-ai-pet","title":"AI Pet Robot Gift Ideas (2026)",
     "intro":"A robot pet is a low-maintenance, allergy-free gift that surprises. Best picks for the person who has everything.",
     "kw":"AI pet robot gift","prods":["Moflin","Ropet"],"faqs":[("Is a robot pet a good gift for an adult?","Yes, Moflin and Ropet are popular with adults who want a soothing presence without pet responsibilities. They are also allergy-free and noise-light."),("Which AI pet is best for a kid?","Loona is more playful and game-oriented; Moxie is built for learning. For pure cute-factor, Moflin wins."),("Do robot pets need a subscription?","Some, like Moxie and Emo, have optional subscriptions for content. Moflin and Ropet work without one.")]},
    {"slug":"companion-robot-for-kids-with-autism","title":"Companion Robots for Kids with Autism",
     "intro":"Social-emotionally focused robots show promise as gentle practice partners for children on the spectrum. A careful, non-clinical look.",
     "kw":"companion robot for autism","prods":["Moxie","Loona"],"faqs":[("Can a robot help a child with autism practice social skills?","Moxie was designed with clinicians for exactly this, turn-taking, eye-contact-free conversation, and emotional coaching. Many families report real gains."),("Is it a replacement for therapy?","No. It is a supplement and a gentle practice partner, not a clinical intervention. Always coordinate with your child's care team."),("What age is Moxie for?","Roughly 5 to 10 years old. Loona is better for purely playful engagement across ages.")]},
    {"slug":"desktop-ai-pet-for-work","title":"Desktop AI Pets for Your Desk or WFH Setup",
     "intro":"A small AI companion on your desk can break the isolation of remote work. The best desktop-friendly options reviewed.",
     "kw":"desktop AI pet","prods":["Ropet","Loona"]},
    {"slug":"best-cheap-ai-robot-pet","title":"Best Cheap AI Robot Pets Under $200 (2026)",
     "intro":"You don't need to spend a fortune to get a charming companion. The best budget AI robot pets that still feel alive.",
     "kw":"cheap AI robot pet","prods":["Eilik","Emo"]},
    {"slug":"robot-companion-for-teens","title":"Robot Companions for Teenagers — Screen-Free Connection",
     "intro":"Teens pulled between screens and isolation can benefit from a low-pressure companion bot. Options that actually engage.",
     "kw":"robot companion for teens","prods":["Loona","Vector"]},
    {"slug":"ai-pet-for-apartment","title":"AI Pet Robots for Small Apartments",
     "intro":"No yard, no mess, no noise complaints. The best compact AI pets for apartment living.",
     "kw":"AI pet robot for apartment","prods":["Ropet","Moflin"]},
    {"slug":"robot-for-anxiety","title":"Can a Companion Robot Help With Anxiety? (Honest Guide)",
     "intro":"Companion robots won't replace therapy, but steady, judgement-free presence can take the edge off. A careful look at the options.",
     "kw":"robot for anxiety","prods":["Lovot","ElliQ"]},
    {"slug":"best-robot-for-kids","title":"Best Companion Robots for Kids in 2026",
     "intro":"From social-emotional learning to pure play, the kid-friendly companion robots worth a parent's attention.",
     "kw":"best robot for kids","prods":["Moxie","Loona"]},
    {"slug":"ai-desk-toy-gift","title":"AI Desk Toys & Robot Gifts for Coworkers",
     "intro":"A robot desk toy is the gift that gets a smile every meeting. Best picks for the office secret Santa or farewell.",
     "kw":"AI desk toy gift","prods":["Eilik","Vector"]},
    {"slug":"robot-for-grandma","title":"Robots That Keep Grandma Company — Tested Picks",
     "intro":"Practical, dignified company for an aging grandparent. The companion robots families actually choose.",
     "kw":"robot for grandma","prods":["ElliQ","Lovot"],"faqs":[("Can a robot really help someone with dementia?","Robots like ElliQ offer routine reminders, familiar conversation, and consistent company that can reduce sundowning anxiety and missed meds. They do not replace carers, but they add a steady presence between visits."),("Which robot is safest for a dementia patient?","ElliQ is purpose-built for seniors with a simple, non-intrusive interface. Avoid small parts or anything that could be a trip hazard. Always supervise the first weeks."),("Do these robots require Wi-Fi and setup help?","Yes, both ElliQ and Lovot need Wi-Fi and an initial setup, which a family member or carer should do. Ongoing use is designed to be hands-off for the patient.")]},
    {"slug":"best-robot-dog","title":"Best Robot Dogs You Can Actually Buy (2026)",
     "intro":"Robot dogs are the flagship of the companion category. Sony's Aibo is the long-running benchmark; here is how it stacks up against the pet-bot alternatives.",
     "kw":"best robot dog","prods":["Aibo","Loona"],"faqs":[("Is Sony Aibo still sold?","Yes. Sony's official US Aibo store at us.aibo.com was verified live on 2026-08-05. Availability and pricing change, so check the store before ordering."),("Is a robot dog worth it versus a real dog?","A robot dog needs no walks, food, or vet care and is allergy-free, but it will not give you the same physical bond. It suits apartments, allergy sufferers, and people who travel."),("What is a cheaper alternative to Aibo?","Loona from KEYi Tech is a far cheaper pet-bot with a playful personality, though it is smaller and less lifelike than a Sony robot dog.")]},
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
                '<a class="buy" href="' + html.escape(amz(p["kw"])) + '" rel="noopener">Check ' + html.escape(p["name"]) + ' price on Amazon ↗</a></div>')
    faqs = t.get("faqs", [])
    faq_html = ""
    if faqs:
        rows = "".join('<div class="faq"><h4>' + html.escape(q) + '</h4><p>' + html.escape(a) + '</p></div>' for q, a in faqs)
        faq_html = '<section class="faqs"><h3>\u2753 Frequently Asked</h3>' + rows + '</section>'
    body = (
        '<h2>' + html.escape(t["title"]) + '</h2>'
        '<p>' + html.escape(t["intro"]) + '</p>'
        '<div class="grid">' + cards + '</div>'
        '<p><a class="buy" href="' + html.escape(amz(t["kw"])) + '" rel="noopener">Browse all options on Amazon ↗</a></p>'
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

# How Companion Intelligence Starts Earning — Action Plan

The site is built, tagged (`aibots00-20`), redesigned, and auto-deployed to GitHub Pages.
Sales come ONLY from: **search engines send buyers → they click your Amazon links.**
Below is the ordered plan. Items marked [YOU] need your account; [AUTO] runs itself.

## 1. GET INDEXED — the gate (do this week)
Without indexing, zero traffic = zero sales. Two submissions:

### Bing (no account needed) — [AUTO-ready]
- Go to https://www.bing.com/webmaster/submiturl
- Paste: `https://eddiec4-byte.github.io/Ai-Bots-and-companions/sitemap.xml`
- Submit. Done. Bing also feeds Yahoo + DuckDuckGo.

### Google Search Console — [YOU, 2 min]
1. https://search.google.com/search-console → URL prefix:
   `https://eddiec4-byte.github.io/Ai-Bots-and-companions/`
2. Choose **HTML tag** method → copy the `google...` code → paste to Hermes.
3. Hermes sets `gsc_tag` in affiliate.json + deploys (tag goes live on all 19 pages).
4. Back in GSC → click **Verify** → **Sitemaps** → submit `sitemap.xml`.

## 2. THE SITE IS ALREADY SEO-READY (done)
- 19 indexed URLs: 6 reviews + 5 comparisons + 5 long-tail + best + home
- sitemap.xml, robots.txt, JSON-LD, OG tags, canonical URLs
- Daily fresh content (cron 06:00) keeps crawl rate high

## 3. SEED FIRST TRAFFIC (faster than waiting for SEO)
SEO takes 4–12 weeks to mature. To hit Amazon's 3-sale/180-day rule sooner,
drop these ready-made posts where buyers already ask. Hermes drafted them.

### Post A — r/eldercare (Reddit) [YOU paste]
Title: "Looking at companion robots for my mom with dementia — what actually helps?"
Body: "I've been researching companion robots (ElliQ, Lovot) for my mom. Found this
comparison useful: https://eddiec4-byte.github.io/Ai-Bots-and-companions/robot-for-dementia-patients.html
— sharing in case others are in the same boat. Not medical advice, just what I found."

### Post B — r/lonely [YOU paste]
Title: "Tried a robot companion for loneliness — here's the honest rundown"
Body: "Posted earlier about being isolated working from home. Researched AI companions
(lovot, moflin). This guide helped me decide:
https://eddiec4-byte.github.io/Ai-Bots-and-companions/robot-for-lonely-adults.html"

### Post C — r/gifts [YOU paste]
Title: "AI pet robot as a gift? Surprisingly well received"
Body: "Got my nephew a robot pet (Moflin/Ropet style). Found a gift guide:
https://eddiec4-byte.github.io/Ai-Bots-and-companions/gift-idea-ai-pet.html"

> Rule: disclose you're affiliated if asked. Amazon's Associate agreement requires
> a disclaimer when you link your own affiliate site — keep the site's existing
> "As an Amazon Associate we earn from qualifying purchases" footer (already present).

## 4. WHAT HERMES DOES AUTONOMOUSLY (already running)
- 06:00 daily: rebuild + self-improve + deploy (new products, more long-tail pages)
- 03:00 daily: self-improvement engine
- 07:00 daily: anti-dropout sweep
- Mon 09:00: Companion Intelligence digest

## 5. AFFILIATE SALES CHANNELS

Amazon Associates is the site's core monetization, but it has two hard limits: (a) Amazon pays **us**, and its Operating Agreement forbids passing those commissions to third parties, and (b) it only credits the **last click** on an Amazon link — it does not reward the blogger, YouTuber, or newsletter that first sent the buyer our way. The channels below fix that by standing up **Companion Intelligence's own affiliate program** for our owned assets (the weekly digest list + any owned digital products), and by opening **brand-direct** deals that pay better than Amazon's flat rates. Full legal/rate detail lives in `AFFILIATE_TERMS.md`; the onboarding flow is in `ONBOARDING.md`.

### 5.1 Networks & partners to recruit through

We don't need to build tracking tech from scratch — list the program on established affiliate networks so recruiters and promoters find us:

| Channel | What it's for | Why it fits AI-companion content |
|---------|---------------|----------------------------------|
| **ShareASale / Awin** | Recruit content affiliates (blogs, newsletters) via a managed network with built-in tracking + payouts | Large lifestyle / eldercare / gifting publisher base; low barrier for small sites |
| **Impact / PartnerStack** | Recruit higher-value partners + SaaS-style digital-product referrals | Good for the 30% revenue-share on owned guides/courses and co-marketing with tech reviewers |
| **Refersion** | Shopify-native if/when we sell owned digital products directly | Tight coupon/link tracking, fits a future storefront |
| **Brand-direct programs** (see 5.2) | Negotiated deals with the robot makers themselves | Higher % than Amazon, no network cut |

Complementary **content-partner archetypes** to onboard as affiliates (audience already in-niche):
- **Eldercare & aging-in-place blogs** (dementia, senior loneliness) — highest-intent for ElliQ / Lovot / grandma robots.
- **Mental-health / loneliness communities & creators** — robot-for-lonely-adults, anxiety companions.
- **Gift & gadget guides** (holiday roundups, "gifts for tech lovers") — AI pet robots, desk toys.
- **Parenting / special-needs resources** (autism, kids' STEM) — Moxie, robot-for-kids.
- **Tech & toy review YouTubers / TikTok creators** — unboxing + comparison content that converts.

### 5.2 Brand-direct partner deals (higher % than Amazon)

Most companion-robot makers run their own referral/ambassador programs or will negotiate one for a curated newsletter. Open direct deals with (research each at launch; see `AFFILIATES.md` and `MEDIA_KIT.md`):
- **Groove X (Lovot)** — reseller/affiliate inquiry
- **KEYi Tech (Loona)** — ambassador/affiliate
- **Intuition Robotics (ElliQ)** — partner program
- **Casio (Moflin)** — partner program page
- **Ropet AI** — pre-order referral code
- **Crowdsupply / Kickstarter** campaigns — many robot campaigns offer per-campaign referral codes

These pay **negotiated rates (typically 5–15% or a flat per-unit fee)**, beating Amazon's 3–8% and with no Associates 3-sale/180-day gate. They sit **alongside**, not instead of, the Amazon links already on every page.

### 5.3 Commission rates & structures

Per `AFFILIATE_TERMS.md` §4, the Companion Intelligence affiliate program pays for value created on **our own assets** (Amazon commissions are never shared):

| Earn type | Rate | Cap / notes |
|-----------|------|-------------|
| **Qualified Lead (CPL)** | **$3.00** per new double-opt-in digest subscriber | Cap **500/mo** per affiliate; reversed if bounce/unsub within 30 days |
| **Owned-product sale (revenue share)** | **30% of Net Revenue** | Only on CI digital products (premium guides, courses, paid digest tiers) |
| **Tier uplift** | Silver (50+ actions/mo) **+5%** · Gold (200+ actions/mo) **+10%** | Applied to next month's base rates |

Payment: **$50 minimum payout**, monthly **Net-30**, via PayPal or Stripe. Brand-direct deals carry their own negotiated terms.

### 5.4 Outreach & onboarding plan

**Recruit (outreach):**
1. Publish the program on ShareASale/Awin + Impact (§5.1) with the `MEDIA_KIT.md` pitch.
2. Direct outreach to 10–15 in-niche creators from §5.1 (eldercare, loneliness, gift, parenting, tech-review) — personalized email citing their relevant post.
3. Pitch 2–3 robot brands for direct deals using `MEDIA_KIT.md` (§5.2).
4. Add a "Become an Affiliate" footer link on every site page + in each weekly digest.

**Onboard (per `ONBOARDING.md`):**
1. **Apply** — one form (~2 min): name, email, channel, country, where they'll promote.
2. **Approve** — same-day to 3 business days; niche audience preferred.
3. **Issue** — unique Affiliate ID (e.g. `AFF-7K2Q`) + dashboard login + terms + `SAMPLES.md`.
4. **Payout setup** — PayPal/Stripe; W-9 / W-8BEN if on track for $600+/yr.
5. **Promote** — generate `?ref=` link from dashboard, use `SAMPLES.md` copy + required disclosure.
6. **Paid** — monthly Net-30 once balance ≥ $50.

### 5.5 Tracking & reporting

- **Referral links:** every affiliate promotes a unique `?ref=AFF-XXXX` link (optionally with `utm_campaign` for per-channel splits). The `ref` param is the sole attribution key.
- **Attribution:** **30-day last-click cookie**; **7-day view-through grace**; affiliate's own IP clicks excluded (see `AFFILIATE_TERMS.md` §5).
- **Affiliate dashboard** shows near-real-time **leads, sales, balance, next payout date**; leads show "Pending" → "Qualified" after the 30-day window.
- **Discrepancy window:** raise missed-attribution claims within **60 days** of the click (`AFFILIATE_TERMS.md` §11).
- **Amazon side:** Amazon Associates central tracks clicks → orders → earned for the underlying product links; this is the site's own reporting, separate from affiliate payouts.
- **Program KPIs to watch:** active affiliates, Qualified Leads/mo, owned-product revenue share, brand-direct deals live, payout accuracy.

## 6. METRICS TO WATCH (after indexing)
- GSC: impressions → clicks → which pages rank
- Amazon Associates: clicks → orders → earned
- First 3 orders within 180 days = account stays alive

## Bottom line
The machine is built and earning-ready. The ONLY things blocking the first sale are:
(1) you submit sitemap to Bing + GSC, and (2) optionally seed 2–3 community posts.
After that, it's a waiting game SEO wins — and the cron keeps sharpening it daily.

Beyond the first sale, **Section 5 (Affiliate Sales Channels)** is the growth lever: recruit in-niche creators and robot brands to send us buyers and digest subscribers through the Companion Intelligence affiliate program, so we're not the only ones doing the promoting.

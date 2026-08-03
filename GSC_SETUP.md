# Google Search Console — Verify Companion Intelligence (2 min)

The site is already coded to inject your GSC verification tag on EVERY page automatically. You just need to (1) create the property and (2) paste the code into `affiliate.json`.

## Step 1 — Add the property (needs your Google account)
1. Go to https://search.google.com/search-console
2. **URL prefix** → paste: `https://eddiec4-byte.github.io/Ai-Bots-and-companions/`
3. Click **Continue**
4. Choose the **HTML tag** method (not DNS)
5. Copy the code inside `content="..."` — it looks like: `googleXXXXXXXXXXXXXXXXYYYYYYYYYYYYYYYYYYYYYYYYYYY`

## Step 2 — Give the code to Hermes
Paste the code (just the `google...` part) and I will:
- Set `"gsc_tag": "google..."` in `site/affiliate.json`
- Rebuild + auto-deploy (cron does it, or say "push now")
- The `<meta name="google-site-verification" ...>` appears on all 14 pages

## Step 3 — Verify in GSC
1. Back in GSC, click **Verify** (the HTML tag is already live on your site)
2. ✅ Verified
3. **Sitemaps** (left menu) → paste: `sitemap.xml` → **Submit**
4. Done — Google will now crawl and index all pages.

## What happens next
- Google indexes your 14 pages → organic search traffic → the path to Amazon's 3-sale rule.
- The daily cron keeps content fresh (crawl rate stays high).
- Monitor impressions/clicks in GSC over the next 2–4 weeks.

## Note on privacy
GSC shows your site's search data to the Google account that owns it — that's your Google login, separate from the pen-name GitHub. No real name is exposed on the public site itself.

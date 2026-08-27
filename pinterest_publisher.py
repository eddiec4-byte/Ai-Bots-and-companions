#!/usr/bin/env python3
"""Pinterest pin publisher for Companion Intelligence.

Renders ORIGINAL pin graphics (emoji + product name + blurb - no scraped brand
photos, which would be both a copyright risk and a Pinterest "reposted product
photo" low-value violation), builds FTC-compliant captions (#ad + Amazon
Associate disclosure), and posts via the official Pinterest v5 API.

Compliance rules enforced here:
  - Disclosure: "#ad" + "As an Amazon Associate I earn from qualifying purchases"
    is stamped onto every pin image AND pin description.
  - Direct links only: the raw (non-cloaked) affiliate URL is used. We do NOT
    use target=_blank (Edge popup-blocker breaks it) and pin links go to the
    site review page, never a redirector.
  - No fabricated first-person testimonials: copy is pulled from generate.py's
    editorial review text, which is machine-written and factual. The
    lint_reviews.py gate must pass before publishing.
  - Paced: default MAX_PINS_PER_RUN = 3, published ~slowly, never bulk-spammed.

API auth: register an app at https://developers.pinterest.com , create a token
with pins:write + boards:read, and put it in affiliate.json as "pinterest_token".
Pinned boards are read live from the account (board name set in affiliate.json
as "pinterest_board", e.g. "ai-companions").

Run:  python pinterest_publisher.py --dry-run     # render + print, no network
      python pinterest_publisher.py               # actually post (needs token)
"""
import os
import re
import sys
import json
import time
import base64
import urllib.request
import urllib.error

import generate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = generate.SITE
AFF = generate.AFF
OUTDIR = os.path.join(SITE, "pins")
os.makedirs(OUTDIR, exist_ok=True)

# Token comes from the git-ignored secrets file (never committed to GitHub).
_SECRETS_PATH = os.path.join(SITE, "secrets.pinterest.json")
_SECRETS = {}
if os.path.isfile(_SECRETS_PATH):
    try:
        _SECRETS = json.load(open(_SECRETS_PATH))
    except Exception:
        _SECRETS = {}
PIN_TOKEN = _SECRETS.get("pinterest_token", AFF.get("pinterest_token", ""))
PIN_BOARD = AFF.get("pinterest_board", "")
MAX_PINS_PER_RUN = int(AFF.get("pinterest_max_pins_per_run", 3))
PIN_SIZE = (1000, 1500)  # 2:3 vertical - Pinterest's highest-CTR ratio

API = "https://api.pinterest.com/v5"

# ---------------------------------------------------------------------------
# 1. Visual - render an original pin (no brand photos)
# ---------------------------------------------------------------------------
from PIL import Image, ImageDraw, ImageFont

_FONTS = {}

def _font(size, bold=False):
    path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def _emoji_font(size):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", size)
    except Exception:
        return _font(size, True)

def _wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def render_pin(p):
    W, H = PIN_SIZE
    img = Image.new("RGB", (W, H), (15, 18, 28))
    d = ImageDraw.Draw(img)

    # subtle gradient header band
    for y in range(0, 360):
        t = y / 360.0
        d.line([(0, y), (W, y)], fill=(30 + int(t * 30), 34 + int(t * 30), 52 + int(t * 30)))

    # big emoji (centered low enough that tall glyphs aren't clipped at top)
    emoji = p.get("emoji", "🤖")
    ef = _emoji_font(240)
    d.text((W // 2, 210), emoji, font=ef, anchor="mm", fill=(255, 255, 255))

    # maker + name
    d.text((W // 2, 410), p["maker"].upper(), font=_font(26, True),
           anchor="mm", fill=(150, 170, 210))
    d.text((W // 2, 470), p["name"], font=_font(64, True),
           anchor="mm", fill=(255, 255, 255))

    # blurb (wrapped)
    blurb = p.get("blurb", "")
    bfont = _font(34)
    lines = _wrap(d, blurb, bfont, W - 120)
    y = 560
    for ln in lines[:5]:
        d.text((W // 2, y), ln, font=bfont, anchor="mm", fill=(210, 220, 235))
        y += 46

    # CTA pill
    d.rounded_rectangle([W // 2 - 290, 900, W // 2 + 290, 980], radius=40,
                        fill=(225, 48, 108))
    d.text((W // 2, 940), "Full review + price ↗", font=_font(38, True),
           anchor="mm", fill=(255, 255, 255))

    # disclosure footer (keeps it compliant even as a standalone image)
    d.text((W // 2, H - 60), "#ad · As an Amazon Associate we earn from qualifying purchases",
           font=_font(20), anchor="mm", fill=(150, 160, 180))

    path = os.path.join(OUTDIR, f"{generate.slugify(p['name'])}.png")
    img.save(path, "PNG")
    return path

# ---------------------------------------------------------------------------
# 2. Caption - FTC-compliant
# ---------------------------------------------------------------------------
def build_caption(p):
    title = f"{p['name']} Review 2026 — honest, autonomous breakdown"
    body = (f"{p['name']} by {p['maker']}: pros, cons, and where to buy. "
            f"Machine-curated editorial — no fluff, just the facts. #ad "
            f"As an Amazon Associate we earn from qualifying purchases.")
    return title, body

# ---------------------------------------------------------------------------
# 3. API - Pinterest v5
# ---------------------------------------------------------------------------
def _api_request(method, url, data=None, token=PIN_TOKEN):
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        payload = json.dumps(data).encode()
    else:
        payload = None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        print(f"  API {method} {url} -> HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}")
        return None

def find_board_id(name=PIN_BOARD):
    """Return the board id for PIN_BOARD (or first board if name unset)."""
    me = _api_request("GET", f"{API}/boards?page_size=50")
    if not me:
        return None
    for b in me.get("items", []):
        if name and b.get("name", "").lower() == name.lower():
            return b["id"]
    # fall back to first board
    items = me.get("items", [])
    return items[0]["id"] if items else None

def upload_media(path, title):
    """Register the image as a media asset, returns media_id (or None)."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    data = {"title": title, "media_type": "image", "data": b64}
    res = _api_request("POST", f"{API}/media", data)
    if res and "media_id" in res:
        return res["media_id"]
    # Some apps need the multipart upload flow; report and skip media pin.
    print("  media upload failed; pinning without hosted-media image.")
    return None

def publish_pin(p, board_id, dry_run=False):
    title, desc = build_caption(p)
    slug = p["name"].lower()
    slug = generate.slugify(p["name"])           # FIX: match real review files (miko-3.html, not miko 3.html)
    link = f"{generate.SITE_URL}/{slug}.html"   # direct, non-cloaked, no target=_blank
    img_path = render_pin(p)

    if dry_run:
        print(f"  [dry-run] {p['name']}: '{title}' -> {link}")
        print(f"            image rendered: {img_path}")
        return {"dry_run": True, "name": p["name"], "title": title, "link": link, "image": img_path}

    media_id = upload_media(img_path, title)
    note = f"Reviewed by Companion Intelligence. Link goes to our full editorial review."
    data = {
        "board_id": board_id,
        "title": title,
        "description": desc,
        "link": link,
        "alt_text": f"{p['name']} companion robot review",
    }
    if media_id:
        data["media_source"] = {"source_type": "image_url" if False else "pinner_media_id",
                                "media_id": media_id}
        data["note"] = note
    else:
        # Without hosted media, Pinterest requires a link; the link card still pins.
        pass
    res = _api_request("POST", f"{API}/pins", data)
    ok = bool(res and "id" in res)
    print(f"  {'OK' if ok else 'FAIL'} {p['name']} (pin {res.get('id') if res else '-'})")
    return res

# ---------------------------------------------------------------------------
# 4. Run
# ---------------------------------------------------------------------------
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="render pins + print plan, make no network calls")
    ap.add_argument("--limit", type=int, default=MAX_PINS_PER_RUN)
    args = ap.parse_args()

    # 0. compliance gate
    sys.path.insert(0, SITE)
    import lint_reviews
    probs = lint_reviews.lint_all()
    if probs:
        print("ABORT: compliance lint failed. Fix generate.py first:")
        for x in probs:
            print("  -", x)
        sys.exit(1)
    print("Compliance lint clean.")

    # pick a small, fresh subset (least-recently pinned tracked in state)
    state_file = os.path.join(OUTDIR, "state.json")
    state = {}
    if os.path.isfile(state_file):
        try:
            state = json.load(open(state_file))
        except Exception:
            state = {}
    last = state.get("pinned", {})
    ordered = sorted(generate.PRODUCTS, key=lambda p: last.get(p["name"], 0))
    picks = ordered[:max(1, args.limit)]

    print(f"{'DRY-RUN: ' if args.dry_run else ''}Publishing {len(picks)} pins "
          f"(max/run={args.limit}).")

    board_id = None
    if not args.dry_run:
        if not PIN_TOKEN:
            print("SKIP: no pinterest_token in affiliate.json - not configured yet. "
                  "Add your Business account's OAuth token to enable auto-publish.")
            sys.exit(0)
        board_id = find_board_id()
        if not board_id:
            print("ERROR: could not resolve a board id.")
            sys.exit(1)
        print(f"Board resolved: {board_id}")

    results = []
    for p in picks:
        r = publish_pin(p, board_id, dry_run=args.dry_run)
        results.append(r)
        if not args.dry_run:
            last[p["name"]] = int(time.time())
            time.sleep(8)  # pace: ~1 pin / 8s, never bulk-spam
    if not args.dry_run:
        state["pinned"] = last
        json.dump(state, open(state_file, "w"))

    print(f"Done. {'[dry-run, nothing posted]' if args.dry_run else 'Posted %d pins.' % len(results)}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Emit a Pinterest bulk-upload CSV + publish pin images to the site.

Until the Pinterest app is upgraded to STANDARD access, the daily auto-pin cron
cannot post publicly. This script produces a CSV you can upload manually at
business.pinterest.com -> Ads -> Bulk editor -> Create, choosing the board
"ai.pets.and.companions". Pinterest requires an IMAGE URL (not a local file),
so pin images are rendered to pins/ and that folder is committed/deployed to
GitHub Pages, giving each image a public URL.

Reuses pinterest_publisher.build_caption / render_pin so the CSV matches exactly
what the auto-pinner would post (same title, description, link, FTC disclosure).
"""
import os
import csv
import json
import generate
import pinterest_publisher as pp

SITE = generate.SITE
OUTDIR = pp.OUTDIR
os.makedirs(OUTDIR, exist_ok=True)

# Pinterest bulk-create CSV columns (minimal, required subset). Header names
# are what the bulk editor expects; extra columns are ignored.
CSV_COLS = [
    "Image URL",
    "Board",
    "Title",
    "Description",
    "Link",
    "Alt Text",
]

board = generate.AFF.get("pinterest_board", "ai.pets.and.companions")
csv_path = os.path.join(SITE, "pins", "pinterest_bulk_upload.csv")

rows = []
for p in generate.PRODUCTS:
    title, desc = pp.build_caption(p)
    img_path = pp.render_pin(p)  # renders pins/<slug>.png
    slug = generate.slugify(p["name"])
    img_url = f"{generate.SITE_URL}/pins/{slug}.png"
    link = f"{generate.SITE_URL}/{slug}.html"
    rows.append({
        "Image URL": img_url,
        "Board": board,
        "Title": title,
        "Description": desc,
        "Link": link,
        "Alt Text": f"{p['name']} companion robot review",
    })

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=CSV_COLS)
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} pins to {csv_path}")
print(f"Board: {board}  |  site: {generate.SITE_URL}")
print("Pin images rendered to pins/*.png (deploy via git to make URLs live).")
for r in rows:
    print(f"  {r['Title']}\n    img: {r['Image URL']}\n    link: {r['Link']}")

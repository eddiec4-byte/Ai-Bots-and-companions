#!/usr/bin/env python3
"""Emit a Pinterest bulk-upload CSV using the EXACT schema Pinterest's bulk
editor expects (verified against Pinterest's column spec):

  Title          (required, <=100 chars)
  Media URL      (required, BARE public png/jpeg URL - do NOT use @url: or the
                  organic bulk uploader treats it as a video link and errors)
  Pinterest board(required, board title; created if missing)
  Description    (<=500 chars)
  Link           (bare destination URL - no @url: prefix)
  Publish date   (optional -> publish immediately if blank)
  Keywords       (optional, comma-separated)

Until the Pinterest app is upgraded to STANDARD access, the daily auto-pin cron
cannot post publicly, so this CSV lets you bulk-upload manually. Pin images are
rendered to pins/ and deployed to GitHub Pages (public URLs). Reuses
pinterest_publisher.build_caption / render_pin so copy matches the auto-pinner.
"""
import os
import sys
import csv
import generate
import pinterest_publisher as pp

SITE = generate.SITE
OUTDIR = pp.OUTDIR
os.makedirs(OUTDIR, exist_ok=True)


def validate(rows, board):
    """Fail loudly (exit non-zero) if any pin would break Pinterest's bulk upload.
    Catches the two real failure modes seen in production:
      1. @url: prefix anywhere -> Pinterest reads it as a video link -> pin dies.
      2. non-https (or empty) URL in Media URL / Link -> 'no content extracted'.
    This runs BEFORE the file is written, so a broken CSV is never produced.
    """
    errors = []
    for i, r in enumerate(rows, 1):
        for col in ("Media URL", "Link"):
            val = r.get(col, "")
            if not val:
                errors.append(f"row {i} ({r.get('Title','?')}): {col} is empty")
                continue
            if "@url:" in val:
                errors.append(f"row {i} ({r.get('Title','?')}): {col} contains forbidden '@url:' prefix -> {val}")
            if not val.startswith("https://"):
                errors.append(f"row {i} ({r.get('Title','?')}): {col} is not https -> {val}")
        if not r.get("Pinterest board"):
            errors.append(f"row {i}: Pinterest board is empty")
        elif "." in r["Pinterest board"]:
            errors.append(f"row {i}: Pinterest board '{r['Pinterest board']}' contains '.' (invalid in board title)")
    return errors

# Exact Pinterest bulk-editor columns (order matters to the importer).
CSV_COLS = [
    "Title",
    "Media URL",
    "Pinterest board",
    "Description",
    "Link",
    "Publish date",
    "Keywords",
]

board = generate.AFF.get("pinterest_board", "ai.pets.and.companions")
csv_path = os.path.join(SITE, "pins", "pinterest_bulk_upload.csv")

rows = []
for p in generate.PRODUCTS:
    # Only pin products with a VERIFIED, in-stock Amazon ASIN. Products whose
    # ASIN was removed from affiliate.json (dead / not-listed) are not featured,
    # per the affiliate policy — pinning them would send buyers to a 404.
    if p["name"] not in generate.AMAZON_ASIN:
        continue
    title, desc = pp.build_caption(p)
    img_path = pp.render_pin(p)  # renders pins/<slug>.png
    slug = generate.slugify(p["name"])
    img_url = f"{generate.SITE_URL}/pins/{slug}.png"
    link = f"{generate.SITE_URL}/{slug}.html"
    # Organic bulk uploader: BARE URLs only. @url: prefix makes Pinterest treat
    # Media URL as a video link -> "Video link in URL column isn't formatted properly".
    rows.append({
        "Title": title[:100],
        "Media URL": img_url,
        "Pinterest board": board,
        "Description": desc[:500],
        "Link": link,
        "Publish date": "",            # publish immediately
        "Keywords": f"{p['name']}, {p['maker']}, AI companion, robot pet, review",
    })

# --- SAFETY NET: never emit a CSV Pinterest will reject ---
errors = validate(rows, board)
if errors:
    sys.stderr.write("PIN CSV VALIDATION FAILED — not writing broken file:\n")
    for e in errors:
        sys.stderr.write(f"  - {e}\n")
    sys.exit(1)

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=CSV_COLS)
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} pins to {csv_path}")
print(f"Board (will be created if missing): {board}")
for r in rows:
    print(f"  {r['Title']}  | media: {r['Media URL']}")

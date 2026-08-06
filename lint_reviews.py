#!/usr/bin/env python3
"""Content-safety lint for Companion Intelligence reviews.

Flags deceptive first-person / hands-on claims that could read as fabricated
testimonials. Machine-generated editorial copy is legal and fine; *pretending a
human tested/owned the product* is not (FTC Endorsement Guides + Amazon
Associates policy). check_text() returns a list of violation labels; empty =
clean. lint_all() scans the whole catalog and exits non-zero if anything fails,
so it can gate the nightly build.
"""
import re
import sys

# Patterns implying a real, personal hands-on experience we cannot truthfully
# claim for autonomous editorial copy.
PATTERNS = [
    (r"\bI (tested|tried|owned|own|bought|used|have|got|received|reviewed)\b",
     "first-person hands-on ('I tested/owned/used')"),
    (r"\bI've (tested|tried|owned|used|had|reviewed)\b",
     "first-person perfect ('I've tested/owned')"),
    (r"\bwe (tested|tried|owned|bought|used|reviewed)\b",
     "first-person-plural hands-on ('we tested')"),
    (r"\bmy (cat|dog|kid|child|daughter|son|grandma|grandmother|mother|father|wife|husband|family|home|desk|pet|partner)\b",
     "possessive firsthand ('my cat/kid/home')"),
    (r"\bour (hands-on|testing|lab|review)\b",
     "possessive firsthand ('our testing')"),
    (r"\bafter (using|testing|living with|owning|spending)\b",
     "implies personal use ('after using')"),
    (r"\bspent (a|two|three|several|few) (week|weeks|month|months|day|days)\b",
     "claims a test duration"),
    (r"\bwhen (it|he|she) (arrived|shipped|showed up|came)\b",
     "implies receipt of product"),
]


def check_text(text):
    if not text:
        return []
    hits = []
    for pat, label in PATTERNS:
        if re.search(pat, text, re.I):
            hits.append(label)
    return hits


def lint_all():
    import generate
    problems = []

    def scan(label, text):
        for x in check_text(text or ""):
            problems.append(f"{label}: {x}")

    for p in generate.PRODUCTS:
        scan(f"PRODUCT {p['name']} review", p.get("review", ""))
        scan(f"PRODUCT {p['name']} blurb", p.get("blurb", ""))
        for pr in p.get("pros", []):
            scan(f"PRODUCT {p['name']} pro", pr)
        for c in p.get("cons", []):
            scan(f"PRODUCT {p['name']} con", c)
    for c in generate.COMPARES:
        scan(f"COMPARE {c['slug']} intro", c.get("intro", ""))
    for t in generate.LONGTAIL:
        scan(f"LONGTAIL {t['slug']} intro", t.get("intro", ""))
        for q, a in t.get("faqs", []):
            scan(f"LONGTAIL {t['slug']} faq", a)
    return problems


if __name__ == "__main__":
    probs = lint_all()
    if probs:
        print("COMPLIANCE LINT FAILED - deceptive first-person claims found:")
        for x in probs:
            print("  -", x)
        sys.exit(1)
    print("COMPLIANCE LINT CLEAN: no deceptive first-person claims.")
    sys.exit(0)

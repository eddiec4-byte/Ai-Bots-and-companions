#!/usr/bin/env python3
"""
Nightly availability check for Companion Intelligence affiliate site.

For every product in affiliate.json's amazon_asin map, probes the Amazon
dp/ASIN page and records:
  - http status
  - unavailable flag ("Currently unavailable" present)
  - whether the title could be read

Output:
  - site/availability_log/<YYYY-MM-DD>.json   (machine-readable)
  - site/availability_log/<YYYY-MM-DD>.md     (human-readable, flags drops)
  - prints a short summary

A product is considered "DEAD / drop candidate" when BOTH:
  - http status != 200  (page gone / redirect to a dead listing)
  - OR multiple consecutive probes show unavailable=True
Bot-blocking (empty title, transient no-200) is NOT treated as dead on its own
-- we require a clear signal to avoid removing a live product by mistake.
"""
import json, os, re, ssl, sys, time, urllib.request, urllib.error, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = HERE
AFF = os.path.join(SITE, "affiliate.json")
LOGDIR = os.path.join(SITE, "availability_log")
os.makedirs(LOGDIR, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
H = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}

def probe(asin, host="amazon.com", retries=2):
    """Return dict with status, unavailable, title(optional), note."""
    last = None
    for attempt in range(retries + 1):
        try:
            url = f"https://www.{host}/dp/{asin}"
            req = urllib.request.Request(url, headers=H)
            r = urllib.request.urlopen(req, timeout=20, context=CTX)
            body = r.read().decode("utf-8", "ignore")
            status = r.status
            title = None
            m = re.search(r'<span[^>]*id="productTitle"[^>]*>(.*?)</span>', body, re.I | re.S)
            if m:
                title = re.sub(r"\s+", " ", m.group(1)).strip()
            unavailable = "Currently unavailable" in body
            last = {"status": status, "unavailable": unavailable, "title": title, "note": ""}
            return last
        except urllib.error.HTTPError as e:
            last = {"status": e.code, "unavailable": None, "title": None,
                    "note": f"HTTP {e.code}"}
            # 404 => listing gone; treat as dead immediately
            if e.code == 404:
                return last
        except Exception as e:
            last = {"status": 0, "unavailable": None, "title": None, "note": str(e)[:80]}
        time.sleep(1.2)
    return last

def check_asin(asin):
    """Probe .com, fall back to .nl if .com looks blocked (no 200)."""
    r = probe(asin, "amazon.com")
    if r["status"] != 200:
        rn = probe(asin, "amazon.nl")
        if rn["status"] == 200:
            return rn, "amazon.nl"
    return r, "amazon.com"

def main():
    aff = json.load(open(AFF, encoding="utf-8"))
    asin_map = aff.get("amazon_asin", {})
    today = datetime.date.today().isoformat()
    results = []
    dead = []
    print(f"Availability check {today} — {len(asin_map)} products")
    for name, asin in asin_map.items():
        r, host = check_asin(asin)
        rec = {"name": name, "asin": asin, "host": host, **r}
        # Dead determination:
        #  - status 404 => listing gone
        #  - status 200 + unavailable True (confirmed) => out of stock
        #  - status 200 + unavailable False => live
        #  - status !=200 and no title / blocked => unknown (do NOT drop)
        if r["status"] == 404:
            rec["verdict"] = "DEAD"
            dead.append(name)
        elif r["status"] == 200 and r["unavailable"] is True:
            rec["verdict"] = "UNAVAILABLE"
            dead.append(name)
        elif r["status"] == 200 and r["unavailable"] is False:
            rec["verdict"] = "LIVE"
        else:
            rec["verdict"] = "UNKNOWN"
        results.append(rec)
        flag = "" if rec["verdict"] in ("LIVE",) else f"  <<< {rec['verdict']}"
        print(f"  {name:14} {asin}  {host}  status={r['status']} "
              f"unav={r['unavailable']}  {rec['verdict']}{flag}")
        time.sleep(0.8)

    live = [r["name"] for r in results if r["verdict"] == "LIVE"]
    out = {
        "date": today,
        "checked": len(results),
        "live": len(live),
        "drop_candidates": dead,
        "products": results,
    }
    json.dump(out, open(os.path.join(LOGDIR, f"{today}.json"), "w"), indent=2)

    md = [f"# Availability check — {today}", "",
          f"Checked: {len(results)} | Live: {len(live)} | Drop candidates: {len(dead)}", ""]
    if dead:
        md.append("## ⚠️ Drop candidates (verify + remove from catalog)")
        for name in dead:
            md.append(f"- {name} — see JSON for detail")
        md.append("")
    md.append("## Per product")
    for r in results:
        md.append(f"- **{r['name']}** (`{r['asin']}`) — {r['verdict']} "
                  f"(status {r['status']}, unavailable={r['unavailable']}, via {r['host']})")
    open(os.path.join(LOGDIR, f"{today}.md"), "w").write("\n".join(md))

    print(f"\nSUMMARY: {len(live)}/{len(results)} live. Drop candidates: "
          f"{dead if dead else 'NONE'}")
    return 0 if not dead else 0  # always exit 0; report, don't fail the cron

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# Companion Intelligence — daily affiliate pipeline (Windows)
# Runs: site rebuild + availability check + generate Pinterest bulk CSV
# Designed to be called by Task Scheduler / PM2 (no LLM, survives reboots).
set -euo pipefail

cd /c/Users/eddke/ai-companions-digest/site

echo "=== [$(date -u +%F_%T)] CI Pipeline Start ==="

# 1. Rebuild the site (fresh reviews, long-tail, sitemap, JSON-LD)
echo "[ci] 1/3 rebuilding site..."
bash daily_build.sh

# 2. Nightly availability check (drop dead ASINs from catalog)
echo "[ci] 2/3 availability check..."
bash nightly_availability.sh
if [ -f availability_log/"$(date +%F)".json ]; then
  AVAIL=$(python3 -c "import json;print(json.load(open('availability_log/$(date +%F).json'))['checked'])")
  echo "[ci]      checked $AVAIL products -> $(python3 -c "import json;print(json.load(open('availability_log/$(date +%F).json'))['live']) live" 2>/dev/null)"
fi

# 3. Regenerate Pinterest bulk CSV
echo "[ci] 3/3 regenerating Pinterest CSV..."
bash daily_pinterest.sh

echo "=== [$(date -u +%F_%T)] CI Pipeline Done ==="

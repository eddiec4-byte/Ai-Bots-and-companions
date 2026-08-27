#!/usr/bin/env bash
# Durable daily site build — runs WITHOUT the agent/LLM so it survives auth-token expiry.
set -e
cd /c/Users/eddke/ai-companions-digest/site
python generate.py
# Regenerate the Pinterest bulk CSV; pins_csv.py validates URLs and exits 1 if
# any pin would break Pinterest (e.g. @url: prefix, non-https link). set -e
# means a bad CSV aborts the whole build instead of deploying a broken file.
python pins_csv.py
git add -A
if git diff --cached --quiet; then
  echo "Daily build: no content changes."
else
  git commit -m "daily autonomous build $(date +%F)"
  git push
  echo "Daily build: rebuilt + pushed to GitHub Pages."
fi
echo "SITE BUILD OK"

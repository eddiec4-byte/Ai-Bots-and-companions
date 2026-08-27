#!/usr/bin/env bash
# Durable daily site build — runs WITHOUT the agent/LLM so it survives auth-token expiry.
cd /c/Users/eddke/ai-companions-digest/site
python generate.py
git add -A
if git diff --cached --quiet; then
  echo "Daily build: no content changes."
else
  git commit -m "daily autonomous build $(date +%F)"
  git push
  echo "Daily build: rebuilt + pushed to GitHub Pages."
fi
echo "SITE BUILD OK"

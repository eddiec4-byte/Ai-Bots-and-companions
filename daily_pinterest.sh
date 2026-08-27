#!/usr/bin/env bash
# Daily Pinterest auto-pin — no_agent. Needs secrets.pinterest.json (one-time OAuth).
cd /c/Users/eddke/ai-companions-digest/site
if [ ! -f secrets.pinterest.json ]; then
  echo "PINTEREST DISABLED: secrets.pinterest.json missing. Run: python pinterest_oauth.py (localhost:8080 consent) once to enable auto-pins."
  exit 0
fi
python pinterest_publisher.py

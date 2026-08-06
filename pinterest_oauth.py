#!/usr/bin/env python3
"""Local Pinterest OAuth helper for Companion Intelligence.

Walks you through generating a USER access token (the one pinterest_publisher.py
needs) without manual curl. Pure stdlib - no pip installs.

Flow (Pinterest v5 OAuth 2, authorization_code grant):
  1. Open this app's "Connect app" page in your browser to get a client_id + secret.
  2. Put those in secrets.pinterest.json (git-ignored - NEVER committed).
  3. Run this script. It opens Pinterest's consent screen, catches the redirect
     on localhost:8080, exchanges the code for an access token, and saves it to
     secrets.pinterest.json (and a refresh token).

IMPORTANT: A token minted under TRIAL access only creates sandbox pins that are
invisible to the public. To publish real, public pins you must upgrade the app to
STANDARD access in the developer portal (submit a short video of the OAuth flow).

Redirect URI to register in the app: http://localhost:8080/
Scopes requested: boards:read pins:write pins:read
"""
import os
import re
import sys
import json
import time
import base64
import random
import string
import webbrowser
import urllib.parse
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

SITE = os.path.dirname(os.path.abspath(__file__))
SECRETS = os.path.join(SITE, "secrets.pinterest.json")
REDIRECT = "http://localhost:8080/"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
AUTH_URL = "https://www.pinterest.com/oauth/"
SCOPES = "boards:read,pins:write,pins:read"

_state = None
_code = None


def load_secrets():
    if os.path.isfile(SECRETS):
        try:
            return json.load(open(SECRETS))
        except Exception:
            return {}
    return {}


def save_secrets(d):
    json.dump(d, open(SECRETS, "w"), indent=2)
    print(f"Saved secrets to {SECRETS} (git-ignored - keep it local).")


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):

        global _code
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        if "code" in params:
            _code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Companion Intelligence</h2><p>Pinterest auth OK - you can close this tab.</p>")
        else:
            self.send_response(400)
            self.end_headers()
        self.server.shutdown()

    def log_message(self, *a):
        pass


def exchange(code, client_id, client_secret):
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=data,
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        print("TOKEN EXCHANGE FAILED:", e.code, e.read().decode("utf-8", "ignore")[:400])
        return None


def main():
    s = load_secrets()
    if not s.get("client_id") or not s.get("client_secret"):
        print("\nMissing client_id/client_secret.")
        print("1. Go to https://developers.pinterest.com/apps/ , open your app, copy App ID and App secret.")
        print(f"2. Register redirect URI exactly: {REDIRECT}")
        print("3. Put them in secrets.pinterest.json like:")
        print('   {"client_id": "YOUR_ID", "client_secret": "YOUR_SECRET"}')
        sys.exit(1)

    state = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    auth = (AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": s["client_id"],
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    }))
    print("\nOpening Pinterest consent screen...\n")
    print("If the browser doesn't open, visit this URL manually:")
    print(" ", auth, "\n")
    webbrowser.open(auth)

    server = HTTPServer(("127.0.0.1", 8080), _Handler)
    print("Waiting for Pinterest to redirect back (localhost:8080)... approve in the browser.")
    server.serve_forever()

    if not _code:
        print("No authorization code received. Aborting.")
        sys.exit(1)
    print("Got authorization code. Exchanging for token...")
    tok = exchange(_code, s["client_id"], s["client_secret"])
    if not tok or "access_token" not in tok:
        print("Exchange returned no access_token. Check the app's approved scopes/access tier.")
        sys.exit(1)
    s["pinterest_token"] = tok["access_token"]
    if tok.get("refresh_token"):
        s["refresh_token"] = tok["refresh_token"]
    save_secrets(s)
    print("\nACCESS TOKEN ACQUIRED. pinterest_publisher.py will now auto-publish.")
    print("Reminder: under TRIAL access pins are sandbox-only (invisible).")
    print("Upgrade to STANDARD access in the developer portal for public pins.")


if __name__ == "__main__":
    main()

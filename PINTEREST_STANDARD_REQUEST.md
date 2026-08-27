# Pinterest Developer App — STANDARD Access Request (draft)

Copy the sections below into the Pinterest Developer Portal app-review form.
App: Companion Intelligence (AI pets & companions affiliate publisher)
Board used: `ai.pets.and.companions`
Scopes requested: `boards:read`, `pins:write`, `pins:read`
Site: https://eddiec4-byte.github.io/Ai-Bots-and-companions

---

## 1. App description
Companion Intelligence is an autonomous content-publishing app for the niche of
AI pets, robot companions, and social/elder/child companion devices. It renders
ORIGINAL pin graphics (emoji + product name + editorial blurb — no scraped brand
photos) and posts them to a single curated board (`ai.pets.and.companions`) that
links back to our own affiliate review pages. Every pin carries an FTC-compliant
disclosure ("#ad" + "As an Amazon Associate I earn from qualifying purchases").

## 2. How users authenticate
The app uses OAuth 2.0 (authorization_code grant) with the redirect URI
`http://localhost:8080/`. A local helper script opens Pinterest's consent screen,
catches the redirect on localhost, exchanges the code for an access token, and
stores it locally. No end-user credentials are collected by us; only the app
owner's own Pinterest account is authorized.

## 3. Use case / data accessed
- `boards:read` — to resolve the target board ID by name at publish time.
- `pins:write` — to create pins (max 3 per day, paced, never bulk-spammed).
- `pins:read` — to confirm a pin was created and avoid duplicates.
We only create pins; we do not read, modify, or delete user content, and we do
not access analytics beyond what the publish confirmation returns.

## 4. Why STANDARD access is needed
Under TRIAL access, pins are created in the sandbox and are invisible to the
public, so the board drives no referral traffic. STANDARD access is required for
the pins to appear publicly on the `ai.pets.and.companions` board and function as
intended (organic referral traffic to our review pages).

## 5. Demo video shot list (record ~60–90s, show the real flow)
1. Open the app's local helper (`pinterest_oauth.py`) → Pinterest consent screen
   appears with scopes `boards:read, pins:write, pins:read`.
2. Approve in the browser → redirect to `http://localhost:8080/` ("auth OK").
3. Show the access token saved locally (redacted) in `secrets.pinterest.json`.
4. Run `python pinterest_publisher.py --dry-run` → an ORIGINAL pin image renders
   with the "#ad" disclosure stamped on it; caption + link shown (no brand photo).
5. Show the publish call hitting `POST /v5/pins` and the returned pin object.

---

## Notes / gotchas
- Submit the video from the SAME developer account that owns the app.
- Approved scopes must exactly match what the app requests (no extras).
- Review can take several business days; you'll get an email on decision.
- After approval, re-run the daily pin cron (`b09a517701f8`) — it will post
  publicly. Until then it stays in the safe "PINTEREST DISABLED" notice state.

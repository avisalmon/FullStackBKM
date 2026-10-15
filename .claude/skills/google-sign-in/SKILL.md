---
name: google-sign-in
description: >
  Add "Continue with Google" sign-in (plus the existing email and password sign-in) to the site: Google Cloud project,
  OAuth consent screen, OAuth client, redirect URIs, moving the keys to Render, testing, and fixing
  redirect_uri_mismatch. Claude automates configuration and tests; the owner does the Google console clicks. TRIGGER:
  "google login", "sign in with google", "google sso", "oauth", "social login", "redirect_uri_mismatch", "continue
  with google", "allauth".
---

# Google sign-in

Source of truth: [docs/procedures/auth_google_oauth.md](../../../docs/procedures/auth_google_oauth.md). Re-read it before starting.

Email + password already works (django-allauth). Google appears automatically once `GOOGLE_CLIENT_ID` **and** `GOOGLE_CLIENT_SECRET` are set.

## Who does what

**The owner (Google console, about 10 minutes):** create a project, configure the OAuth consent screen (External; publish it so anyone can sign in), create a
**Web application** OAuth client, add every redirect URI `https://<host>/accounts/google/login/callback/` (local `http://127.0.0.1:8000/...`, the onrender.com host, and the custom domain),
then put the Client ID and secret in the git-ignored `.env`. Give exact menu names and wait after each step. **Never ask for the secret in chat.**

**You:** copy both values to Render without showing them (`python scripts/render_api.py env-set GOOGLE_CLIENT_ID --from-env GOOGLE_CLIENT_ID`, same for the secret), wait for the redeploy,
check `https://<host>/` shows "Continue with Google" and that `/accounts/google/login/` redirects towards accounts.google.com. Make sure the Site record carries the real host
(`bootstrap_site` does it from `SITE_DOMAIN` or the Render hostname). Run `python scripts/verify_site.py --url https://<host>`.

## Behaviour to explain to the owner (it is a feature)

A brand-new person: instant sign-in, account created. Someone who already has a password account with the same email: a one-time "connect these accounts" form, then seamless. That form prevents account takeover.

## Troubleshooting

`redirect_uri_mismatch` -> the exact callback URL is missing from the OAuth client (gotcha #18). No button -> one of the two variables is empty on that environment. Redirect loop -> `LOGIN_REDIRECT_URL`, `SITE_DOMAIN`.
Privacy: request only the `profile` and `email` scopes; name Google in the privacy policy (the generated page does when sign-in is on).

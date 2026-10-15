# Sign-in: email + password, and Google

Both work out of the box through django-allauth. Email + password needs nothing. "Continue with
Google" appears automatically once `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set.

```
visitor -> /accounts/login/ -> password form        -> session
                            -> Google -> callback   -> session (account auto-created)
```

## Google setup (humans: ~10 minutes, one time)

You need a Google account. Claude can't click through Google's console for you, so do this and
then hand the two values over **via `.env` / Render, not by pasting them into chat**.

1. https://console.cloud.google.com -> create a project (e.g. "my-site").
2. **APIs & Services -> OAuth consent screen**: user type **External**; app name, support email,
   developer email. Add your own email as a test user while it is in "Testing".
   To let anyone sign in, click **Publish app** (basic scopes `profile` + `email` need no review).
3. **Credentials -> Create credentials -> OAuth client ID -> Web application**.
4. **Authorized redirect URIs** (add every host you use):
   * `http://127.0.0.1:8000/accounts/google/login/callback/` (local)
   * `https://<service>.onrender.com/accounts/google/login/callback/`
   * `https://<your-domain>/accounts/google/login/callback/` (when you have one; gotcha #18)
5. Copy the **Client ID** and **Client secret**.
6. Put them in your local `.env` as `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`, and on Render
   (Environment tab, or `render_api.py env-set --from-env`). Render redeploys.
7. The Site record (`/admin/sites/site/`) must carry the real hostname. `bootstrap_site` does this
   on every boot from `SITE_DOMAIN` or the Render hostname, so there is nothing to click.

Locally the Site record is `example.com` until you run `python manage.py bootstrap_site` with
`SITE_DOMAIN=127.0.0.1:8000` (put it in `.env`). Do that once if Google login redirects oddly.

## Behaviour (proven)

* New person, never signed up: Google -> instant login, account created, no form.
* Existing password account with the same email: a one-time "connect this account" form, then
  seamless forever. That is deliberate (it stops account takeover), not a bug (gotcha #11).

## Settings that matter (all in `mysite/settings.py`)

```python
ACCOUNT_LOGIN_METHODS = {"email"}  # allauth 65.x syntax
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"  # raise to "mandatory" once email is verified/working
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False  # don't mail strangers (it burned a mail quota once)
SOCIALACCOUNT_LOGIN_ON_GET = True  # skip the "Continue with Google?" page
```

Turn on `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` for an open-to-the-world site once Resend works.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `redirect_uri_mismatch` | The exact callback URL is missing from the OAuth client (step 4) |
| No Google button | One of the two env vars is empty on that environment |
| "Social account already exists" | They already have an account with that email; they just log in |
| Redirect loop after login | `LOGIN_REDIRECT_URL = "/"` in settings; check `SITE_DOMAIN` / Site record |
| Password-reset email never arrives | [email_resend.md](email_resend.md) |

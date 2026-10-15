# Email: Resend through django-anymail

```
Django (send_mail / allauth) -> django-anymail -> Resend API -> recipient
```

No `RESEND_API_KEY` -> email is printed to the console (the right behaviour for local development
and tests). With it -> real mail. Nothing else to configure in code.

## Setup (humans)

1. Account at https://resend.com (free tier is enough to start).
2. **Domains -> Add domain** (your own domain, e.g. `your-domain.com`). Resend shows DNS records.
3. Add them at wherever your DNS lives (registrar or Cloudflare, [custom_domain_dns.md](custom_domain_dns.md)):
   * DKIM: a `resend._domainkey` CNAME/TXT (value supplied by Resend)
   * SPF: TXT on the root, e.g. `v=spf1 include:amazonses.com ~all` (use exactly what Resend shows)
   * DMARC: TXT on `_dmarc`, e.g. `v=DMARC1; p=none;`
   For Cloudflare, set the DKIM record to **DNS only** (grey cloud), not proxied.
4. Wait until all show **Verified** in Resend.
5. **API Keys -> Create** (permission "Sending access" is enough). Copy it once.
6. Set `RESEND_API_KEY` and `DEFAULT_FROM_EMAIL=noreply@your-domain.com` in local `.env` and on Render.
   Set `OWNER_EMAIL` to your real inbox to receive error and cost alerts.

## Test

```powershell
.\env\Scripts\python.exe manage.py shell -c "from django.core.mail import send_mail; print(send_mail('Test', 'Hello', None, ['you@example.com']))"
```
Prints `1` on success. Check the Resend dashboard -> Logs if nothing arrives.

## Lessons from the reference site

* **Do not mail addresses you have no account for.** allauth's enumeration guard otherwise answers
  every login/reset attempt with an "unknown account" email, so a bot posting random addresses made
  the site mail strangers on demand and burned the whole daily quota (about 700 emails in a week).
  `ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False` is already set here.
* Cap sends per recipient per day and log what you send, if mail volume ever matters. The
  reference site wraps the backend in a small "guard" for this (see backlog).
* Free tiers have daily limits; a send-loop shows up as quota exhaustion.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Nothing arrives | Key set on *that* environment? Resend dashboard -> Logs |
| `AnymailRequestsAPIError` | Bad key, or `DEFAULT_FROM_EMAIL` is on an unverified domain |
| Goes to spam | SPF, DKIM and DMARC must all pass; new domains need warming up |

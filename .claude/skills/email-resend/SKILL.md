---
name: email-resend
description: >
  Set up real transactional email (password resets, alerts, notifications) with Resend: account, domain verification
  (SPF, DKIM, DMARC), API key, sender address, owner alert address, testing, and deliverability fixes. Without a key,
  email prints to the console. TRIGGER: "email", "send email", "resend", "smtp", "password reset email", "emails not
  arriving", "spam folder", "dkim", "spf", "dmarc", "sender address", "notifications by email".
---

# Email with Resend

Source of truth: [docs/procedures/email_resend.md](../../../docs/procedures/email_resend.md). Re-read it first.

No `RESEND_API_KEY` -> email is printed to the console (right for local work and tests). With it -> real mail through django-anymail. No code change needed.

## Who does what

**The owner:** create a Resend account, add their domain, add the DNS records Resend shows at their registrar/Cloudflare (DKIM, SPF, DMARC; Cloudflare DKIM record must be **DNS only**), wait for **Verified**, create a
sending API key, put it in `.env`. A domain is required for good deliverability: if they don't have one yet, finish [custom-domain](../custom-domain/SKILL.md) first.

**You:** set `RESEND_API_KEY`, `DEFAULT_FROM_EMAIL=noreply@<domain>` and `OWNER_EMAIL` on Render (`render_api.py env-set ... --from-env`), then send a test from the live service
(`render_api.py job --command "python manage.py shell -c ..."` or ask the owner to use "forgot password") and confirm it arrived and did not land in spam.
Consider `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` once mail works and the site is public.

## Rules learned the hard way

* Never mail addresses you have no account for (`ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False`): a bot posting random addresses once burned a whole daily quota.
* Don't put secrets or sensitive personal data in email bodies. Name Resend in the privacy policy (the generated page does when a key is set).
* A failing alert email must never break a request.

## Troubleshooting

Nothing arrives -> key set on *that* environment? Resend dashboard -> Logs. `AnymailRequestsAPIError` -> bad key or unverified sender domain. Spam -> SPF, DKIM, DMARC must all pass; new domains need warming.

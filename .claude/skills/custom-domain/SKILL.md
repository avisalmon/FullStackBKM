---
name: custom-domain
description: >
  Attach the owner's own domain name to the Render site with HTTPS: choose a registrar, add custom domains in Render,
  DNS records (A and CNAME), ALLOWED_HOSTS and SITE_DOMAIN, Google OAuth and Resend follow-ups, Cloudflare option, and
  diagnosing DNS, SSL and redirect problems. TRIGGER: "domain", "dns", "custom domain", "buy a domain", "www", "https
  certificate", "ssl", "cloudflare", "nameservers", "my site address", "400 bad request on my domain".
---

# Custom domain

Source of truth: [docs/procedures/custom_domain_dns.md](../../../docs/procedures/custom_domain_dns.md). Re-read it first. Do this only after the site works on its `*.onrender.com` address.

## Who does what

**The owner:** buy the domain (any registrar with an A/CNAME/TXT DNS panel, or move DNS to free Cloudflare) and add the DNS records **exactly as Render shows them** (the root A-record IP can change; enter just `www`, not `www.example.com`,
because registrar forms append the domain). Some country domains take up to 72 hours.

**You:**
1. Add both `example.com` and `www.example.com` in Render (`python scripts/render_api.py domain --name ...`, or dashboard -> Settings -> Custom Domains) and read back the records Render wants.
2. Set `ALLOWED_HOSTS=<service>.onrender.com,example.com,www.example.com` and `SITE_DOMAIN=example.com` (CSRF origins derive from `ALLOWED_HOSTS`). Remember these are dashboard values: editing `render.yaml` will not change them (gotcha #8).
3. Follow-ups: add the new callback URL to the Google OAuth client ([google-sign-in](../google-sign-in/SKILL.md)); verify the domain in Resend ([email-resend](../email-resend/SKILL.md)); `gh variable set SITE_URL --body https://example.com`; update `DOMAIN_YEARLY_USD` for the cost report.
4. Verify: `python scripts/verify_site.py --url https://example.com` (HTTPS redirect, HSTS, cookie flags) and `curl -sI`.

## Troubleshooting

No resolution -> records match Render exactly? SSL error -> wait for the certificate; with Cloudflare use **Full (strict)**. Too many redirects -> Cloudflare mode must not be Flexible. 400 on the new domain -> missing from `ALLOWED_HOSTS`. `redirect_uri_mismatch` -> gotcha #18.
Cost: ~$10-15/year; record it. Privacy: the domain registration can expose the owner's contact details unless WHOIS privacy is on; recommend turning it on.

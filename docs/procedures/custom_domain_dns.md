# Your own domain name

Do this *after* the site works on its `*.onrender.com` address.

## 1. Buy a domain (human)

Any registrar works (Namecheap, Porkbun, Cloudflare Registrar, GoDaddy, a local registrar for a
country domain). Typical cost $10-15/year; record it in `DOMAIN_YEARLY_USD` for the cost report.
Pick a registrar whose DNS panel lets you add A, CNAME and TXT records, or move DNS to Cloudflare (free).

## 2. Tell Render

Render -> your service -> **Settings -> Custom Domains** -> add both `your-domain.com` and
`www.your-domain.com`. (Or `render_api.py domain --service srv-... --name your-domain.com`.)
Render shows the exact DNS records it wants; **use those values, not the examples below**
(the root A-record IP in particular).

## 3. DNS records (human, at your registrar / Cloudflare)

| Name | Type | Value |
|---|---|---|
| `@` (root) | A | the IP Render shows (it was `216.24.57.1` when this was written) |
| `www` | CNAME | `<service>.onrender.com` |

Registrar forms often append your domain to the host: enter `www`, not `www.your-domain.com` (gotcha #16).
Render issues the HTTPS certificate (Let's Encrypt) once DNS resolves; allow minutes to hours.
Some country domains take up to 72 hours (gotcha #19).

## 4. Tell the app (this part is automatable)

On Render -> Environment (or `render_api.py env-set`):

```
ALLOWED_HOSTS = <service>.onrender.com,your-domain.com,www.your-domain.com
SITE_DOMAIN   = your-domain.com
```

CSRF origins derive from `ALLOWED_HOSTS`; `bootstrap_site` updates the Site record on the redeploy.
Remember: these were set in the dashboard, so editing `render.yaml` will not change them (gotcha #8).

## 5. Tell Google and Resend

* Google OAuth client: add `https://your-domain.com/accounts/google/login/callback/` (gotcha #18).
* Resend: verify the domain ([email_resend.md](email_resend.md)).
* GitHub variable for the scheduled jobs: `gh variable set SITE_URL --body https://your-domain.com`.

## Optional: Cloudflare for DNS

Free, fast propagation, full control over record types (the reference site moved there because
its registrar's DNS panel could not set what email authentication needs). Set SSL/TLS mode to
**Full (strict)**; "Flexible" causes redirect loops. Email-auth records must be DNS-only (grey cloud).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Site does not resolve | Records match what Render shows? Nameservers point where you edit DNS? |
| SSL error | Cloudflare mode Full (strict); wait for Render's certificate |
| "Too many redirects" | Cloudflare SSL mode must not be Flexible |
| 400 Bad Request on the new domain | Domain missing from `ALLOWED_HOSTS` |
| Google `redirect_uri_mismatch` | Gotcha #18 |

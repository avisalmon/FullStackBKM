# Privacy: an advisor's guide for your site

> **Not legal advice.** This is practical guidance from people who have built and run a real site, including one used by
> teenagers. Laws differ by country and change. For anything high-stakes (children's data, health, payments, schools, a company)
> talk to a qualified lawyer in your jurisdiction.

## How this guide works: advice, not rules

Claude acts as your **privacy advisor** while it builds. That means:

* It **raises** privacy questions at the moments they matter (the interview, the data model, before launch), explains *why*, and says how
  serious it thinks each one is: **must** (probably unlawful or harmful if skipped), **should** (strong good practice), **could** (nice to have).
* **You decide.** If you choose differently, Claude respects that, helps you do it as safely as it can, and writes your decision and reason in
  [privacy_decisions.md](privacy_decisions.md) so future-you (and anyone who inherits the site) knows it was deliberate. Claude will not nag you twice
  about a decision you have recorded; it will raise it again at launch and when the situation changes.
* **Two honest limits.** Claude will say plainly when something is likely to break the law or put young people at risk, and why. And it will not
  help hide data collection from the people it concerns. Everything else is your call.

The shortest version of the whole guide: **collect less, keep it shorter, tell people the truth, let them take it back, and protect what you hold.**

---

## 1. HTTPS and the safe defaults you already have

| What | Why it matters | State in this blueprint |
|---|---|---|
| **HTTPS everywhere** | Without it, anyone on the same Wi-Fi can read or alter what visitors send, including passwords | Render issues the certificate; `http://` redirects to `https://`; HSTS tells browsers to never try plain http |
| **Secure cookies** | A cookie without `Secure` can leak over http | `Secure` on session and CSRF cookies whenever `DEBUG=False` |
| **HttpOnly + SameSite=Lax cookies** | Stops scripts and other websites reading or riding your visitors' sessions | On by default |
| **Hashed passwords** | A database leak must not reveal passwords | Django hashes with PBKDF2; you can't read them, and neither can attackers cheaply |
| **Short-ish sessions** | Shared computers (libraries, schools) | 14 days (`SESSION_COOKIE_AGE`); shorten for sensitive sites |
| **Browser feature lock** | Camera, microphone, location are off unless you turn them on | `Permissions-Policy` header |
| **No leaking referrers** | Other sites shouldn't learn which of your pages sent a visitor | `Referrer-Policy: same-origin` |
| **Secrets out of git, private repo** | Credentials are personal data's front door | See [security.md](security.md) |

Things that can still weaken it, which Claude will watch for: **mixed content** (an `http://` image on an https page), **third-party scripts**
(everything you embed can see your visitors), and **turning `DEBUG` on in production**. `verify_site.py` checks the first two kinds of problem it can see.

**Turn on two-factor authentication for every admin account** (yours, GitHub, Render, Google). A stolen admin login is a data breach.

---

## 2. Cookies: what you set, and when you need a banner

This site sets only **strictly necessary** cookies: `sessionid` (keeps you signed in) and `csrftoken` (blocks forged form posts). In the EU/UK (the "ePrivacy"
rules) and many other places those need **no consent banner**; non-essential cookies (analytics, advertising, social embeds) **do** need prior, freely given consent.

Practical advice, from safest to riskiest:

1. **Stay cookie-light.** No tracking, no ads, no social-media widgets. Then a banner is unnecessary, and your pages are faster and calmer. *(Recommended: it's the default.)*
2. **Analytics:** if you want visitor counts, use a cookieless tool (Plausible, as wired in via `PLAUSIBLE_DOMAIN`). It still counts as a third party; name it in your policy.
   Google Analytics and similar set cookies and need consent in the EU/UK.
3. **Embeds are trackers.** A YouTube video, a Google Map, a Facebook button, even Google Fonts (visitors' IP addresses go to Google) load third-party code. Prefer
   links, self-hosted fonts (this site uses system fonts) or privacy-enhanced modes (`youtube-nocookie.com`), and update the policy if you add any.
4. If you do add non-essential cookies: show a banner with **equal-weight "Accept" and "Reject"**, load nothing until accepted, remember the choice, let people change it later.

The generated [/privacy/ page](../templates/core/privacy.html) lists the cookies actually set and the third parties actually switched on. **Keep it true:**
if you add a service, add it to the page (the page builds its list from settings; add new services to `third_parties()` in `core/views.py`).

---

## 3. Collect less (data minimisation)

Every field you collect is something you must protect, explain, export and delete. Before adding a field ask: **what will I do with this, and could I do it without?**

| Instead of | Consider |
|---|---|
| Full date of birth | Birth **year** (or just "over 13/16/18" yes/no) |
| Home address | Town or country, or nothing |
| Real name | A chosen display name |
| Phone number "just in case" | Nothing, until a feature truly needs it |
| Government ID numbers | Never. Almost no website needs them |
| Free-text "tell us about yourself" | A fixed list of options |
| Precise location | None, or city level |
| Photos of people | Avatars/illustrations, or photos only with clear consent |

During every data model, Claude asks you to classify each field (section 9 below). This is the single most effective privacy habit: the data you never collected can never leak.

---

## 4. Young people and students

If any of your users could be under 18, *this section changes your design.* Rules vary, but the common shape:

* **Under 13 (US COPPA and similar):** verifiable parental consent *before* collecting personal information, and a strict limit on what you may collect. Many sites simply
  decide **not to allow under-13s**.
* **13 to 15/16 (EU GDPR "digital consent age", set by each country between 13 and 16):** below your country's age, a parent or guardian must consent.
* **Under 18 generally:** extra duty of care, and in many places contracts with minors need guardian involvement. Schools add their own rules (in the US, FERPA covers
  education records; elsewhere, school or ministry policies, and a school may need to be the party that signs).
* **Israel:** the Privacy Protection Law applies and was significantly amended recently; handling minors' data calls for particular care and, in practice, guardian consent.
  Check current requirements with a local lawyer before launching to under-18s.

**Our advice for sites with young users (all "should", most are "must" in some jurisdictions):**

1. **Decide the minimum age** and enforce it with the birth year you collect. Record the decision.
2. **Guardian consent as infrastructure from day one.** Use the `ConsentRecord` model (`kind="guardian"`, `source="guardian"`, `recorded_by` = the teacher or admin who entered it).
   Keep the gate switchable (an environment variable), as the reference site did while it was being built: the *records* and forms exist and work, and turning the *requirement*
   on later is a config change, not a rewrite. Test that the infrastructure survives being switched off.
3. **Private by default.** No public profiles, no real names or photos or school names visible to others, no precise location, no direct messages with strangers.
4. **Adult moderation** for anything one young person can show another (comments, uploads, chat), and a way to report.
5. **No advertising, no behavioural analytics, no third-party trackers.** Ever, for minors.
6. **Be careful with AI.** Don't send a minor's personal details to an AI provider; consider disabling free-form AI for under-18s, or filtering input and output.
7. **Uploads by minors are private files**, not public `/media/` URLs (section 7).
8. **A policy they can read.** Plain language, short, reading-age appropriate, plus one for guardians.
9. **Easy deletion:** a guardian can ask for everything to be deleted, and you can do it quickly (`/privacy/my-data/` plus an admin procedure).
10. **Minimise records about children,** collect the minimum, and delete on a schedule.

If you decide differently (for example, an adult-only site that happens to be used by a few teenagers), record it, and consider adding a clear age statement and a way to remove under-age accounts.

---

## 5. Consent: what it is, and what it isn't

Consent is only valid if it is **informed, specific, freely given, and as easy to withdraw as to give**. Practical rules:

* Don't pre-tick boxes. Don't bundle ("agree to everything or you can't use the site") unless the thing is truly necessary for the service.
* Terms and privacy acceptance at sign-up is a **record** (`ConsentRecord`, with the **version** of the text agreed), not just a click you forget.
* Marketing email needs its own separate opt-in and an unsubscribe link in every message.
* A withdrawal is a new record (`granted=False`), never an edited or deleted one: the history is the evidence.
* **Consent is not the only legal basis** (contract, legal obligation, legitimate interest also exist). Don't ask for consent you don't need, because consent can be withdrawn.

---

## 6. People's rights: see, take, correct, delete

Privacy laws (GDPR, UK GDPR, California's CCPA/CPRA, Israel's law, and others) give people some version of: **know** what you hold, **get a copy**, **correct** it,
**delete** it, and **object** to some uses. The blueprint builds the two hard ones:

* **`/privacy/my-data/`**: a signed-in person downloads everything the site holds about them (JSON), or deletes their account and data (typing their username to confirm).
* **The registry (`core/privacy.py`)**: each app registers an *exporter* (what it stores about a person) and an *eraser* (what a cascade will **not** remove, typically uploaded **files**).

**Every app must register** both when it stores personal data. It is part of the app checklist ([building_an_app.md](building_an_app.md), Rule 7), and a test per app should prove that
an erased person's rows **and files** are gone and someone else's are untouched (see `tests/test_privacy.py`).

Also decide, and write down, how you handle a request that arrives by email: who answers, within what time (GDPR: one month), how you verify identity, and what you do about backups
(they age out: this blueprint keeps bucket snapshots 30 days, so a deletion is fully gone from backups within about 30 days; say so in your policy; it's already in the generated one).

---

## 7. Uploaded files: unguessable is not private

Everything under `/media/` is served **to anyone who has the URL, with no login**. This blueprint stores uploads under random file names (so URLs can't be guessed and names
like `dana-passport.jpg` never appear), but anyone who is *given or finds* a URL can open it, including via browser history, shared screenshots and referrers.

| Your uploads are... | Recommendation |
|---|---|
| Public by nature (a recipe photo meant to be seen) | Current setup is fine. Compress images, strip location data (EXIF) if people upload phone photos |
| Personal but not sensitive (a profile picture) | Current setup is acceptable; random names; consider downscaling and stripping EXIF |
| **Sensitive or about minors** (school work with names, ID, medical, anything you'd mind seeing on a stranger's screen) | **Do not use public `/media/`.** Store outside `MEDIA_ROOT` (e.g. `PERSISTENT_ROOT/private/`) and serve through a view that checks who is asking. The reference site did exactly this for teenagers' uploads |

Claude will ask which of these your uploads are *during the data model step*, because it changes the design. **EXIF:** phone photos often contain GPS coordinates; strip them on upload for any personal photos.

---

## 8. Your data, your helpers (third parties)

Each service you connect sees some data. Name them in your policy, use only what you need, and know what you've agreed to.

| Service | Sees | Notes |
|---|---|---|
| **Render** | Everything on the site (it hosts it) | Choose the region closest to your users; they are your "processor" |
| **GitHub** | Your code (never your data, never secrets) | Private repo; don't commit production data |
| **Google (sign-in)** | That a person signed in; gives you their name/email | Only request `profile` and `email` scopes |
| **Resend** | The email addresses and message content you send | Don't put secrets in emails; no sensitive data |
| **OpenAI** | Whatever text you send in a request | Check their current API data-use and retention terms. As of writing, API data is not used for training by default, but terms change: verify. Never send children's personal details or secrets; disclose AI use |
| **GCS (backups)** | A copy of your whole database and media | Encrypted at rest by Google; bucket is private; key held only in Render |
| **Plausible** | Page visits, no cookies, no personal profile | Name it in your policy |

**Where data lives:** check the region of each service. Some laws restrict moving personal data between regions; a lawyer can tell you whether it matters for you.

---

## 9. In every data model: the personal-data pass

When Claude drafts `docs/<app>/data_model.md` it adds a **Personal data** section and asks you to confirm it. For each field and model:

| Question | Why |
|---|---|
| Is it personal data (could it identify or say something about a person)? | Decides everything below |
| Is it **sensitive** (health, beliefs, children's details, precise location, ID, finances)? | Needs more care, maybe more consent, maybe not collecting at all |
| **Why** do we collect it, in one sentence? | If you can't say, don't collect it |
| Who can **see** it (the person, other users, staff, the public)? | Drives permissions and scoping |
| How long do we **keep** it? | Retention: delete when no longer needed |
| Does the exporter/eraser **cover** it (including files)? | Rights must work |
| Does it appear in **logs, emails, backups, AI prompts**? | The places data leaks without anyone deciding to |

Then a test: erase a person, and prove nothing of theirs remains while someone else's is untouched.

---

## 10. Logs, backups and AI prompts

* **Logs:** don't write personal data into log lines (no emails, no message bodies). Render keeps logs for a limited time; logs are still data.
* **Backups** contain everything, including data people asked you to delete, until they age out. Keep retention as short as your recovery needs allow, and keep the bucket private.
* **AI prompts and responses** may contain personal data. Don't log full prompts. Consider whether you need to store AI conversations at all; if you do, they are personal data
  (export, erase, retain for as short as possible).
* **Error alerts by email** can contain request details; send them only to you.

---

## 11. Retention: decide how long, write it down

"Forever" is a decision with a cost. A reasonable starting policy: keep an account while it's active; delete accounts inactive for N years after warning; keep logs weeks, not years;
keep backups 30 days. Put your numbers in [privacy_decisions.md](privacy_decisions.md) and in the policy. Automate deletion with a management command (and a test) instead of promising to remember.

---

## 12. If something goes wrong (a breach)

A lost laptop with a `.env`, a leaked key, a misconfigured bucket: assume it will happen once, and know the steps.

1. **Contain**: rotate the credential at its provider, update Render and `.env`, suspend if needed ([security.md](security.md) "If you suspect a leak").
2. **Find out**: what was exposed, whose, since when? Check provider logs.
3. **Tell the right people.** Under GDPR a breach likely to harm people must be reported to the supervisory authority **within 72 hours of becoming aware**, and to the affected people
   if the risk is high. Other regimes have similar duties (California, Israel, many US states). A short, plain, honest message beats silence.
4. **Fix and learn**: add a test or hook so that mistake fails next time.
5. **Record it** in [privacy_decisions.md](privacy_decisions.md).

---

## 13. The policy pages

`/privacy/` and `/terms/` are generated from how the site is actually configured and start with a visible **DRAFT** banner. That banner is on purpose. Before you tell anyone about the site:

1. Read both pages end to end. Are they true? Do they say what you actually collect, who else sees it, how long you keep it, and how to reach you (`OWNER_EMAIL`)?
2. Adjust the templates (`templates/core/privacy.html`, `terms.html`) to fit. Add sections for anything specific (children, payments, AI).
3. When you're happy, set `PRIVACY_REVIEWED=True` in Render. The banner disappears and `verify_site.py` stops reminding you. Consider a lawyer's review if the site is more than a hobby.

Keep them updated. When you add a service or a new kind of data, the policy changes in the same pull request.

---

## 14. Privacy checklist by stage

**Interview (before any code):** who are the users and how old; which countries; what personal data is essential; anything sensitive; any school/organisation involved.
**Data model:** the personal-data pass (section 9); private vs public files (section 7); exporter/eraser planned.
**Before launch:** HTTPS check (`verify_site.py --url`); cookies and third parties match the policy; policy reviewed and `PRIVACY_REVIEWED` set; minors' safeguards decided; 2FA on admin accounts; a deletion tested.
**Every release:** did we add a field, a cookie, a service, or a log line that touches personal data? Update the policy and the registry.
**Yearly:** delete what's past retention; review third parties; re-read this guide; check the law for your regions.

---

## Recording your decisions

When you go a different way from the advice here, add a row to [privacy_decisions.md](privacy_decisions.md): the topic, what was advised, what you decided, why, and when to revisit.
That's not bureaucracy: it is what lets you explain yourself to a user, a parent, a school or a regulator, and what stops future-you from "fixing" something that was deliberate.

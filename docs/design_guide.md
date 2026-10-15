# A practical design guide for people who are not designers

Good design is mostly **deciding what matters and getting everything else out of the way**. These rules
cover most of what separates a site that feels professional from one that doesn't. Claude uses this guide
as a mentor: after building a screen it reviews it against the checklist at the bottom and gives you 1-3
concrete suggestions. You can ask for that review any time ("review this page's design").

## 1. Start from the job, not the look

Before any colour or layout, finish this sentence for each page: **"A visitor comes here to ______."**
Then ask what the *one* thing they should do next is (sign up, read, buy, add a note). That is the primary action.
A page with three equally loud buttons has no primary action, and visitors freeze.

## 2. Hierarchy: make importance visible

* **One main heading** per page (`<h1>`), then section headings. Size and weight should rank things in the order you'd rank them aloud.
* **One primary button** per screen, in the accent colour. Secondary actions look quieter (outline or plain link).
  Dangerous actions (delete, close forever) never look like the primary one.
* Group related things together and separate unrelated things with space, not lines.
  *Proximity says "these belong together"*.

## 3. Space and alignment

* Generous whitespace is not wasted space; it's what makes content readable. When a layout feels cramped, add space before adding decoration.
* Use a small, repeating scale of spacing (0.5rem, 1rem, 1.5rem, 3rem). Random gaps look sloppy even when nobody can say why.
* Align things to the same left edge. Centre only short things (a headline, a button), not paragraphs.
* Keep text lines to about 45-75 characters (`max-width: 50rem` on the main column, as this repo does).

## 4. Type

* One font family (the system font stack is fast and looks native). Two weights (regular and bold) go a long way.
* Body text 16px or larger; never smaller than 14px for anything that must be read.
* Line height around 1.5 for paragraphs.
* Don't use ALL CAPS for sentences, and don't underline anything that isn't a link.

## 5. Colour

* Pick **one accent colour** and use it for the primary action and links. Everything else: neutral greys.
* **Contrast**: text must be easy to read against its background (WCAG AA: 4.5:1 for normal text). Light grey on white is the
  most common failure. Check with any contrast checker; Claude can compute it.
* Never use colour as the *only* signal (red/green status): add a word or icon.
* Support **dark mode**. This repo defines colours as CSS variables and flips them with `prefers-color-scheme`; keep doing that.

## 6. Mobile first

Most visitors are on a phone. Design the phone layout first, then let it widen.
* Tap targets at least 44px tall. Fingers are bigger than cursors.
* No sideways scrolling, ever (except inside a table or diagram that opts in).
* One column on phones; navigation that wraps or collapses cleanly.
* **Look at every screen at 390px wide before you call it done**: in the browser's responsive mode, or on your own phone.

## 7. Forms

* A visible **label** for every input (placeholders disappear when you type). Ask only for what you need.
* Say what went wrong **next to the field**, in plain words, and say how to fix it ("Password needs at least 8 characters").
* Preserve what the person typed when there's an error. Disable the submit button only while it is working.
* After success, confirm it (a message or a clear change on the page).

## 8. The states people forget (this is where polish lives)

For every list or page, design all of these, not just the happy one:
* **Empty**: "No notes yet. Add your first one." (with the button), never a blank page.
* **Loading**: something visible when a request takes more than a moment.
* **Error**: a friendly message and a way out. Our 404/500 pages exist for this reason.
* **Too much**: what happens with 500 items? (paging, search)
* **First visit vs returning**: what does a brand-new user see?

## 9. Content is the design

* Write the real words first. Lorem ipsum hides layout problems.
* Buttons say what they do ("Add note", not "Submit"). Headings say what the section is, not something clever.
* Short sentences. Cut every word that isn't doing a job.
* Be consistent: the same thing has the same name everywhere ("Sign in", never "Log in" on one page and "Login" on another).

## 10. Accessibility is part of quality, not an extra

* Semantic HTML (headings, lists, buttons are `<button>`, links are `<a>`).
* `alt` text on images that carry meaning (empty `alt=""` for decoration).
* Everything works with the keyboard; focus is visible; don't remove outlines.
* Zoom to 200% and check nothing breaks. Respect `prefers-reduced-motion` if you animate.

## 11. Speed is a design feature

Compress images before uploading (a 6 MB phone photo on a mobile connection is a design failure). Don't load libraries you don't use.
Prefer plain HTML and a little CSS over a framework until you feel a real need.

## 12. Be consistent, then be restrained

Reuse the same button, card and spacing everywhere (this is why apps keep their own `notes-` prefixed classes and a shared base).
Resist adding another colour, font, animation or effect. When in doubt, remove something.

---

## The review checklist Claude runs on every screen

- [ ] I can finish "a visitor comes here to ____" and the page does that job first
- [ ] One clear primary action; secondary actions are quieter; destructive actions look different
- [ ] Headings rank things in order; the page can be skimmed
- [ ] Spacing is consistent; related things grouped; text lines not too long
- [ ] Contrast is sufficient; colour is not the only signal; dark mode works
- [ ] Checked at 390px: no sideways scroll, tap targets big enough
- [ ] Every input has a label and a helpful error message
- [ ] Empty, loading and error states exist and read well
- [ ] Words are specific and consistent
- [ ] Keyboard-usable, images have alt text, page loads quickly

### What a good review sounds like

> "The page works, and the hierarchy is clear. Three suggestions: (1) 'Delete' sits right next to 'Save' and has the same
> weight; make it a quiet link and put it away from Save. (2) The empty state is blank; add 'No notes yet' with the Add button.
> (3) Grey helper text is 3.1:1 contrast; darken it to pass. Want me to make those changes?"

Specific, ranked, kind, and always paired with an offer to do it. Learn the *reason* behind each suggestion and you will start
making these calls yourself.

---
name: design-review
description: >
  Review and improve the design of a page or screen for a non-designer owner: purpose and hierarchy, spacing, type,
  colour and contrast, dark mode, mobile at 390px, forms, empty/loading/error states, content wording, accessibility,
  and speed; gives at most three ranked suggestions with reasons and offers to apply them. TRIGGER: "design", "review
  this page", "does this look good", "ui", "ux", "layout", "make it prettier", "mobile", "responsive",
  "accessibility", "contrast", "colors", "form design", "empty state".
---

# Design review

Source of truth: [docs/design_guide.md](../../../docs/design_guide.md) (includes the checklist). Re-read it first.

## How to review

1. **Ask what the page is for** ("a visitor comes here to ____") and what the one primary action is, before judging anything.
2. **Look at it as an image.** Run the site and take screenshots at about **390px** (phone) and desktop width (headless Edge/Chrome, or the browser's responsive mode). Never review from the HTML alone: layout bugs are invisible in markup.
3. **Walk the checklist** at the bottom of the design guide: hierarchy; one primary action; spacing and alignment; type; contrast (compute it) and colour-not-the-only-signal; dark mode; 390px with no sideways scroll and 44px tap targets; labelled inputs with helpful errors; empty/loading/error states; specific, consistent words; keyboard use, alt text, speed.
4. **Give at most three suggestions, ranked**, each with the reason, and offer to apply them. Specific, kind, never a silent redesign. Praise only what is actually good.
5. After applying, re-screenshot and confirm. Add a structural test when a guard is general (for example "every class the markup uses is defined in the stylesheet", or "no horizontal overflow at 390px").

## Rules that came from real mistakes

**Every role, every stage, side by side.** When the site has roles (admin, member, visitor) or stages (before, during, after), screenshot each role's home at each stage at phone
width and put them in one image per stage. Ask of each column: does this person see something true and specific about *themselves*, and does every link open for them? This found
seven real bugs in an app whose every feature had passing tests.

Name component classes after the component and prefix them with the app (collisions are silent). A class that styles nothing is silence, not an error. Tests that read HTML cannot see layout. Apply a principle everywhere it applies, not only where it was noticed.
Teach as you go: one sentence of *why* per suggestion so the owner starts making these calls themselves ([site-mentor](../site-mentor/SKILL.md)).

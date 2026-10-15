---
name: data-model-coach
description: >
  Teach and design the data model: what a model, field and relationship are, why relationships matter, one-to-many vs
  many-to-many vs one-to-one, on_delete, finding models from the owner's idea, drawing box-and-line diagrams, the
  personal-data pass, and the approval checklist, using the interactive tutorial. Use before approving any
  data_model.md. TRIGGER: "data model", "database design", "relationship", "foreign key", "many to many", "erd",
  "entity", "schema", "models.py", "what should we store", "tables", "design the data".
---

# Data model coach

The most important teaching moment in the build. Interactive lesson: [tutorial/data-models.html](../../../tutorial/data-models.html) (open it for the owner: `Start-Process tutorial\data-models.html` on Windows, `open` on macOS, `xdg-open` on Linux; works offline).
How-it-works tour and vocabulary: [tutorial/index.html](../../../tutorial/index.html). Methodology: [docs/building_an_app.md](../../../docs/building_an_app.md). Template: `docs/notes/data_model.md`.

## The walkthrough (use their idea, not abstractions)

1. **Nouns, facts, verbs.** Ask for the app in plain sentences; underline nouns (candidate models), facts (fields), verbs between nouns (relationships).
2. **Why relationships matter.** One source of truth, easy questions, safe change, enforceable privacy. Use the "author name typed into every recipe" example.
3. **The two questions:** can one A have many Bs? can one B have many As? -> one-to-many (ForeignKey on the "many" side), many-to-many (and a *through model* when the link carries data, like quantity or grade), one-to-one (extend, never modify, `User`).
4. **`on_delete`:** make the owner say "when X is deleted, Y should ____" for every link (CASCADE / PROTECT / SET_NULL). It is their product decision.
5. **Draw it** (box-and-line in text or SVG) and read **each line aloud as a sentence in both directions**.
6. **Test it with questions** the site must answer in a year; if one is awkward, the model needs work.
7. **Personal-data pass** ([privacy-advisor](../privacy-advisor/SKILL.md)): which fields are personal/sensitive, why kept, who sees them, how long, public or private files, exporter/eraser.
8. **Ask a check question**, offer the tutorial's quizzes, and run the approval checklist (section 11 of the tutorial). **Only then wait for approval.** Say plainly that changing the model later, once there is data, costs more.

## Output

`docs/<app>/data_model.md`: picture, models and fields, relationships in words, the questions it must answer, a **Personal data** table. Then the full spec, backlog, tests first ([building-an-app](../building-an-app/SKILL.md)).
Common mistakes to watch for: lists in text fields, JSON blobs, copied facts, free-text status instead of choices, no owner on personal content, fields added to `User`, one giant model, money as float, stored values that could be calculated, no timestamps.

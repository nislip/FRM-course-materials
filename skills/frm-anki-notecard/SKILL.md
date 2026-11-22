---
name: frm-anki-notecard
description: Create Anki flashcards for FRM (GARP Financial Risk Manager) study from the course semantic layer, written in the style of GARP exam questions. Use when the user asks to make, add or update Anki cards, flashcards or a deck for an FRM reading, chapter, term, concept or formula. Requires the Anki MCP server.
---

# FRM Anki notecards

Turn entries in the semantic layer into Anki cards that read like FRM exam questions.

## Sources

- **Content:** `${CLAUDE_SKILL_DIR}/../../semantic-layer/` (`terminology/`, `concepts/`, `formulas/`, each under `<part>/<reading>.yaml`). Use `${CLAUDE_SKILL_DIR}/../../graph/concept-graph.json` to find entries and their `links`.
- **Question style:** the two Notion pages in the "FRM Part I & II" database whose `Domain Type` is `Question Bank`:
  - "Extra Sources: Sample Questions from GARP Study Guide"
  - "Extra Resources: Sample Questions from Analyst Prep"

  Before writing cards for a chapter, fetch both pages and read the questions for that chapter, if there are any. Copy their phrasing and difficulty. Don't copy them word for word.

## Card style

Use only these three formats, which are the ones the sample questions use:

| Type | Front | Back |
|---|---|---|
| **Multiple Choice** | A short scenario or stem, then options A–D on separate lines. Wrong options are real FRM terms that a student could confuse with the answer, such as strategic, credit or operational risk. | The correct letter, one line on why it is right, and one line on why the strongest wrong option is wrong. |
| **True or False** | One statement. False statements should contain a single plausible error, such as two items swapped (first and second line of defense) or an "always" that should be "sometimes". | "True" or "False, because …" |
| **Short Answer** | "Describe…", "What does it mean if…", "Provide examples of…" | The definition or `key_points` from the entry, in a few short lines. |

Rules:

- Prefer applied questions to definition recall. For example: "A bank reports a 1-day 97.5% VaR of USD 14M. What does this mean?"
- Formulas get a numeric question built from the entry's `examples`. Recompute the answer and check it matches `output` within `tolerance`. Show the working on the back.
- Write one fact per card. Aim for 2–4 cards for each concept or formula and 1–2 for each term.
- Build every answer from the YAML. Skip any entry whose `definition` is `null` or whose graph node has `complete: false`, and list the skipped entries at the end.
- Add the source on the back when the entry has one, e.g. `GARP FRM Part I, Book 1, ch. 3`.

## Decks and tags

- **Deck:** `FRM::<Part>::<Reading>`, e.g. `FRM::Part I::01 Building Blocks of Risk Management`. Use one deck per reading file, so the decks match the semantic layer.
- **Note type:** `Basic`, with fields `Front` and `Back`.
- **Tags:** put these on every note:
  - `frm-id::<entry-id>` (used to find duplicates)
  - `frm-kind::<term|concept|formula>`
  - `frm-qtype::<mc|tf|short>`
  - `frm-part::<part-I|part-II>`

## Steps

1. **Scope.** Confirm which reading, chapter or entries to cover. If the user didn't say, ask.
2. **Read** the YAML entries for that scope and the matching sample questions in Notion.
3. **Avoid duplicates.** For each entry, search Anki for `tag:frm-id::<id>`. If an entry already has cards, skip it, unless the user asked to regenerate it.
4. **Draft and preview.** Show the drafted cards to the user in a compact table before adding them.
5. **Add.** Create the deck if it is missing, then add all notes in one batch call.
6. **Report** the number of cards added for each deck, the entries skipped as duplicates, and the entries skipped as incomplete.

## Rules

- Don't edit the semantic layer or the graph files.
- If the Anki MCP tools are unavailable, tell the user that Anki must be open with AnkiConnect running. Don't fall back to writing files.

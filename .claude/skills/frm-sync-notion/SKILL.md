---
name: frm-sync-notion
description: Sync FRM study notes from Notion into the semantic layer. Finds Notion pages in the "FRM Part I & II" database edited since the last sync, extracts terms and concepts, merges them into semantic-layer/terminology and semantic-layer/concepts, rebuilds the graph, and opens or updates a PR. Use when asked to sync, import or pull Notion notes into the FRM knowledge base. Runs nightly as a cloud routine.
---

# Sync Notion notes into the semantic layer

You turn the user's Notion study notes into entries in `semantic-layer/`. A human reviews every change in a PR, so be careful and leave a clear record of what you did.

## Inputs

- **Notion source.** A Notion database inside the "FRM Part I & II" page. Each page is one set of notes and is tagged with the exam part, e.g. `FRM Exam > Part I` or `FRM Exam > Part II`. Use the Notion connector tools (`notion-search`, `notion-fetch`, and `notion-query-data-sources` or `notion-query-database-view`).
- **State file.** `.sync/notion-state.json`, shaped like this:

  ```json
  {
    "database_id": "…",
    "last_synced_at": "2026-11-18T07:00:00Z",
    "pages": {
      "<notion-page-id>": {
        "title": "Building Blocks of Risk Management",
        "part": "frm-part-I",
        "reading": "01_building-blocks-risk-management",
        "last_edited_time": "2026-11-17T22:14:00Z"
      }
    }
  }
  ```

  `database_id` may be `null` on the first run. If it is, find the database by searching Notion for "FRM Part I & II", then save the ID.

## Steps

### 1. Set up the working branch

Always work on the branch `claude/notion-sync`.

- If `origin/claude/notion-sync` exists, an earlier sync PR has not been merged yet. Check out that branch and build on it, so its state file and edits carry forward. Run `git merge origin/main` too, to pick up anything the user merged since.
- Otherwise, create `claude/notion-sync` from `origin/main`.

This keeps all pending sync work in one PR and stops the same Notion change from being imported twice.

### 2. Find changed pages

1. Query the database for **every** page, not only recent ones. Record each page's ID, title, exam-part tag and `last_edited_time`.
2. A page **changed** if it isn't in `state.pages`, or if its `last_edited_time` is later than the stored one.
3. If nothing changed, **stop**. Make no commit and no PR. Report "No Notion changes since <last_synced_at>".

### 3. Map each changed page to a reading file

- **Part:** `FRM Exam > Part I` → `frm-part-I`, `FRM Exam > Part II` → `frm-part-II`. If a page has no part tag, skip it and list it in the PR body.
- **Reading:** if the page is already in `state.pages`, reuse its `reading`. Otherwise, match the title to an existing file in `semantic-layer/*/<part>/` (e.g. "Building Blocks of Risk Management" → `01_building-blocks-risk-management`). If there is no match, create a slug: `NN_kebab-case-title`, where `NN` is the GARP reading number if the page states one, or else the next free number in that part. Drop filler words such as "of", "the" and "and", as the existing file does.

### 4. Extract entries

Read the whole page with `notion-fetch`, including nested toggles and child blocks. Sort what you find into two kinds:

- **Terms** (`semantic-layer/terminology/<part>/<reading>.yaml`) are named things with a definition, such as a type of risk, an instrument or a ratio name. Fields, in this order:
  `id, name, aliases, acronyms, definition, related, notation, examples`
- **Concepts** (`semantic-layer/concepts/<part>/<reading>.yaml`) are bigger ideas with several points, such as a framework, a method, or a relationship between risks. Fields, in this order:
  `id, name, aliases, definition, key_points, formulas, learning_objectives`

Formulas are **out of scope**. If a page contains a formula, don't write to `semantic-layer/formulas/`. List it under "Formulas seen but not imported" in the PR body. A concept may still list a formula ID in `formulas:`.

Rules for the content:

- `id` is kebab-case of the name (`credit-risk`). IDs are unique across **all** of `semantic-layer/`. Before adding an entry, grep for the ID. If it already exists anywhere, update that entry rather than creating a second one, even if it's in another reading or folder.
- `definition` is one or two sentences, written as a YAML folded block (`>`). Keep the user's own wording from their notes where it reads as their notes. Don't paste long passages that look copied word for word from the GARP curriculum; paraphrase those. The repo is shared.
- `related` must be **two-way**. If you add B to A's `related`, add A to B's `related` too, as long as B exists. Only link entries the notes actually connect, such as "X is a type of Y" or "X is driven by Y".
- Use `null` for fields with no content, as the existing files do. Never invent content to fill a field.
- Keep existing entries in the same order, and append new entries at the end of the file. Match the existing indentation and the blank line between entries.

### 5. Merge, never clobber

For each extracted entry:

| Existing value | Notion has | Action |
|---|---|---|
| entry missing | content | Add the entry |
| `null` / `[]` | content | Fill it in |
| list (`related`, `aliases`, `key_points`) | more items | Add the new items and keep the existing ones |
| text the user wrote | same meaning | Leave it |
| text the user wrote | **different** content | **Don't overwrite.** Add the conflict to the PR body under "Conflicts to review", quoting both versions |

Never delete an entry or a field. Even if a term was removed from Notion, keep it and list it under "In repo but no longer in Notion".

### 6. Validate

```sh
pip install -q pyyaml 2>/dev/null || true
python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('semantic-layer/**/*.yaml', recursive=True)]"
python3 scripts/build_graph.py
```

Both commands must succeed. The pre-commit hook isn't installed in the cloud, so run `build_graph.py` yourself, and commit `graph/concept-graph.json`, `graph/concept-graph.md` and `graph/concept-graph.html` along with the YAML. If validation fails, fix the YAML. If you can't fix it, stop: don't commit, and report the error.

### 7. Update state, commit, PR

1. In `.sync/notion-state.json`, update `pages[<id>]` for every page you processed (title, part, reading, `last_edited_time`), set `last_synced_at` to now (UTC), and set `database_id`. Write it with 2-space indentation and keys sorted.
2. Bump the patch number of `version` in `.claude-plugin/plugin.json` (e.g. `0.1.0` → `0.1.1`), but only once per PR: skip it if this branch already bumped it compared with `origin/main`.
3. Commit with the message `Sync Notion notes: <n> pages, +<a> terms, +<b> concepts, <c> fields filled`, then push `claude/notion-sync`.
4. If no PR is open from `claude/notion-sync`, open one into `main`, titled `Notion sync: <date>`. If one is open, update its body. The body must include:
   - **Pages processed**: each with a Notion link and its target reading file
   - **Added**: new term and concept IDs
   - **Filled**: `id.field` for every field that was null before
   - **Conflicts to review**: both versions quoted, or "none"
   - **Formulas seen but not imported**
   - **Skipped**: pages with no part tag, and anything you couldn't classify
   - **In repo but no longer in Notion**

## Final report

Finish with a short summary: how many pages changed, the counts of added and filled entries, any conflicts, and the PR URL. If nothing changed, say so in one line.

# FRM-course-materials
This repo holds all the information pulled from notes across FRM topics. It is also a Claude Code plugin, so Claude can look up terms and formulas and walk the concept graph.

# Using it as a Claude Code plugin

Install in Claude Code:

```
/plugin marketplace add nislip/FRM-course-materials
/plugin install frm-course-materials@frm-course-materials
```

Run `/plugin marketplace update frm-course-materials` to get new notes. Then just ask: "what is market risk?", "how does parametric VaR relate to expected shortfall?", "what should I study before VaR?", "what's missing from my notes?", "open the concept graph".

To try local changes without installing: `claude --plugin-dir /path/to/FRM-course-materials`.

| Path | What it is | Who uses it |
|---|---|---|
| `semantic-layer/` | The notes: terms, concepts and formulas as YAML. **The source of truth.** | You edit it, the skills read it |
| `graph/concept-graph.json` | Generated graph keyed by id, with links and coverage summary | The skills |
| `graph/concept-graph.html` | Generated FRM Mind Map: interactive graph plus Term, Concept and Formula glossaries | People, in a browser |
| `graph/concept-graph.md` | Generated Mermaid diagram | People, on GitHub |
| `skills/frm-lookup/` | Answers definitions and formulas from the notes, with citations | Claude |
| `skills/frm-concept-map/` | Connections, study order, coverage gaps, opens the graph | Claude |
| `scripts/` | Graph generator and HTML template | Maintainers (run by the pre-commit hook) |
| `.claude/skills/frm-sync-notion/` | Nightly cloud routine: pulls changed Notion notes into terminology and concepts, opens a PR from `claude/notion-sync` | Claude (scheduled) |
| `.sync/notion-state.json` | Which Notion pages were synced and when | The sync skill |
| `.claude-plugin/` | Plugin and marketplace manifests | Claude Code |

Before publishing a change, bump `version` in `.claude-plugin/plugin.json` and run `claude plugin validate .`.

Keep definitions in your own words and cite `source`; don't copy GARP curriculum text verbatim, since this repo is shared.

# Repository Control Flow

test >> Main

1) Clone the repository from main

``` 

git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

```

2) Create branch off of test

- fetch downloads a list of branches from github
- `checkout test` automatically creates a local test branch tracking origin/test
- If there is no local `test` branch but a remote one exists, for example `origin/test` it will create a local `test` branch tracking the remote one then swirches to that.
- To reduce ambiguity you can use `git switch -c test` to create a new branch and swithc to it in one step.

```

git checkout test
git pull origin test
git checkout -b feature/my-change

```

3) Make the changes, commit and then push these changes

```

git add .
git commit -m "Describe your change"
git push -u origin feature/my-change

```

4) Open the pull request

```

gh pr create --base test --head feature/my-change --title "My change" --body "What this does"

gh pr create --base dev --head test --title "Promote test to dev" --body "Changes from test"

```

5) Other useful commands commands

- `-v` stands for verbose and makes it show the URLS, not just the names
- `remote` is the remote repositories that your local repo is connected to along with their URLs
- `origin` is the remote repo's name and `origin` is the default name that git gies the remote you cloned from

```

git remote -v
git branch -a

```

- For example, `git remote -v` may return something like this.

```

origin  https://github.com/nislip/FRM-study-agent.git (fetch)
origin  https://github.com/nislip/FRM-study-agent.git (push)

```

```
git status --short
git diff --shortstat
```
# FRM Mind Map

`graph/` holds a graph of every term, concept and formula in `semantic-layer/`, built from the `related`, `concepts` and `variants` fields.

- `graph/concept-graph.json` is what the plugin skills query.
- `graph/concept-graph.md` renders on GitHub and in the VS Code Markdown preview.
- `graph/concept-graph.html` is the FRM Mind Map: open it in a browser. The Mind Map tab is the interactive graph (click a node for its definition and links); the Terms, Concepts and Formulas tabs are searchable glossaries with formulas rendered.

Both are generated, so don't edit them by hand. A pre-commit hook rebuilds them whenever `semantic-layer/` changes. After cloning, run once:

```
pip3 install -r requirements.txt
git config core.hooksPath .githooks
```

To rebuild manually: `python3 scripts/build_graph.py`

Links can be plain ids (`related: [market-risk]`) or typed (`related: [{ id: market-risk, type: is-a }]`). Typed links show as labelled arrows.

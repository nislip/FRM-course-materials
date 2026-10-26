# FRM-course-materials
This repo holds all the information pulled from notes across FRM topics

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
# Concept Graph

`graph/` holds a graph of every term, concept and formula in `semantic-layer/`, built from the `related`, `concepts` and `variants` fields.

- `graph/concept-graph.md` renders on GitHub and in the VS Code Markdown preview.
- `graph/concept-graph.html` is interactive: open it in a browser, click a node to see its definition and links.

Both are generated, so don't edit them by hand. A pre-commit hook rebuilds them whenever `semantic-layer/` changes. After cloning, run once:

```
pip3 install -r requirements.txt
git config core.hooksPath .githooks
```

To rebuild manually: `python3 scripts/build_graph.py`

Links can be plain ids (`related: [market-risk]`) or typed (`related: [{ id: market-risk, type: is-a }]`). Typed links show as labelled arrows.

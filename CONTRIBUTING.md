# Contributing

Thanks for helping keep this list useful. The list leans toward **where papers meet engineering**, so
repos without papers, closed systems described in blogs, incident write-ups and lab policies are all
in scope, as long as they say something about how an improvement loop is *run*.

## Add an entry

1. Add one record to [`data/entries.yaml`](data/entries.yaml), in the block for its section:

   ```yaml
   - title: "RSIGym: A Flexible Environment for Recursive Self-Improvement"  # exact title for papers
     year: 2026
     month: 10                      # optional, only used for ordering
     venue: arXiv                   # or ICLR 2026, Blog, Report, GitHub, Product ...
     org: Evolvent AI               # optional
     section: execution.runtime     # an id from data/sections.yaml
     links: {paper: "https://arxiv.org/abs/2610.10310", code: "https://github.com/evolvent-ai/RSIGym"}
     access: open                   # open | closed | paper
     note: "Training, inference, rollout, eval and sandbox as services behind one auth, budget and permission layer."
   ```

   - **title**: the exact arXiv title for papers. For a project without a paper, use `Name: what it is`.
   - **links**: any of `paper`, `code`, `blog`, `project`, `docs`. Link the primary source: the lab's own
     post, not news coverage.
   - **access**: `open` if code or the system is released, `closed` if it is only described (blog,
     report, paper about an internal system), `paper` for a paper with no code.
   - **note**: one factual line on what it gives an improvement loop. No hype words.

2. Regenerate the tables:

   ```bash
   pip install pyyaml
   python scripts/build_readme.py
   ```

   The script checks required fields, section ids and duplicate links, and rewrites only the generated
   parts of `README.md`. `python scripts/build_readme.py --check` tells you if the README is stale.

3. Open a PR. One PR may add many entries.

## What does not fit

- General agent frameworks or LLM tooling with no link to an improvement loop.
- Pure method papers with nothing to say about execution, evaluation, lineage or control. Those belong
  in a method-centric list; see *Related Resources* in the README.

## Figures

The figures in `figures/` are maintained by the authors; only the rendered PNGs live in this repository.
The taxonomy figure is drawn from `data/entries.yaml`, so a leaf it shows must exist in the list. If an
entry you add should appear in a figure, say so in the PR and we will redraw it.

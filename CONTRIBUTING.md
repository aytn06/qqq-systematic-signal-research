# Contributing

This repository is a research codebase, so good contributions improve both the code and the research discipline around it.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Core Principles

- Do not introduce lookahead bias.
- Keep signal logic interpretable.
- Preserve the train / validation / holdout boundary.
- Do not commit proprietary or licensed datasets.
- Prefer small, reviewable pull requests.

## Recommended Workflow

1. Create or update one signal family at a time.
2. Re-run the baseline backtest summary.
3. Re-generate diagnostic plots if the signal set changes materially.
4. Run `pytest` before pushing.
5. Document important assumptions in the relevant module or report.

## Data Hygiene

- Keep large raw files out of the repository.
- Use `data/README.md` to document local datasets.
- Treat `data/sample_prices.csv` as a smoke-test fixture only.

## Pull Request Expectations

A good pull request should explain:

- what changed
- why it changed
- whether the holdout period was touched or only referenced
- how the change was validated

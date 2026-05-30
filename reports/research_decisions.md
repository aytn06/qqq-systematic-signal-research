# Research Notes

This note records the main choices behind the committed version of the QQQ
project.

## Included Dataset Versus Original Submission

The original finalist submission used a longer challenge dataset. The repo uses
an included dataset so the code can run end to end without reposting that
source data.

## Shifted Exposure

The backtest applies today's chosen exposure to tomorrow's return. That makes
the backtest a little harsher, but it is much easier to defend.

## Family Diversity

Several signals turned out to behave too similarly to justify keeping all of
them in the final ensemble. The final version keeps one strong representative
instead of pretending near-duplicate signals are independent ideas.

## Validation-Only Selection

The final ensemble is chosen on validation, not holdout. That matters because
it keeps the holdout period as a real out-of-sample check.

## Negative Holdout

The included dataset does not give the final ensemble a positive holdout
Sharpe. I left that result in the repo because it is the honest result on the
included data.

## Evidence Gap

The original finalist result is still best supported as a saved project
summary. If stronger old files turn up later, they belong in
`reports/original_challenge_evidence/`.

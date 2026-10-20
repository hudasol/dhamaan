# Human check of the evidence table: design

Written and committed before any row was read. The sample frame (`sample_frame.csv`) is fixed by seed 20261020 and by `tools/human_check.py draw`.

## Why

Every earlier check of the evidence table was made by automated verifiers from one model family. Their errors can repeat, and their "full text seen" often means a model written extraction of a page. This check puts a person reading the source directly against the table.

## Sample

- 60 rows of 222, stratified by binding status: 20 mandatory, 20 conditional, 10 guidance, 10 voluntary. Mandatory and conditional rows are oversampled because a wrong obligation there costs most.
- Two waves of 30, each with the same proportions. Wave 1 is a valid sample on its own, so a reader who stops after 30 rows still gets a usable estimate with a wider interval.
- Drawn without replacement with a seeded generator. Rerunning the draw reproduces the frame.

## Reader task

For each row the reader opens the source, finds the passage, and records four things in the worksheet: whether the paraphrase is supported (yes, partly, no, cannot open source), which binding status the reader would assign using the written definitions, what access level the reader reached (full text, summary, title only, could not open), and whether the locator was found. The worksheet hides the table's binding status and access level so the reader decides them from the source. Blinding is by omission only; the table is public.

## Definitions

- **Content error:** paraphrase marked "partly" or "no", or a binding status different from the table's.
- **Access overclaim:** the reader opened the source and reached a lower level than the table claims. Rows the reader could not open are excluded from this count, because a closed page does not show an overclaim.
- Binding statuses follow `docs/PROTOCOL.md`: mandatory, conditional, voluntary, guidance.

## Estimates

- Stratified estimate with weights N_h / N, and a seeded percentile bootstrap interval (10000 resamples).
- Wilson intervals per stratum.
- Agreement and Cohen's kappa for binding status.
- A two by two comparison of human error against the earlier automated flags (passes A and B), to show whether those flags were informative.

## Limits stated in advance

- One reader. Reader error is not measured. A second reader on a subset (the rows at odd positions, for example) would measure it.
- The interval reflects sampling only.
- Rows whose source cannot be opened (paywalled standards) cannot be scored; their number is reported, and they stay at their present access level.

## Predictions written before reading

These are the authors' expectations, fixed now so they can be scored.

| Id | Prediction |
|---|---|
| HC-P1 | The stratified content error rate lies between 15 and 35 percent. |
| HC-P2 | The error rate among mandatory rows is not higher than among guidance rows. |
| HC-P3 | At least 5 of the 60 rows cannot be opened (paywalled or blocked). |
| HC-P4 | Binding agreement with the table is at least 90 percent. |
| HC-P5 | Rows with the table access level "full text seen" show fewer content errors than rows with "summary seen". |

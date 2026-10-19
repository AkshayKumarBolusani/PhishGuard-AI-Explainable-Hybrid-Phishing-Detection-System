# Public benchmark evaluation

This folder holds the independent benchmark evaluation of PhishGuard's detection
core on public corpora. It was run 2026-10-18; results are in
`BENCHMARK_REPORT.md` (human-readable) and `benchmark_results.json` (raw).

## Corpora (not vendored — download before running)

**Phishing Email Curated Datasets**, Zenodo DOI
[10.5281/zenodo.8339691](https://doi.org/10.5281/zenodo.8339691) (CC-BY-4.0).
The run used the byte-identical HuggingFace mirror
`kudzaiprichard/aura-phishing-email-corpus` (all files MD5-verified against the
Zenodo-published checksums). Place these five CSVs in `evaluation/data/`:

- `TREC_07.csv`, `CEAS_08.csv`, `Nazario_5.csv`, `Nigerian_5.csv`, `SpamAssasin.csv`

The 208 MB of raw email data is intentionally not committed to this repo.

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install scikit-learn pandas numpy
# put the five CSVs in evaluation/data/, then from the repo root:
.venv/bin/python evaluation/benchmark.py
```

The script imports the production `RuleEngine` verbatim from
`backend/app/ai/rule_engine.py`, trains TF-IDF + LR / TF-IDF + SVM / a
PILFER-style heuristic baseline and the hybrid ensemble under identical
stratified 5-fold splits (random_state=42), and writes fresh results to
`evaluation/benchmark_results.json`.

## What the numbers mean

See `BENCHMARK_REPORT.md` for the honest reading: the hybrid leads on precision
(0.9850–0.9997) on every corpus but does not beat TF-IDF + SVM on F1. The
130-email demo set in `backend/app/ai/models/seed_data.py` is pipeline
validation only and is never presented as benchmark accuracy.

# Dataset Provenance

The benchmark in this repository uses the **Phishing Email Curated Datasets**
collection, obtained from Zenodo. This document records exactly which data was
used, how it was verified, and under what terms it may be redistributed.

## Source

| Field | Value |
|---|---|
| Collection | Phishing Email Curated Datasets |
| DOI | [10.5281/zenodo.8339691](https://doi.org/10.5281/zenodo.8339691) |
| Version | v1 (published 2023-09-13) |
| License | CC-BY-4.0 |
| Access used for the benchmark run | HuggingFace mirror `kudzaiprichard/aura-phishing-email-corpus`, verified byte-identical to the Zenodo files by MD5 (see below) |

The collection is curated for phishing-email research (see Champa et al.,
ISDFS 2024 and ICMI 2024), but the five corpora it packages originate from
different source tracks — see `label_mapping.md` for what the labels in each
corpus actually mean.

## Corpora and verification

All five CSVs were MD5-verified against the checksums published with the
Zenodo v1 record on 2026-10-19. Row counts below are from
`evaluation/benchmark_results.json`.

| File | Rows | Positive | Legitimate | MD5 (Zenodo v1) |
|---|---|---|---|---|
| `TREC_07.csv` | 53,757 | 29,399 | 24,358 | `e5a5ae0de1580965191cb32806dc0dae` |
| `CEAS_08.csv` | 39,154 | 21,842 | 17,312 | `1f0d59191eec892a709995d48cd8decb` |
| `Nazario_5.csv` | 3,065 | 1,565 | 1,500 | `45db8330ea4aabbf72f5199949ae03e5` |
| `Nigerian_5.csv` | 6,331 | 3,332 | 2,999 | `edfbbb89c40e7447f47867bcc82e72f9` |
| `SpamAssasin.csv` | 5,809 | 1,718 | 4,091 | `d921e0b2333bfaa058bd38193e6b3fbd` |
| **Total** | **108,116** | | | |

Corpus origins, per the benchmark report:

- **TREC_07** — TREC 2007 spam track
- **CEAS_08** — CEAS 2008 challenge
- **Nazario_5** — Nazario phishing + legitimate mail
- **Nigerian_5** — Nigerian (advance-fee) fraud + legitimate mail
- **SpamAssasin** — SpamAssassin corpus (note: the file name uses the source
  collection's spelling, `SpamAssasin`)

## The CSVs are not in this repository

**The dataset CSVs are NOT vendored in this repository.** To reproduce the
benchmark, download the five files from the Zenodo record
(https://doi.org/10.5281/zenodo.8339691) and verify each file's MD5 against
the checksums in the table above before running anything. Only files whose
checksums match exactly are the data the published results were measured on.

## Redistribution and licensing

- The dataset is distributed by its curators under **CC-BY-4.0**. Any reuse or
  redistribution of the data must respect that license, including attribution
  to the dataset's creators and a link to the DOI above.
- This repository's **MIT license covers the code only**. It does not extend
  to, replace, or relicense the third-party dataset, which remains governed
  by CC-BY-4.0 and the terms of the original corpora it packages.
- Because the data is not vendored here, nothing in this repository
  redistributes it; the benchmark code expects the user to obtain the data
  from the source DOI.

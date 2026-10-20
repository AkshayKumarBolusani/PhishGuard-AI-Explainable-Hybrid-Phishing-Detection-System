#!/usr/bin/env bash
#
# run_benchmark.sh — reproduce the PhishGuard benchmark results.
#
# What it does:
#   1. Verifies python3 and the required packages (numpy, pandas, scikit-learn, scipy).
#   2. Verifies the five dataset CSVs are present under <repo>/data/
#      (they are NOT bundled: download them from Zenodo, see the message below).
#   3. Invokes evaluation/benchmark.py (stratified 5-fold CV, random_state=42).
#
# Results are written to evaluation/ (benchmark_results.json, BENCHMARK_REPORT.md).
# The script never downloads data, never modifies the datasets, and fails fast
# on any missing prerequisite.
#
set -euo pipefail

# --- Resolve the repo root from this script's own location -------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
EVAL_DIR="${REPO_ROOT}/evaluation"
ENTRYPOINT="${EVAL_DIR}/benchmark.py"
DATA_DIR="${REPO_ROOT}/data"
BACKEND_DIR="${REPO_ROOT}/backend"

# --- 1. python3 ----------------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found on PATH. Install Python 3.10+ and re-run." >&2
    exit 1
fi

# --- 2. required packages -------------------------------------------------------
if ! python3 -c "import numpy, pandas, sklearn, scipy" 2>/dev/null; then
    echo "ERROR: missing required Python packages." >&2
    echo "Install them with:" >&2
    echo '  pip install "numpy==2.5.4" "pandas==3.0.6" "scikit-learn==1.9.1" "scipy==1.18.1"' >&2
    exit 1
fi

# --- 3. dataset CSVs (never auto-downloaded) ------------------------------------
MISSING=0
for csv in TREC_07.csv CEAS_08.csv Nazario_5.csv Nigerian_5.csv SpamAssasin.csv; do
    if [ ! -f "${DATA_DIR}/${csv}" ]; then
        echo "MISSING: ${DATA_DIR}/${csv}" >&2
        MISSING=1
    fi
done
if [ "${MISSING}" -ne 0 ]; then
    echo "" >&2
    echo "The benchmark datasets are not bundled with this repository." >&2
    echo "Download them (free, CC-BY-4.0) from Zenodo:" >&2
    echo "  https://doi.org/10.5281/zenodo.8339691  (\"Phishing Email Curated Datasets\", v1)" >&2
    echo "Place the five CSV files (TREC_07.csv, CEAS_08.csv, Nazario_5.csv," >&2
    echo "Nigerian_5.csv, SpamAssasin.csv) into:" >&2
    echo "  ${DATA_DIR}/" >&2
    echo "then re-run this script." >&2
    exit 1
fi

# --- sanity: entry point and backend exist --------------------------------------
if [ ! -f "${ENTRYPOINT}" ]; then
    echo "ERROR: benchmark entry point not found: ${ENTRYPOINT}" >&2
    exit 1
fi
if [ ! -f "${BACKEND_DIR}/app/ai/rule_engine.py" ]; then
    echo "ERROR: rule engine not found: ${BACKEND_DIR}/app/ai/rule_engine.py" >&2
    exit 1
fi

# --- 4. run the benchmark ---------------------------------------------------------
# PYTHONPATH makes `from app.ai.rule_engine import RuleEngine` resolve against
# the repository's backend/ directory.
export PYTHONPATH="${BACKEND_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

cd "${EVAL_DIR}"
echo "Running benchmark.py (stratified 5-fold CV, random_state=42)..."
python3 "${ENTRYPOINT}"
echo "Done. Results written under ${EVAL_DIR}/"

#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${PYTHON_BIN:-}" ]]; then
  # shellcheck disable=SC2206
  PYTHON_CMD=(${PYTHON_BIN})
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=("python")
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=("python3")
elif command -v py >/dev/null 2>&1; then
  PYTHON_CMD=("py" "-3")
else
  echo "Python interpreter not found on PATH." >&2
  exit 1
fi

run_guard() {
  local name=$1
  shift
  echo "Running ${name}..."
  if ! "$@"; then
    echo "${name} failed." >&2
    exit 1
  fi
}

run_guard "Invariant checks" "${PYTHON_CMD[@]}" tools/ci_guard.py invariants
run_guard "Qt resource verification" "${PYTHON_CMD[@]}" tools/ci_guard.py resources
run_guard "Radon complexity gate" "${PYTHON_CMD[@]}" tools/ci_guard.py radon
run_guard "Doctests" "${PYTHON_CMD[@]}" -m pytest core/domain/parsing.py --doctest-modules

run_guard "Collecting coverage metrics" bash -c 'QT_QPA_PLATFORM=offscreen "'"${PYTHON_CMD[@]}"'" -m coverage run -m pytest'
run_guard "Coverage report" "${PYTHON_CMD[@]}" -m coverage report --fail-under=78
run_guard "Coverage XML" "${PYTHON_CMD[@]}" -m coverage xml
run_guard "Module coverage gates" "${PYTHON_CMD[@]}" tools/ci_guard.py coverage

if "${PYTHON_CMD[@]}" - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec("diff_cover") else 1)
PY
then
  run_guard "Diff coverage" "${PYTHON_CMD[@]}" -m diff_cover coverage.xml --fail-under 85
else
  echo "Diff cover not installed; skipping diff coverage step"
fi

run_guard "Ruff lint" "${PYTHON_CMD[@]}" -m ruff check .
run_guard "mypy strict" "${PYTHON_CMD[@]}" -m mypy --strict core adapters services

if command -v openspec >/dev/null 2>&1; then
  echo "Validating OpenSpec specifications..."
  openspec validate refactor-phase5-ai-port --strict || echo "OpenSpec validation skipped: refactor-phase5-ai-port not found."
else
  echo "Skipping OpenSpec validation (openspec CLI not found)..."
fi

echo "All checks passed"

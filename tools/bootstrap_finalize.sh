#!/usr/bin/env bash
set -euo pipefail

section() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()      { printf "\033[0;32m[ok]\033[0m %s\n" "$*"; }
warn()    { printf "\033[0;33m[warn]\033[0m %s\n" "$*"; }
info()    { printf "\033[0;34m[i]\033[0m %s\n" "$*"; }

PY="python3"
PIP="python3 -m pip"

section "Bootstrap Python environment"
if ! command -v python3 >/dev/null 2>&1; then
  echo "[err] python3 not found in PATH"; exit 1
fi
$PIP --version >/dev/null 2>&1 || ($PY -m ensurepip --upgrade || true)
$PIP install --break-system-packages --upgrade pip wheel setuptools

if [[ -f requirements-dev.txt ]]; then
  info "requirements-dev.txt found → installing"
  $PIP install --break-system-packages -r requirements-dev.txt
elif [[ -f requirements.txt ]]; then
  info "requirements-dev.txt not found, using requirements.txt"
  $PIP install --break-system-packages -r requirements.txt
else
  info "requirements-dev.txt not found → installing minimal toolchain"
  $PIP install --break-system-packages coverage pytest ruff mypy || true
fi

if ! command -v openspec >/dev/null 2>&1; then
  warn "openspec CLI not found → attempting optional install"
  $PIP install --break-system-packages openspec-cli || warn "openspec optional install failed (continuing)"
fi

section "Verify tool availability"
$PY --version
$PY -m pip show coverage pytest ruff mypy || true
openspec --version || true

section "Run finalize flow"
chmod +x tools/check.sh tools/finalize.sh || true
./tools/finalize.sh || { echo "[err] finalize.sh failed"; exit 1; }

section "Audit snapshot"
git --version || true
git status --porcelain || true
git tag -l 'refactor-phase1-stabilization*' || true

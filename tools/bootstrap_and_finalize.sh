#!/usr/bin/env bash
set -euo pipefail

section() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()      { printf "\033[0;32m[ok]\033[0m %s\n" "$*"; }
warn()    { printf "\033[0;33m[warn]\033[0m %s\n" "$*"; }
info()    { printf "\033[0;34m[i]\033[0m %s\n" "$*"; }

# --- 0) Create local venv (.venv) and use it ---------------------------------
section "Python venv bootstrap (.venv)"
PY="python3"
if ! command -v python3 >/dev/null 2>&1; then
  echo "[err] python3 not found in PATH"; exit 1
fi
if [[ ! -d .venv ]]; then
  $PY -m venv .venv
  ok "Created .venv"
fi

if [[ -x .venv/bin/python ]]; then
  PY=".venv/bin/python"
elif [[ -x .venv/Scripts/python ]]; then
  PY=".venv/Scripts/python"
elif [[ -x .venv/Scripts/python.exe ]]; then
  PY=".venv/Scripts/python.exe"
else
  echo "[err] Could not find Python executable in .venv"; exit 1
fi
VENV_BIN=$(dirname "$PY")
export PATH="$VENV_BIN:$PATH"
PIP="$PY -m pip"

$PIP --version >/dev/null 2>&1 || ($PY -m ensurepip --upgrade || true)
$PIP install --upgrade pip wheel setuptools

# --- 1) Dev toolchain ---------------------------------------------------------
section "Install dev toolchain"
if [[ -f requirements-dev.txt ]]; then
  info "requirements-dev.txt found → installing"
  $PIP install -r requirements-dev.txt
else
  info "requirements-dev.txt not found → installing minimal toolchain"
  $PIP install "coverage>=7.6" "pytest>=7.4" "ruff>=0.5" "mypy>=1.8"
fi

# Optional: OpenSpec CLI
if ! command -v openspec >/dev/null 2>&1; then
  warn "openspec CLI not found → attempting optional install"
  $PIP install openspec-cli || warn "openspec optional install failed (continuing)"
fi

# --- 2) Verify tools ----------------------------------------------------------
section "Verify tool availability"
$PY --version
$PIP show coverage pytest ruff mypy | sed 's/^Name: /-- /' || true
openspec --version || true

# --- 3) Run finalize flow w/ audit log ---------------------------------------
section "Run finalize.sh (with audit log)"
mkdir -p .openspec
ts=$(date +%Y%m%d_%H%M%S)
LOG=".openspec/finalize-${ts}.log"

chmod +x tools/check.sh tools/finalize.sh || true
# Capture both finalize output AND a quick env snapshot into the same log
{
  echo "# Environment snapshot";
  which $PY || true;
  $PY -m pip freeze || true;
  echo;
  echo "# Finalize flow";
  ./tools/finalize.sh
} 2>&1 | tee "$LOG"

ok "Audit log saved to: $LOG"

# --- 4) Optional stricter OpenSpec check if CLI present -----------------------
if command -v openspec >/dev/null 2>&1; then
  section "OpenSpec validate (strict, hard-fail)"
  openspec validate --strict | tee -a "$LOG"
  ok "OpenSpec validate passed"
else
  warn "openspec CLI not found; validation deferred"
fi

# --- 5) Exit summary ----------------------------------------------------------
section "Summary"
echo "Finalize log: $LOG"
ok "Bootstrap + Finalization completed"

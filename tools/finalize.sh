#!/usr/bin/env bash
set -euo pipefail

CHANGE_ID="refactor-phase1-stabilization"
TAG_NAME="refactor-phase1-stabilization-done"

section() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
info()    { printf "\033[0;34m[i]\033[0m %s\n" "$*"; }
ok()      { printf "\033[0;32m[ok]\033[0m %s\n" "$*"; }
warn()    { printf "\033[0;33m[warn]\033[0m %s\n" "$*"; }
err()     { printf "\033[0;31m[err]\033[0m %s\n" "$*"; }

# 0) Preflight
section "Preflight"
if [[ ! -f tools/check.sh ]]; then
  err "Missing tools/check.sh"; exit 1
fi
chmod +x tools/check.sh || true
ok "tools/check.sh is executable"

# 1) Quality Gate (unified)
section "Quality Gate"
./tools/check.sh
ok "Quality gate passed (tools/check.sh)"

# 2) OpenSpec finalize + validate (if CLI available)
section "OpenSpec Finalization"
if command -v openspec >/dev/null 2>&1; then
  info "openspec CLI detected"
  openspec finalize "$CHANGE_ID"
  ok "openspec finalize $CHANGE_ID done"

  section "OpenSpec Validate (strict)"
  openspec validate --strict
  ok "openspec validate --strict passed"
else
  warn "openspec CLI not found in PATH. Skipping finalize/validate."
  warn "Run later when CLI is available: "
  printf "  openspec finalize %s\n  openspec validate --strict\n" "$CHANGE_ID"
fi

# 3) Git: init/commit/tag/push (optional, only if inside repo OR user wants it)
section "Git Commit/Tag"
if command -v git >/dev/null 2>&1; then
  if git rev-parse --git-dir >/dev/null 2>&1; then
    info "Git repository detected"
  else
    warn "No git repo found. Initializing a new one..."
    git init
    git branch -M main || true
  fi

  # Ensure .gitignore exists minimally
  if [[ ! -f .gitignore ]]; then
    cat <<'EOF' > .gitignore
__pycache__/
*.pyc
.coverage
htmlcov/
.env
.venv/
EOF
    info "Created minimal .gitignore"
  fi

  git add -A
  COMMIT_MSG="Finalize ${CHANGE_ID}: quality gate pass, docs aligned (PyQt6+QSettings), Purpose sections, CHANGELOG 0.0.1"
  if git diff --cached --quiet; then
    info "No staged changes to commit"
  else
    git commit -m "$COMMIT_MSG"
    ok "Committed changes"
  fi

  if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    info "Tag ${TAG_NAME} already exists"
  else
    git tag -a "$TAG_NAME" -m "Stabilization phase 1 finalized"
    ok "Created tag ${TAG_NAME}"
  fi

  if git remote get-url origin >/dev/null 2>&1; then
    git push origin HEAD --tags
    ok "Pushed branch and tags to origin"
  else
    warn "No git remote configured. Skipping push."
  fi
else
  warn "git not found. Skipping commit/tag/push."
fi

section "Done"
ok "Finalization flow completed. If OpenSpec CLI was missing, re-run the finalize/validate commands later."

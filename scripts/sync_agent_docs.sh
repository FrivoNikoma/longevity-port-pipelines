#!/usr/bin/env bash
# Keeps CLAUDE.md in sync with the canonical AGENTS.md.
# Preferred: CLAUDE.md is a symlink. If the platform turned it into a real file
# (Windows checkout, zip export), this restores the symlink so they can't drift.
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$0")/.."

if [ ! -f AGENTS.md ]; then
  echo "AGENTS.md missing — it is canonical, cannot sync." >&2
  exit 1
fi

# If CLAUDE.md isn't already a symlink pointing at AGENTS.md, (re)create it.
if [ ! -L CLAUDE.md ] || [ "$(readlink CLAUDE.md)" != "AGENTS.md" ]; then
  rm -f CLAUDE.md
  ln -s AGENTS.md CLAUDE.md
  echo "Restored CLAUDE.md -> AGENTS.md symlink."
fi

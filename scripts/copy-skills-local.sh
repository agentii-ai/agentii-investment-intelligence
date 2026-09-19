#!/usr/bin/env bash
# copy-skills-local.sh
# Copies ALL skills (every vertical) into the target project's .claude/skills/agentii/.
#
# Workaround for Claude Code v2.1.143 plugin bug (GitHub issue #15178):
# Skills installed via 'claude plugin install' may not be injected into the runtime.
# Copying skills into .claude/skills/ bypasses the plugin registration system.
#
# Usage: bash scripts/copy-skills-local.sh [target-dir]
#   target-dir: Optional project root (defaults to current directory)
#
# Feature: 023 — Plugin bug workaround (FR-014b)
# Fixed 2026-09-10 (spec 046 dogfooding feedback): the previous version hardcoded
# 5 verticals and copied only SKILL.md — silently skipping 9 verticals (including
# the scenarios kit skills) and dropping every references/ methodology directory.
# Now: ALL verticals, FULL skill directory (SKILL.md + references/), idempotent.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Usage: copy-skills-local.sh [target-dir] [--dry-run]
#
# `--dry-run` reports what WOULD change and writes nothing. It exists because the
# prune below is the first step of this script that REMOVES something from the
# destination, and a removal nobody can preview is a removal nobody reviews.
DRY_RUN=0
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -*) echo "unknown option: $arg"; exit 2 ;;
    *) TARGET="$arg" ;;
  esac
done
TARGET="${TARGET:-.}"

if [[ ! -d "$TARGET" ]]; then
  echo "❌ Target directory '$TARGET' does not exist"
  exit 1
fi

SKILLS_SRC="$REPO_ROOT/plugins"
SKILLS_DST="$TARGET/.claude/skills/agentii"
COMMANDS_DST="$TARGET/.claude/commands/agentii"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "── DRY RUN — nothing will be written ──"
fi

mkdir -p "$SKILLS_DST" "$COMMANDS_DST"

TOTAL=0
SKIPPED=0
REMOVED=0

# The source inventory, written to a temp file rather than held in an array.
# macOS ships bash 3.2, where `"${arr[@]}"` under `set -u` raises "unbound variable"
# on an EMPTY array — so the array form works here only because the repo happens to
# have 80 skills, and would break on the day it has none. A file has no such edge.
SRC_NAMES_FILE="$(mktemp)"
SRC_COMMANDS_FILE="$(mktemp)"
trap 'rm -f "$SRC_NAMES_FILE" "$SRC_COMMANDS_FILE"' EXIT
REF_COUNT=0

# ALL verticals — discovered, never hardcoded (the 2026-09-10 fix)
for SRC_DIR in "$SKILLS_SRC"/vertical-plugins/*/skills/agentii; do
  [[ -d "$SRC_DIR" ]] || continue
  vertical="$(basename "$(dirname "$(dirname "$SRC_DIR")")")"

  for skill_dir in "$SRC_DIR"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    SKILL_FILE="$skill_dir/SKILL.md"

    # Validate SKILL.md before copying (I6 fix)
    if [[ ! -f "$SKILL_FILE" ]]; then
      echo "⚠️  Skipping $skill_name: no SKILL.md found"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    if ! grep -q "^---$" "$SKILL_FILE" 2>/dev/null; then
      echo "⚠️  Skipping $skill_name: missing YAML frontmatter"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    if ! grep -q "^name:" "$SKILL_FILE" 2>/dev/null; then
      echo "⚠️  Skipping $skill_name: missing 'name' field in frontmatter"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi

    DST_DIR="$SKILLS_DST/$skill_name"
    echo "$skill_name" >> "$SRC_NAMES_FILE"
    if [[ "$DRY_RUN" == "1" ]]; then
      TOTAL=$((TOTAL + 1))
      continue
    fi
    # FULL skill directory — references/ carries the deep methodology (2026-09-10 fix)
    rm -rf "$DST_DIR"
    cp -R "$skill_dir" "$DST_DIR"
    TOTAL=$((TOTAL + 1))
    REF_COUNT=$((REF_COUNT + $(find "$DST_DIR" -path "*/references/*" -type f | wc -l | tr -d ' ')))
  done

  # Commands into the agentii-namespaced subdir — /agentii:<name> (unified namespace)
  COMMANDS_SRC="$(dirname "$(dirname "$SRC_DIR")")/commands"
  if [[ -d "$COMMANDS_SRC" && "$DRY_RUN" != "1" ]]; then
    cp "$COMMANDS_SRC"/*.md "$COMMANDS_DST/" 2>/dev/null || true
  fi
  if [[ -d "$COMMANDS_SRC" ]]; then
    for c in "$COMMANDS_SRC"/*.md; do
      [[ -f "$c" ]] && basename "$c" >> "$SRC_COMMANDS_FILE"
    done
  fi
done

# ── Prune — the half this script never had ──────────────────────────────────
#
# Until 2026-09-19 the copy loop only ever `rm -rf`'d the destination directory of
# a skill that STILL EXISTS in the source. A skill renamed or split upstream was
# therefore never removed downstream, and re-running the installer (the documented
# upgrade path) could not fix it. Measured consequence: two skills that had been
# split into six — `fda-catalyst-analysis` and `pipeline-analysis` — survived in
# `~/.claude/skills/agentii/` indefinitely, so the install reported 82 entries while
# the repo held 80. Nothing said so; the script printed `skipped: 0` either way.
#
# It prints every removed NAME, not a count. A count is what let the drift go
# unnoticed: `skipped: 0` was true and told the reader nothing about the 2 extras.
for dst in "$SKILLS_DST"/*/; do
  [[ -d "$dst" ]] || continue
  name="$(basename "$dst")"
  if ! grep -qxF "$name" "$SRC_NAMES_FILE"; then
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "  would remove (no upstream source): $name"
    else
      rm -rf "$dst"
      echo "  removed (no upstream source): $name"
    fi
    REMOVED=$((REMOVED + 1))
  fi
done

# The same half for commands. `cp` never removed anything either, so a deleted
# command file kept resolving to a skill that no longer exists.
if [[ "$DRY_RUN" != "1" ]]; then
  for c in "$COMMANDS_DST"/*.md; do
    [[ -f "$c" ]] || continue
    cname="$(basename "$c")"
    if ! grep -qxF "$cname" "$SRC_COMMANDS_FILE"; then
      rm -f "$c"
      echo "  removed command (no upstream source): $cname"
      REMOVED=$((REMOVED + 1))
    fi
  done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Copied $TOTAL skills (all verticals) to $SKILLS_DST"
echo "   references/ files staged: $REF_COUNT"
echo "   skipped: $SKIPPED"
echo "   removed (no upstream source): $REMOVED"
echo "   Commands namespaced under $COMMANDS_DST"
echo "   Single unified namespace: /agentii:<skill-name>"
echo "   Type / in Claude Code to see the auto-complete menu"
echo ""
echo "   Restart Claude Code for changes to take effect."
echo ""
echo "   🔗 GitHub issue: https://github.com/anthropics/claude-code/issues/15178"
echo "   (Remove .claude/skills/agentii/ after upgrading Claude Code to a fixed version)"

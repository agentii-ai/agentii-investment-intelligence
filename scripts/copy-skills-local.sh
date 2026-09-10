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
TARGET="${1:-.}"

if [[ ! -d "$TARGET" ]]; then
  echo "❌ Target directory '$TARGET' does not exist"
  exit 1
fi

SKILLS_SRC="$REPO_ROOT/plugins"
SKILLS_DST="$TARGET/.claude/skills/agentii"
COMMANDS_DST="$TARGET/.claude/commands/agentii"

mkdir -p "$SKILLS_DST" "$COMMANDS_DST"

TOTAL=0
SKIPPED=0
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
    # FULL skill directory — references/ carries the deep methodology (2026-09-10 fix)
    rm -rf "$DST_DIR"
    cp -R "$skill_dir" "$DST_DIR"
    TOTAL=$((TOTAL + 1))
    REF_COUNT=$((REF_COUNT + $(find "$DST_DIR" -path "*/references/*" -type f | wc -l | tr -d ' ')))
  done

  # Commands into the agentii-namespaced subdir — /agentii:<name> (unified namespace)
  COMMANDS_SRC="$(dirname "$(dirname "$SRC_DIR")")/commands"
  if [[ -d "$COMMANDS_SRC" ]]; then
    cp "$COMMANDS_SRC"/*.md "$COMMANDS_DST/" 2>/dev/null || true
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Copied $TOTAL skills (all verticals) to $SKILLS_DST"
echo "   references/ files staged: $REF_COUNT"
echo "   skipped: $SKIPPED"
echo "   Commands namespaced under $COMMANDS_DST"
echo "   Single unified namespace: /agentii:<skill-name>"
echo "   Type / in Claude Code to see the auto-complete menu"
echo ""
echo "   Restart Claude Code for changes to take effect."
echo ""
echo "   🔗 GitHub issue: https://github.com/anthropics/claude-code/issues/15178"
echo "   (Remove .claude/skills/agentii/ after upgrading Claude Code to a fixed version)"

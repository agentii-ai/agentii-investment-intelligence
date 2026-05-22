#!/usr/bin/env bash
# copy-skills-local.sh
# Copies skills/agentii/ contents into the current project's .claude/skills/agentii/ directory.
#
# Workaround for Claude Code v2.1.143 plugin bug (GitHub issue #15178):
# Skills installed via 'claude plugin install' may not be injected into the runtime.
# Copying skills into .claude/skills/ bypasses the plugin registration system.
#
# Usage: bash scripts/copy-skills-local.sh [target-dir]
#   target-dir: Optional project root (defaults to current directory)
#
# Feature: 023 — Plugin bug workaround (FR-014b)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-.}"

if [[ ! -d "$TARGET" ]]; then
  echo "❌ Target directory '$TARGET' does not exist"
  exit 1
fi

SKILLS_SRC="$REPO_ROOT/plugins"
SKILLS_DST="$TARGET/.claude/skills/agentii"

mkdir -p "$SKILLS_DST"

TOTAL=0
VERTICALS=(
  "equity-research-core"
  "business-intelligence"
  "industry-analysis"
  "models-and-pitches"
)

for vertical in "${VERTICALS[@]}"; do
  SRC_DIR="$SKILLS_SRC/vertical-plugins/$vertical/skills/agentii"
  if [[ -d "$SRC_DIR" ]]; then
    for skill_dir in "$SRC_DIR"/*/; do
      [[ -d "$skill_dir" ]] || continue
      skill_name="$(basename "$skill_dir")"
      SKILL_FILE="$skill_dir/SKILL.md"

      # Validate SKILL.md before copying (I6 fix)
      if [[ ! -f "$SKILL_FILE" ]]; then
        echo "⚠️  Skipping $skill_name: no SKILL.md found"
        continue
      fi
      if ! grep -q "^---$" "$SKILL_FILE" 2>/dev/null; then
        echo "⚠️  Skipping $skill_name: missing YAML frontmatter"
        continue
      fi
      if ! grep -q "^name:" "$SKILL_FILE" 2>/dev/null; then
        echo "⚠️  Skipping $skill_name: missing 'name' field in frontmatter"
        continue
      fi
      # Warn if description has fewer than 5 trigger phrases
      desc_line=$(grep "^description:" "$SKILL_FILE" 2>/dev/null | head -1)
      trigger_count=$(echo "$desc_line" | tr ',' '\n' | wc -l | xargs)
      if [[ "$trigger_count" -lt 5 ]]; then
        echo "⚠️  $skill_name: only $trigger_count trigger phrases (recommend ≥10)"
      fi

      DST_DIR="$SKILLS_DST/$skill_name"
      mkdir -p "$DST_DIR"
      cp "$SKILL_FILE" "$DST_DIR/SKILL.md" && {
        TOTAL=$((TOTAL + 1))
      } || true
    done
  fi

  # Also copy commands/ for backward compatibility
  COMMANDS_SRC="$SKILLS_SRC/vertical-plugins/$vertical/commands"
  COMMANDS_DST="$TARGET/.claude/commands"
  if [[ -d "$COMMANDS_SRC" ]]; then
    mkdir -p "$COMMANDS_DST"
    cp "$COMMANDS_SRC"/*.md "$COMMANDS_DST/" 2>/dev/null || true
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Copied $TOTAL skills to $SKILLS_DST"
echo "   Namespace: /agentii:<skill-name>"
echo "   Type / in Claude Code to see the auto-complete menu"
echo ""
echo "   Restart Claude Code for changes to take effect."
echo ""
echo "   🔗 GitHub issue: https://github.com/anthropics/claude-code/issues/15178"
echo "   (Remove .claude/skills/agentii/ after upgrading Claude Code to a fixed version)"

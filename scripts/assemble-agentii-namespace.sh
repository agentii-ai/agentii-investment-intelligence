#!/usr/bin/env bash
# assemble-agentii-namespace.sh — Collate vertical skills into unified agentii meta-plugin
# Phase 23 — FR-014d, FR-014h
# Compatible with bash 3.2+ (macOS default)
#
# Steps:
#   1. Enumerate all vertical skills/agentii/<name>/SKILL.md across 5 verticals
#   2. Validate each has ## Output File, ## Output Structure, ## Error Handling
#   3. Check for name collisions across verticals (fail CI if found)
#   4. Symlink each skills/agentii/<name>/ into plugins/agentii-plugin/skills/agentii/
#   5. Verify flat namespace integrity

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
META_SKILLS_DIR="${REPO_ROOT}/plugins/agentii-plugin/skills/agentii"
VERTICALS="equity-research-core business-intelligence industry-analysis models-and-pitches quantitative-analysis"
TMPFILE="$(mktemp)"
trap "rm -f $TMPFILE" EXIT

echo "=== agentii namespace assembly ==="

# Step 1: Enumerate all vertical skills into a flat list
echo "--- Enumerating skills ---"
count=0
for vertical in $VERTICALS; do
  vertical_skills_dir="${REPO_ROOT}/plugins/vertical-plugins/${vertical}/skills/agentii"
  if [ ! -d "$vertical_skills_dir" ]; then
    echo "WARNING: ${vertical}/skills/agentii/ not found, skipping."
    continue
  fi
  for skill_dir in "$vertical_skills_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    skill_file="${skill_dir}SKILL.md"
    if [ ! -f "$skill_file" ]; then
      continue
    fi
    # Check for collisions
    existing="$(grep "^${skill_name} " "$TMPFILE" 2>/dev/null || true)"
    if [ -n "$existing" ]; then
      other_vert="$(echo "$existing" | awk '{print $2}')"
      echo "ERROR: Name collision: '$skill_name' exists in both '$other_vert' and '$vertical'"
      exit 1
    fi
    echo "${skill_name} ${vertical}" >> "$TMPFILE"
    count=$((count + 1))
  done
done

echo "Found $count skills across 5 verticals."

# Step 2: Validate each skill
echo "--- Validating skills ---"
errors=0
while IFS=' ' read -r skill_name vertical; do
  skill_file="${REPO_ROOT}/plugins/vertical-plugins/${vertical}/skills/agentii/${skill_name}/SKILL.md"

  # Check ## Output File presence
  if ! grep -q "^## Output File" "$skill_file"; then
    echo "ERROR: $skill_name ($vertical) missing ## Output File section"
    errors=$((errors + 1))
  fi

  # Check ## Output Structure has content
  structure_lines="$(sed -n '/^## Output Structure$/,/^## /p' "$skill_file" | sed '1d;$d' | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "$structure_lines" -lt 3 ]; then
    echo "ERROR: $skill_name ($vertical) Output Structure has $structure_lines lines (need ≥3)"
    errors=$((errors + 1))
  fi

  # Check ## Error Handling presence
  if ! grep -q "^## Error Handling" "$skill_file"; then
    echo "ERROR: $skill_name ($vertical) missing ## Error Handling section"
    errors=$((errors + 1))
  fi
done < "$TMPFILE"

if [ "$errors" -gt 0 ]; then
  echo "VALIDATION FAILED: $errors error(s) found."
  exit 1
fi
echo "All $count skills validated."

# Step 4: Symlink into meta-plugin
echo "--- Assembling meta-plugin ---"
rm -rf "$META_SKILLS_DIR"
mkdir -p "$META_SKILLS_DIR"

while IFS=' ' read -r skill_name vertical; do
  src="${REPO_ROOT}/plugins/vertical-plugins/${vertical}/skills/agentii/${skill_name}"
  dst="${META_SKILLS_DIR}/${skill_name}"
  ln -sf "$src" "$dst"
done < "$TMPFILE"
echo "Symlinked $count skills into $META_SKILLS_DIR."

# Step 5: Verify flat namespace
echo "--- Verifying namespace ---"
meta_count="$(ls -1 "$META_SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')"
echo "Meta-plugin skills: $meta_count"
echo "Assembly complete."

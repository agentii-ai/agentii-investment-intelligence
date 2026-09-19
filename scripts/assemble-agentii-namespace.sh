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
# ALL 14 verticals — and note the count, because this list has been wrong twice.
#
# spec 039 US6 (T077) fixed a hardcoded list of 5: 3 pre-existing verticals
# (macro-strategy, options-derivatives, portfolio-strategy) had never been assembled.
# The fix enumerated 13 and its own comment said "all 12" — while the disk held 14.
# **`scenarios` was absent**, so the 10 spec-046 kit skills never reached the
# meta-plugin: `agentii-plugin/skills/agentii/` carried 70 symlinks against 80 skills.
#
# The omission was invisible for the same reason the orphan directories were: every
# count in this repository was self-consistent about 70, and nothing compared the
# list against the disk. `check.py` Check 50 now fails on a namespace directory with
# no SKILL.md; this list is checked by the count in the summary line below.
VERTICALS="equity-research-core business-intelligence industry-analysis models-and-pitches quantitative-analysis macro-strategy options-derivatives portfolio-strategy idea-generation risk-and-psychology trading-as-business technical-analysis bio-pharm scenarios"
# Naming convention (spec 052): same-name sector adaptations use {base}-{sector}
# suffixes (e.g., earnings-preview-med), so the meta namespace stays collision-free.
TMPFILE="$(mktemp)"
TMP_CMDS="$(mktemp)"
trap "rm -f $TMPFILE $TMP_CMDS" EXIT

echo "=== agentii namespace assembly ==="

# Step 1: Enumerate all vertical skills into a flat list
echo "--- Enumerating skills ---"
count=0
vert_count=0
for vertical in $VERTICALS; do
  vertical_skills_dir="${REPO_ROOT}/plugins/vertical-plugins/${vertical}/skills/agentii"
  if [ ! -d "$vertical_skills_dir" ]; then
    echo "WARNING: ${vertical}/skills/agentii/ not found, skipping."
    continue
  fi
  vert_count=$((vert_count + 1))
  for skill_dir in "$vertical_skills_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    skill_file="${skill_dir}SKILL.md"
    if [ ! -f "$skill_file" ]; then
      continue
    fi
    # Check for collisions (strict — {base}-{sector} naming keeps it collision-free)
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

echo "Found $count skills across $vert_count verticals."

# Step 2: Validate each skill
echo "--- Validating skills ---"
# Role-aware, and this is the reason `scenarios` was absent from VERTICALS.
#
# These three checks are TICKER-ANALYSIS checks: a sourcing skill emits output files,
# structures them, and handles its own errors. The 10 `scenarios` skills are
# workspace META-commands — they operate on specs, tasks and theses, and emit no
# ticker artifact — so they legitimately have no `## Output File`. Applied
# unconditionally, these checks fail all 10, and the only way to get a green
# assembly was to leave the vertical out of the list.
#
# So the omission was never an oversight; it was the validator's blind spot being
# worked around by hand. `check.py` already solved this properly — `_meta_role()`
# reads `role: kit|orchestrator` from the frontmatter and excludes those bodies from
# the analysis-only checks (Q25: three body types, three validators). This mirrors it.
#
# The role is read, never inferred, and only from frontmatter — so a skill cannot
# slip past by lacking the marker.
errors=0
meta_skipped=0
while IFS=' ' read -r skill_name vertical; do
  skill_file="${REPO_ROOT}/plugins/vertical-plugins/${vertical}/skills/agentii/${skill_name}/SKILL.md"

  # Q25 role dispatch: kit / orchestrator bodies are meta-commands, not analyses.
  role="$(sed -n '1,/^---$/p' "$skill_file" 2>/dev/null | awk 'NR>1 && /^---$/{exit} /^role:/{sub(/^role:[[:space:]]*/,""); print; exit}')"
  case "$role" in
    kit|orchestrator)
      meta_skipped=$((meta_skipped + 1))
      continue ;;
  esac

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
if [ "$meta_skipped" -gt 0 ]; then
  echo "  ($meta_skipped meta-command(s) skipped — role: kit/orchestrator, Q25)"
fi

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
  dst="${META_SKILLS_DIR}/${skill_name}"
  # Relative symlink so the namespace dir stays portable when copied/published
  # (absolute targets break on other machines). dst lives at
  # plugins/agentii-plugin/skills/agentii/<name> → ../../../ reaches plugins/.
  rel="../../../vertical-plugins/${vertical}/skills/agentii/${skill_name}"
  ln -sf "$rel" "$dst"
done < "$TMPFILE"
echo "Symlinked $count skills into $META_SKILLS_DIR."

# Step 4b: Commands into the meta-plugin — the half that was never assembled.
#
# Until 2026-09-20 this script symlinked 80 skills and carried ZERO commands, so
# `plugins/agentii-plugin/` had no `commands/` directory at all. A clean
# `claude plugin install agentii` therefore yielded the entire skill namespace and not
# one slash command: `/agentii:specify` and `/agentii:synthesize` resolved only for a
# user who had ALSO run `copy-skills-local.sh`, which stages them at
# `.claude/commands/agentii/` by an entirely different route. Two install channels, one
# of which silently shipped half the product.
#
# The omission was invisible for the same reason the missing vertical was: nothing
# compared the assembled plugin against the disk. Step 5 below performs exactly that
# comparison for skills; this extends it to commands.
META_COMMANDS_DIR="${REPO_ROOT}/plugins/agentii-plugin/commands"
rm -rf "$META_COMMANDS_DIR"
mkdir -p "$META_COMMANDS_DIR"

cmd_count=0
for c in "${REPO_ROOT}"/plugins/vertical-plugins/*/commands/*.md; do
  [ -f "$c" ] || continue
  cname="$(basename "$c")"
  cvert="$(echo "$c" | sed -e "s|^${REPO_ROOT}/plugins/vertical-plugins/||" -e 's|/commands/.*||')"
  # The destination is FLAT, so two verticals declaring the same basename would be a
  # silent overwrite — whichever is walked last wins, and nothing would report it.
  # Check 50 guards the skill half of this hazard; the same hazard lives here.
  if grep -qxF "$cname" "$TMP_CMDS"; then
    echo "ERROR: duplicate command name '$cname' — the meta-plugin commands/ dir is"
    echo "       flat, so one would silently overwrite the other. Rename one."
    exit 1
  fi
  echo "$cname" >> "$TMP_CMDS"
  # Relative symlink, for the same portability reason as the skills above. dst lives at
  # plugins/agentii-plugin/commands/<name> → ../../ reaches plugins/.
  ln -sf "../../vertical-plugins/${cvert}/commands/${cname}" "$META_COMMANDS_DIR/$cname"
  cmd_count=$((cmd_count + 1))
done
echo "Symlinked $cmd_count commands into $META_COMMANDS_DIR."

# Step 5: Verify flat namespace — against the DISK, not against ourselves.
#
# The previous version printed `Meta-plugin skills: $meta_count` and stopped. That
# number is computed FROM the thing being verified, so it is true by construction and
# cannot detect the failure that actually occurred: `scenarios` was missing from
# VERTICALS, so 10 skills were never symlinked, and the line still printed a
# self-consistent 70. A count that agrees with itself is not a check.
#
# The comparison that can fail is list-versus-disk: every vertical on disk must be in
# VERTICALS, and the namespace must hold one link per SKILL.md in those verticals.
echo "--- Verifying namespace ---"
disk_verticals="$(cd "$REPO_ROOT/plugins/vertical-plugins" && ls -1d */ 2>/dev/null | sed 's|/$||' | sort)"
missing_verticals=""
for v in $disk_verticals; do
  case " $VERTICALS " in *" $v "*) ;; *) missing_verticals="$missing_verticals $v" ;; esac
done
disk_skills="$(find "$REPO_ROOT/plugins/vertical-plugins" -path '*/skills/agentii/*/SKILL.md' | wc -l | tr -d ' ')"
meta_count="$(ls -1 "$META_SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')"
disk_cmds="$(find "$REPO_ROOT/plugins/vertical-plugins" -path '*/commands/*.md' | wc -l | tr -d ' ')"
meta_cmd_count="$(ls -1 "$META_COMMANDS_DIR" 2>/dev/null | wc -l | tr -d ' ')"
echo "Meta-plugin skills:   $meta_count (disk holds $disk_skills)"
echo "Meta-plugin commands: $meta_cmd_count (disk holds $disk_cmds)"

if [[ -n "$missing_verticals" ]]; then
  echo "FAIL — vertical(s) on disk but not in VERTICALS:$missing_verticals"
  echo "       their skills are absent from the meta-plugin."
  exit 1
fi
if [[ "$meta_count" != "$disk_skills" ]]; then
  echo "FAIL — meta-plugin holds $meta_count skills, disk holds $disk_skills."
  echo "       A name collision or a missing vertical produces this. Re-run after fixing."
  exit 1
fi
# The command half of the same comparison. Without it the plugin can ship a complete
# skill namespace and no slash commands — which is precisely what it did, for as long as
# it did, while every number in this script agreed with itself.
if [[ "$meta_cmd_count" != "$disk_cmds" ]]; then
  echo "FAIL — meta-plugin holds $meta_cmd_count commands, disk holds $disk_cmds."
  echo "       A duplicate basename or a missing vertical produces this. Re-run after fixing."
  exit 1
fi
echo "Assembly complete — every vertical and command on disk is assembled."

---
name: challenge
description: "Adversarial verification of research theses — cross-run/cross-thesis contradiction via the entity index, pre-mortem (Klarman/Kahneman: assume the loss already happened, reverse the path), inversion (Munger: invert, always invert), and wrong_if falsifiability review. ≈50-finding cap sorted by severity; content-derived finding IDs; incremental scoping with three backstops; lifecycle hooks at pillar-complete / thesis-complete / pre-reduction."
role: kit
market_data_stage: none
---

# agentii.challenge

The buyer-side IC verb: *challenge the thesis*. Not `audit` — that name was taken
three times (audit-xls, quality-audit.yaml, G3) — challenge is the thing that
happens in an investment committee.

## Method bodies (the four angles)

1. **Cross-run contradiction** — the entity index (`reduce_journals.build_entity_index`):
   same `(entity, metric, period)` with different values. Same `retrieved_at` →
   true contradiction; different → suspected restatement. **The validator never
   auto-resolves** — candidates go to the IC agenda.
2. **Pre-mortem** — assume the loss already happened; reconstruct the path
   backwards. Which pillar failed first? What data would have to be wrong?
3. **Inversion** — what would make this thesis a sell? What would the bear's
   best case look like? What would falsify the conviction, not just the claim?
4. **`wrong_if` falsifiability** — is each falsifier mechanically checkable
   (metric + threshold + source)? A prose falsifier is not a falsifier (Q8-4).

## Economics (Q40/Q68)

- Findings: ≈50 cap, severity-sorted; overflow aggregates by category.
- Finding IDs are content-derived (`hash(entity+metric+period+gap_type)`) —
  unchanged re-runs yield byte-identical IDs (eval corpus comparability).
- Scope is **incremental** (artifacts whose pins/`as_of` changed since last run)
  with three backstops: every Nth converge / constitution MINOR-MAJOR / subscription
  change (new subscriptions create new comparison pairs — Q9).
- Lifecycle hooks: pillar-complete (cheap, early) / thesis-complete (final line) /
  pre-reduction (claims entering the portfolio are adversarially verified).
  **Unchallenged claims never enter the knowledge base (Q64).**

## Invocation

```bash
# Resolve the kit root first — contracts/kit-root.md. The kit's scripts do NOT ship
# with the skills, so never assume the CWD is the checkout.
KIT=""
for c in "${AGENTII_KIT_ROOT:-}" \
         "$(cat "$HOME/.claude/skills/agentii/.kit-root" 2>/dev/null)" \
         "${CLAUDE_PLUGIN_ROOT:-}"; do
  [ -n "$c" ] && [ -f "$c/scripts/agentii_cmd.py" ] && { KIT="$c"; break; }
done
if [ -z "$KIT" ]; then d="$PWD"; while [ "$d" != "/" ]; do
  [ -f "$d/scripts/agentii_cmd.py" ] && { KIT="$d"; break; }; d="$(dirname "$d")"; done; fi
[ -n "$KIT" ] || { echo "agentii kit not found — see contracts/kit-root.md" >&2; exit 1; }

python3 "$KIT/scripts/challenge.py" --nth-converge 10
```

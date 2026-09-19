# Kit-root Contract (shared include)

Where an installed skill finds the kit's `scripts/`. Every spec 046 scenario skill
(`challenge`, `clarify`, `constitution`, `converge`, `full-equity-research`,
`implement`, `plan`, `specify`, `synthesize`, `tasks`) executes Python that lives in
the **kit checkout**, and no install channel ships it:

| channel | skills | `scripts/` |
|---|---|---|
| `~/.claude/skills/agentii/` (via `copy-skills-local.sh`) | 80 | **absent** |
| `plugins/agentii-plugin/` (the published meta-plugin) | 80 | **absent** |
| `packaging/targets/claude-code/<skill>/` | 80 | **absent** |
| a git checkout of this repo | 80 | 52 `.py` |

So until 2026-09-20 every one of these skills assumed `CWD` was the checkout root —
`synthesize/SKILL.md` literally opened with `cd agentii-investment-intelligence` — and
**no document said so**. `CLAUDE_PLUGIN_ROOT` appeared zero times in the kit. An
installed skill run from a workspace directory simply failed to find its own tooling,
and the failure looked like a missing file rather than a missing dependency.

## The rule

**Resolve the kit root, then assert the script you need exists.** Never assume the
CWD, and never fall back silently.

### Step 1 — resolve

Run this before the first `scripts/…` invocation in a skill. `KIT` is the answer:

```bash
# --- resolve the agentii kit root (contracts/kit-root.md) ---
KIT=""
for c in "${AGENTII_KIT_ROOT:-}" \
         "$(cat "$HOME/.claude/skills/agentii/.kit-root" 2>/dev/null)" \
         "${CLAUDE_PLUGIN_ROOT:-}"; do
  [ -n "$c" ] && [ -f "$c/scripts/agentii_cmd.py" ] && { KIT="$c"; break; }
done
if [ -z "$KIT" ]; then
  d="$PWD"
  while [ "$d" != "/" ]; do
    [ -f "$d/scripts/agentii_cmd.py" ] && { KIT="$d"; break; }
    d="$(dirname "$d")"
  done
fi
```

In precedence order:

1. **`$AGENTII_KIT_ROOT`** — the explicit override. Set it when the checkout lives
   somewhere unusual, or when several checkouts exist and you need a specific one.
2. **`<skills-dst>/.kit-root`** — the pointer `copy-skills-local.sh` writes at install
   time. One line, an absolute path to the checkout it was installed from.
3. **`$CLAUDE_PLUGIN_ROOT`** — set by Claude Code when a skill runs from a plugin. It
   does not contain `scripts/` today, so this branch normally fails the sentinel; it is
   listed because it is the correct answer *if* the plugin ever ships them.
4. **walk up from `$PWD`** — covers the dogfooding case, where an agent is working
   inside the checkout itself.

`scripts/agentii_cmd.py` is the sentinel: it is the kit's core command module, it is
present in every checkout, and nothing else in the world has that path.

### Step 2 — assert the script you actually need

Resolving the root is not the same as having the tool. A **stale kit copy** satisfies
Step 1 and still lacks your script — this is not hypothetical: the published marketplace
copy sat at 2.2.1 missing 9 scripts, including `render_report.py`.

```bash
[ -f "$KIT/scripts/render_report.py" ] || {
  echo "render_report.py missing from $KIT." >&2
  echo "That checkout is stale — $KIT/scripts/ should hold the current kit." >&2
  exit 1
}
```

Then invoke through the variable, never through a bare relative path:

```bash
python3 "$KIT/scripts/render_report.py" render --thesis "$THESIS" --keep-pdf
```

## If resolution fails — stop, do not improvise

```bash
[ -n "$KIT" ] || {
  echo "agentii kit not found. The kit's scripts do not ship with the skills." >&2
  echo "Fix: clone the kit and record the pointer, then re-run:" >&2
  echo "  git clone <kit-url> ~/agentii-investment-intelligence" >&2
  echo "  bash ~/agentii-investment-intelligence/scripts/copy-skills-local.sh ~" >&2
  echo "Or set AGENTII_KIT_ROOT to an existing checkout." >&2
  exit 1
}
```

**A silent fallback is a defect, not a convenience.** The kit's recurring failure is a
declared mechanism returning empty success — a credential scan that blocks a write while
the caller prints `OK`; a reducer that reports `REDUCED N entries` over a write the
boundary refused; an assembler that printed `OK …/thesis-report.html` for three runs
while serving a file three edits old. A resolver that quietly picks a wrong root
reproduces that class exactly, one layer up. It must fail with the remedy in the message.

## Consequence, stated plainly

**The checkout is a runtime dependency.** `copy-skills-local.sh` records where it is; it
does not copy it. Deleting or moving the checkout breaks every scenario skill until the
installer is re-run or `AGENTII_KIT_ROOT` is set.

That is the accepted trade — the alternative was duplicating ~53 scripts per install,
which drifts silently and cannot be fixed by editing the kit. What makes it safe is that
every failure is loud and names the one-line remedy, never a wrong answer.

## Who writes the pointer

`scripts/copy-skills-local.sh`, at install:

```bash
printf '%s\n' "$REPO_ROOT" > "$SKILLS_DST/.kit-root"
```

It writes the **absolute** path of the checkout it ran from. Re-running the installer
rewrites it, so an upgrade that moves the checkout updates the pointer.

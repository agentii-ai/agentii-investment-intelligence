#!/usr/bin/env python3
"""resolve_template.py — the 5-layer template resolution stack (spec 046 Q31/Q38).

Priority (first hit wins; `wrap` composition applies at the layer that provides it):
  ⓪ workspace/.agentii/orchestration/templates/overrides/{name}.md   (highest — per-fund
     style without forking the repo)
  ① kit templates/overrides/{name}.md            (hard override, wins-and-stop)
  ② presets/<preset-id>/{name}.md                (by .registry priority)
  ③ extensions/<ext-id>/{name}.md                (by .registry priority)
  ④ templates/{name}.md                          (core)

Composition strategies: replace (default) / prepend / append / wrap — `wrap` layers
write `{CORE_TEMPLATE}` where the core body goes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

KIT_TEMPLATES = Path(__file__).resolve().parents[1] / "plugins" / "vertical-plugins" / "scenarios" / "templates"


def _registry_priority(reg_dir: Path, name: str) -> int:
    """Read .registry (a list of preset/ext ids, highest priority first)."""
    reg_file = reg_dir / ".registry"
    if not reg_file.is_file():
        return 1_000_000
    try:
        data = yaml.safe_load(reg_file.read_text(encoding="utf-8")) or []
        ids = data if isinstance(data, list) else data.get("priority", [])
        return ids.index(name) if name in ids else 1_000_000
    except (OSError, yaml.YAMLError):
        return 1_000_000


def _find_in_dir(directory: Path, name: str) -> Path | None:
    cand = directory / name
    return cand if cand.is_file() else None


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip("\n")
    return text


def _compose(strategy: str, layer_text: str, base_text: str) -> str:
    layer_body = _strip_frontmatter(layer_text)
    if strategy == "prepend":
        return layer_body + "\n" + base_text
    if strategy == "append":
        return base_text + "\n" + layer_body
    if strategy == "wrap":
        if "{CORE_TEMPLATE}" not in layer_body:
            raise ValueError("wrap strategy requires a {CORE_TEMPLATE} placeholder in the layer")
        return layer_body.replace("{CORE_TEMPLATE}", base_text)
    return layer_body  # replace


def resolve(name: str, *, workspace_root: Path | None = None,
            kit_templates: Path = KIT_TEMPLATES) -> tuple[str, list[Path]]:
    """Returns (resolved_text, chain_of_paths_used). Raises FileNotFoundError when
    the template does not resolve at any layer."""
    chain: list[Path] = []
    # ⓪ workspace overrides — highest priority (Q38)
    if workspace_root is not None:
        ws = workspace_root / ".agentii" / "orchestration" / "templates" / "overrides"
        p = _find_in_dir(ws, name)
        if p:
            chain.append(p)
    # ① kit hard overrides
    p = _find_in_dir(kit_templates / "overrides", name)
    if p:
        chain.append(p)
    # ② presets by .registry priority (lowest index = highest priority)
    if (kit_templates / "presets").is_dir():
        ordered = sorted((kit_templates / "presets").iterdir(),
                         key=lambda d: _registry_priority(d.parent, d.name))
        for preset_dir in ordered:
            p = _find_in_dir(preset_dir, name)
            if p:
                chain.append(p)
    # Strategy comes from the FIRST (highest) layer found, or 'replace' — read
    # AFTER all layers are collected (the first layer may be a preset).
    # Layer convention: an optional YAML frontmatter block carrying `_strategy`.
    strategy_file = chain[0] if chain else None
    strategy = "replace"
    if strategy_file is not None:
        try:
            text = strategy_file.read_text(encoding="utf-8")
            if text.startswith("---"):
                _, fm, _ = text.split("---", 2)
                strategy = (yaml.safe_load(fm) or {}).get("_strategy", "replace")
            else:
                meta = yaml.safe_load(text)
                if isinstance(meta, dict):
                    strategy = meta.get("_strategy", "replace")
        except (OSError, ValueError, yaml.YAMLError):
            strategy = "replace"
    # ④ core
    core = _find_in_dir(kit_templates, name)
    if core is None:
        raise FileNotFoundError(f"template '{name}' not found at any layer under {kit_templates}")
    chain.append(core)
    # Compose: fold layers from lowest priority to highest onto the core.
    text = core.read_text(encoding="utf-8")
    for layer in reversed(chain[:-1]):
        text = _compose(strategy, layer.read_text(encoding="utf-8"), text)
    return text, chain


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="5-layer template resolver (Q31/Q38)")
    p.add_argument("--name", required=True, help="template filename, e.g. plan-template.md")
    p.add_argument("--workspace", default=None, help="workspace root for the ⓪ layer")
    p.add_argument("--out", default=None, help="write resolved text to a file")
    args = p.parse_args(argv)
    text, chain = resolve(args.name, workspace_root=Path(args.workspace) if args.workspace else None)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    print(f"# resolved via: {' → '.join(str(c) for c in chain)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""JSON/YAML instance validation against a JSON Schema.

Ported from anthropics/financial-services/scripts/validate.py (Apache 2.0).

Usage: validate.py <instance.json|yaml> <schema.json|yaml>
Exits 0 on valid, 1 on invalid (message to stderr), 2 on usage error.
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: requires jsonschema (pip install jsonschema)", file=sys.stderr)
    sys.exit(2)


def _load(path: Path):
    text = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        instance = _load(Path(sys.argv[1]))
        schema = _load(Path(sys.argv[2]))
    except Exception as e:
        print(f"LOAD ERROR: {e}", file=sys.stderr)
        return 2
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError as e:
        print(
            f"INVALID: {e.message} at {'/'.join(str(p) for p in e.absolute_path)}",
            file=sys.stderr,
        )
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

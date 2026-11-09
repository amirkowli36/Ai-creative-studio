#!/usr/bin/env python3
"""Validate repository JSON and Jupyter notebook files using only Python stdlib."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def validate_notebook(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{path}: invalid notebook JSON: {exc}"]

    if not isinstance(data, dict):
        return [f"{path}: notebook root must be an object"]
    if data.get("nbformat") != 4:
        errors.append(f"{path}: expected nbformat 4")
    if not isinstance(data.get("cells"), list):
        errors.append(f"{path}: 'cells' must be an array")
    else:
        for index, cell in enumerate(data["cells"]):
            if not isinstance(cell, dict):
                errors.append(f"{path}: cell {index} must be an object")
                continue
            if cell.get("cell_type") not in {"markdown", "code", "raw"}:
                errors.append(f"{path}: cell {index} has an invalid cell_type")
            source = cell.get("source")
            if not isinstance(source, (str, list)):
                errors.append(f"{path}: cell {index} source must be a string or array")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    notebook_paths = sorted(root.rglob("*.ipynb"))
    workflow_json_paths = sorted((root / "workflows").rglob("*.json")) if (root / "workflows").exists() else []

    for path in notebook_paths:
        errors.extend(validate_notebook(path))

    for path in workflow_json_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append(f"{path}: workflow JSON root must be an object")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"Validated {len(notebook_paths)} notebook(s) and {len(workflow_json_paths)} workflow JSON file(s).")
    if not workflow_json_paths:
        print("No workflow JSON exports yet; add only workflows that have been tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

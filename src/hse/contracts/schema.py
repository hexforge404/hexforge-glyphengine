from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from hexforge_contracts import load_schema as _load_schema
from hexforge_contracts import validate_json as _validate_json


# Local override directory so we are not dependent on package data files.
_DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "schemas" / "common"
_SCHEMAS_ROOT = Path(os.getenv("HEXFORGE_CONTRACTS_ROOT", _DEFAULT_ROOT))


def load_contract_schema(name: str) -> Dict[str, Any]:
    """
    Load a contract schema, preferring the repo-local copy under schemas/common.
    Falls back to hexforge_contracts' loader if local file is absent.
    """
    local_path = _SCHEMAS_ROOT / name
    if local_path.exists():
        return json.loads(local_path.read_text(encoding="utf-8"))
    # Fallback to packaged schema (if/when available)
    return _load_schema(name)


def validate_contract(doc: Dict[str, Any], name: str) -> None:
    """Validate the given document against a named contract schema."""
    schema = load_contract_schema(name)
    _validate_json(doc, schema)


__all__ = ["load_contract_schema", "validate_contract"]

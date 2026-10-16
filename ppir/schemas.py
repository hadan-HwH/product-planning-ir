"""Load per-kind schemas and merge them with the shared envelope."""
from __future__ import annotations

from pathlib import Path

import yaml

ENVELOPE_FILE = "_envelope.schema.yaml"


def load_schemas(schemas_dir: Path):
    """Return (envelope_dict, {kind_name: kind_schema_dict})."""
    envelope = yaml.safe_load((schemas_dir / ENVELOPE_FILE).read_text(encoding="utf-8"))
    kinds: dict = {}
    for path in sorted(schemas_dir.glob("*.schema.yaml")):
        if path.name == ENVELOPE_FILE:
            continue
        schema = yaml.safe_load(path.read_text(encoding="utf-8"))
        kinds[schema["x-kind"]] = schema
    return envelope, kinds


def merged_schema(envelope: dict, kind_schema: dict) -> dict:
    properties = {**envelope.get("properties", {}), **kind_schema.get("properties", {})}
    required = sorted(set(envelope.get("required", [])) | set(kind_schema.get("required", [])))
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": True,
    }


def allowed_props(envelope: dict, kind_schema: dict) -> set:
    return set(envelope.get("properties", {})) | set(kind_schema.get("properties", {}))

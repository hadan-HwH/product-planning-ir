"""Load and expose shared PPIR identifiers from ppir.config.yaml."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from ppir import registry

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_config(repo_root: Path = REPO_ROOT) -> dict:
    return yaml.safe_load((repo_root / "ppir.config.yaml").read_text(encoding="utf-8"))


_CFG = load_config()
DOMAINS = set(_CFG["domains"])
SHARED_DOMAINS = set(_CFG.get("shared_domains", []))
STATUSES = set(_CFG["statuses"])
TRACKS = set(_CFG["tracks"])
COMMITMENT_LEVELS = set(_CFG["commitment_levels"])
KIND_TOKEN_MAP = registry.token_map()   # single source: kind-registry.yaml
ID_RE = re.compile(_CFG["id_regex"])


def kind_token(atom_id: str) -> str:
    return atom_id.split(".")[1]


def id_domain(atom_id: str) -> str:
    return atom_id.split(".")[0]


def schema_mode() -> str:
    return load_config().get("schema_mode", "warn")

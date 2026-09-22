#!/usr/bin/env python3
"""
scholar_config.py — Configuration loader for Scholar Scout skills.

Loads scholar-config.json (and optional scholar-config.local.json override).
Provides convenience functions for accessing config sections.
"""

import json
import sys
from functools import lru_cache
from pathlib import Path

_SHARED_DIR = Path(__file__).resolve().parent
_CONFIG_PATH = _SHARED_DIR / "scholar-config.json"
_LOCAL_CONFIG_PATH = _SHARED_DIR / "scholar-config.local.json"


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base, returning new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@lru_cache(maxsize=1)
def load_scholar_config() -> dict:
    """Load and merge config files. Cached after first call."""
    if not _CONFIG_PATH.exists():
        print(f"[WARN] Config not found: {_CONFIG_PATH}", file=sys.stderr)
        return {}

    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    if _LOCAL_CONFIG_PATH.exists():
        with open(_LOCAL_CONFIG_PATH, "r", encoding="utf-8") as f:
            local = json.load(f)
        config = _deep_merge(config, local)

    return config


def paths_config() -> dict:
    return load_scholar_config().get("paths", {})


def daily_papers_config() -> dict:
    return load_scholar_config().get("daily_papers", {})


def researcher_config() -> dict:
    return load_scholar_config().get("researcher", {})


def automation_config() -> dict:
    return load_scholar_config().get("automation", {})


def vault_path() -> Path:
    raw = paths_config().get("obsidian_vault", "~/ObsidianVault")
    return Path(raw).expanduser().resolve()


def daily_papers_dir() -> Path:
    return vault_path() / paths_config().get("daily_papers_folder", "DailyPapers")


def notes_path() -> Path:
    return vault_path() / paths_config().get("paper_notes_folder", "论文笔记")


def concepts_path() -> Path:
    return notes_path() / paths_config().get("concepts_folder", "_概念")

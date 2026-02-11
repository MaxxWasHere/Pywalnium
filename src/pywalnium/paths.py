from __future__ import annotations

import os
from pathlib import Path


def xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")).expanduser()


def xdg_cache_home() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")).expanduser()


def wal_cache_dir() -> Path:
    return xdg_cache_home() / "wal"


def wal_colors_json() -> Path:
    return wal_cache_dir() / "colors.json"


def pywalnium_cache_dir() -> Path:
    return xdg_cache_home() / "pywalnium"


def ensure_parent_dir(path: Path, dry_run: bool = False) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.pywalnium.bak")

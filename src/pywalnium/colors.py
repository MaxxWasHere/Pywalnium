from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import pywalnium_cache_dir, wal_colors_json


@dataclass(frozen=True)
class Palette:
    background: str
    foreground: str
    cursor: str
    colors: list[str]

    def as_dict(self) -> dict[str, Any]:
        color_map = {f"color{i}": value for i, value in enumerate(self.colors)}
        return {
            "special": {
                "background": self.background,
                "foreground": self.foreground,
                "cursor": self.cursor,
            },
            "colors": color_map,
        }


def _validate_hex(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("#") or len(value) != 7:
        raise ValueError(f"Invalid color value: {value!r}")
    return value


def load_palette_from_file(colors_path: Path | None = None) -> Palette:
    src = colors_path or wal_colors_json()
    data = json.loads(src.read_text(encoding="utf-8"))
    special = data.get("special", {})
    color_map = data.get("colors", {})
    colors = [_validate_hex(color_map[f"color{i}"]) for i in range(16)]
    return Palette(
        background=_validate_hex(special["background"]),
        foreground=_validate_hex(special["foreground"]),
        cursor=_validate_hex(special.get("cursor", special["foreground"])),
        colors=colors,
    )


def generate_with_wal(wallpaper: str) -> None:
    wal_bin = shutil.which("wal")
    if wal_bin is None:
        raise RuntimeError("`wal` command is not available in PATH.")
    result = subprocess.run(
        [wal_bin, "-n", "-q", "-i", wallpaper],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(f"wal generation failed: {stderr or 'unknown error'}")


def resolve_palette(wallpaper: str | None = None, verbose: bool = False) -> Palette:
    if wallpaper:
        if verbose:
            print(f"INFO: Generating palette from wallpaper: {wallpaper}")
        generate_with_wal(wallpaper)

    try:
        palette = load_palette_from_file()
    except FileNotFoundError as exc:
        raise RuntimeError(
            "No pywal palette found. Run `wal -i <image>` first or pass --wallpaper."
        ) from exc
    except KeyError as exc:
        raise RuntimeError(f"Malformed wal colors file: missing key {exc}") from exc

    cache_dir = pywalnium_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "last-palette.json").write_text(
        json.dumps(palette.as_dict(), indent=2),
        encoding="utf-8",
    )
    return palette

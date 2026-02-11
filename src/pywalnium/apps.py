from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from shutil import which
from typing import Callable

from .colors import Palette
from .paths import xdg_config_home
from .renderers import (
    render_alacritty,
    render_dunst,
    render_hyprland,
    render_kitty,
    render_rofi,
    render_waybar,
)


RenderFn = Callable[[Palette], str]


@dataclass(frozen=True)
class AppAdapter:
    name: str
    binaries: tuple[str, ...]
    config_hints: tuple[Path, ...]
    target_path: Path
    renderer: RenderFn
    description: str

    def is_installed(self) -> bool:
        if any(which(binary) for binary in self.binaries):
            return True
        return any(path.exists() for path in self.config_hints)


def _cfg(*parts: str) -> Path:
    return xdg_config_home().joinpath(*parts)


def build_registry() -> dict[str, AppAdapter]:
    apps = [
        AppAdapter(
            name="kitty",
            binaries=("kitty",),
            config_hints=(_cfg("kitty", "kitty.conf"),),
            target_path=_cfg("kitty", "colors-pywalnium.conf"),
            renderer=render_kitty,
            description="Kitty terminal include file",
        ),
        AppAdapter(
            name="alacritty",
            binaries=("alacritty",),
            config_hints=(_cfg("alacritty", "alacritty.toml"), _cfg("alacritty", "alacritty.yml")),
            target_path=_cfg("alacritty", "colors-pywalnium.toml"),
            renderer=render_alacritty,
            description="Alacritty color table",
        ),
        AppAdapter(
            name="rofi",
            binaries=("rofi",),
            config_hints=(_cfg("rofi", "config.rasi"),),
            target_path=_cfg("rofi", "colors-pywalnium.rasi"),
            renderer=render_rofi,
            description="Rofi theme variables",
        ),
        AppAdapter(
            name="hyprland",
            binaries=("Hyprland",),
            config_hints=(_cfg("hypr", "hyprland.conf"),),
            target_path=_cfg("hypr", "pywalnium-colors.conf"),
            renderer=render_hyprland,
            description="Hyprland color variables",
        ),
        AppAdapter(
            name="waybar",
            binaries=("waybar",),
            config_hints=(_cfg("waybar", "config"), _cfg("waybar", "config.jsonc")),
            target_path=_cfg("waybar", "colors-pywalnium.css"),
            renderer=render_waybar,
            description="Waybar CSS variables",
        ),
        AppAdapter(
            name="dunst",
            binaries=("dunst",),
            config_hints=(_cfg("dunst", "dunstrc"),),
            target_path=_cfg("dunst", "dunstrc-pywalnium.conf"),
            renderer=render_dunst,
            description="Dunst notification colors",
        ),
    ]
    return {app.name: app for app in apps}


@lru_cache(maxsize=1)
def get_registry() -> dict[str, AppAdapter]:
    return build_registry()


def get_adapter(name: str) -> AppAdapter | None:
    query = name.strip().lower()
    return get_registry().get(query)


def detected_apps() -> list[AppAdapter]:
    return [app for app in get_registry().values() if app.is_installed()]

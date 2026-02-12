# pywalnium

`pywalnium` is a terminal-first Arch Linux helper that applies pywal palettes to multiple desktop apps.

## Features

- Single app generation: `pywalnium --gen <app>`
- Undo generated files safely: `pywalnium --ungen <app>`
- Auto-detect and generate for all known apps: `pywalnium --gen-all`
- App detection from both binaries and config presence
- Backup-safe writes with restore support
- Dry-run and verbose modes for shell workflows

Supported app adapters:

- `kitty`
- `alacritty`
- `rofi`
- `hyprland`
- `waybar`
- `dunst`

## Install (easy)

One command:

```bash
curl -fsSL https://raw.githubusercontent.com/MaxxWasHere/Pywalnium/main/install.sh | bash
```

This installer:

- uses `pipx` when available (recommended for global CLI apps)
- falls back to `python3 -m pip install --user` if `pipx` is missing
- prints exact next steps if your PATH needs `~/.local/bin`

Manual alternatives:

```bash
pipx install git+https://github.com/MaxxWasHere/Pywalnium.git
# or
python3 -m pip install --user --upgrade git+https://github.com/MaxxWasHere/Pywalnium.git
```

## Usage

List support and detection state:

```bash
pywalnium --list-apps
```

Generate for one detected app:

```bash
pywalnium --gen kitty
```

Generate from a wallpaper path:

```bash
pywalnium --gen-all --wallpaper ~/Pictures/wallpaper.jpg
```

Undo generation for one app:

```bash
pywalnium --ungen kitty
```

Preview only:

```bash
pywalnium --gen-all --dry-run --verbose
```

## end4 dots note

The tool writes dedicated generated files in each app config directory. In your customized end4 dotfiles, include these generated files from your primary app configs so updates are picked up cleanly.

Example include points:

- Kitty: include `~/.config/kitty/colors-pywalnium.conf`
- Hyprland: source `~/.config/hypr/pywalnium-colors.conf`
- Waybar CSS: import `~/.config/waybar/colors-pywalnium.css`

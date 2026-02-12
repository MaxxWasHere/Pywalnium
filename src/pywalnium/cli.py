from __future__ import annotations

import argparse
import sys

from .apps import detected_apps, get_adapter, get_registry
from .colors import resolve_palette
from .core import OperationResult, generate_for_app, ungenerate_for_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pywalnium",
        description="Generate pywal-compatible colors for detected desktop apps.",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--gen", metavar="APP", help="Generate colors for one app")
    action.add_argument("--ungen", metavar="APP", help="Undo generated colors for one app")
    action.add_argument("--gen-all", action="store_true", help="Generate for all detected apps")
    parser.add_argument("--list-apps", action="store_true", help="List supported apps and detection status")
    parser.add_argument("--wallpaper", help="Generate palette from wallpaper path via wal")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing files")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    return parser


def _info(message: str) -> None:
    print(f"INFO: {message}")


def _warn(message: str) -> None:
    print(f"WARN: {message}", file=sys.stderr)


def _error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def _print_result(result: OperationResult, verbose: bool = False) -> None:
    status = "changed" if result.changed else "unchanged"
    if verbose:
        print(f"RESULT: app={result.app} status={status} target={result.target} message={result.message}")
    else:
        print(f"RESULT: {result.app} {status} - {result.message}")


def _list_apps() -> int:
    registry = get_registry()
    detected = {app.name for app in detected_apps()}
    _info(f"Supported apps: {len(registry)}; detected: {len(detected)}")
    for app in registry.values():
        state = "detected" if app.name in detected else "not detected"
        print(f"- {app.name:10} {state:13} {app.description}")
    return 0


def _generate_single(app_name: str, wallpaper: str | None, dry_run: bool, verbose: bool) -> int:
    app = get_adapter(app_name)
    if app is None:
        _error(f"Unknown app '{app_name}'. Use --list-apps to see supported names.")
        return 2
    if not app.is_installed():
        _error(
            f"App '{app.name}' was not detected (binary/config missing). "
            "Install or create config first, or use --gen-all for auto-detected apps.",
        )
        return 2

    _info(f"Generating app: {app.name}")
    palette = resolve_palette(wallpaper=wallpaper, verbose=verbose)
    result = generate_for_app(app, palette, dry_run=dry_run)
    _print_result(result, verbose=verbose)
    return 0


def _generate_all(wallpaper: str | None, dry_run: bool, verbose: bool) -> int:
    apps = detected_apps()
    if not apps:
        _warn("No supported apps were detected. Use --list-apps.")
        return 2

    _info(f"Generating for detected apps: {len(apps)}")
    palette = resolve_palette(wallpaper=wallpaper, verbose=verbose)
    for idx, app in enumerate(apps, start=1):
        if verbose:
            print(f"INFO: [{idx}/{len(apps)}] {app.name}")
        result = generate_for_app(app, palette, dry_run=dry_run)
        _print_result(result, verbose=verbose)
    return 0


def _ungenerate_single(app_name: str, dry_run: bool) -> int:
    app = get_adapter(app_name)
    if app is None:
        _error(f"Unknown app '{app_name}'. Use --list-apps to see supported names.")
        return 2
    _info(f"Removing generated theme for app: {app.name}")
    result = ungenerate_for_app(app, dry_run=dry_run)
    _print_result(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_apps:
        return _list_apps()

    if not any([args.gen, args.ungen, args.gen_all]):
        parser.print_help(sys.stderr)
        return 2

    try:
        if args.gen:
            return _generate_single(args.gen, args.wallpaper, args.dry_run, args.verbose)
        if args.gen_all:
            return _generate_all(args.wallpaper, args.dry_run, args.verbose)
        if args.ungen:
            return _ungenerate_single(args.ungen, args.dry_run)
    except RuntimeError as exc:
        _error(str(exc))
        return 1

    return 0


def entrypoint() -> None:
    raise SystemExit(main())

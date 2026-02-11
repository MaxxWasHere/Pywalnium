from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .apps import AppAdapter
from .colors import Palette
from .paths import backup_path, ensure_parent_dir


@dataclass
class OperationResult:
    app: str
    target: Path
    changed: bool
    message: str


def generate_for_app(
    app: AppAdapter,
    palette: Palette,
    dry_run: bool = False,
) -> OperationResult:
    content = app.renderer(palette)
    target = app.target_path
    backup = backup_path(target)
    previous = target.read_text(encoding="utf-8") if target.exists() else None

    if previous == content:
        return OperationResult(
            app=app.name,
            target=target,
            changed=False,
            message="already up to date",
        )

    if previous is not None and not backup.exists() and not dry_run:
        ensure_parent_dir(backup, dry_run=False)
        shutil.copy2(target, backup)

    if not dry_run:
        ensure_parent_dir(target, dry_run=False)
        target.write_text(content, encoding="utf-8")

    return OperationResult(
        app=app.name,
        target=target,
        changed=True,
        message="generated",
    )


def ungenerate_for_app(app: AppAdapter, dry_run: bool = False) -> OperationResult:
    target = app.target_path
    backup = backup_path(target)

    if backup.exists():
        if not dry_run:
            ensure_parent_dir(target, dry_run=False)
            shutil.move(str(backup), str(target))
        return OperationResult(
            app=app.name,
            target=target,
            changed=True,
            message="restored from backup",
        )

    if target.exists():
        if not dry_run:
            target.unlink()
        return OperationResult(
            app=app.name,
            target=target,
            changed=True,
            message="removed generated file",
        )

    return OperationResult(
        app=app.name,
        target=target,
        changed=False,
        message="nothing to remove",
    )

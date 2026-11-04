"""
=========================================================
sAI V1 - User Data Storage and Migration Architecture
=========================================================
Manages persistent user data paths and safe legacy-data
migration across source and packaged installations.
=========================================================
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path


IGNORED_MIGRATION_FILENAMES = {
    ".env",
    ".git",
    ".gitignore",
    ".DS_Store",
    "desktop.ini",
    "thumbs.db",
}

IGNORED_MIGRATION_EXTENSIONS = {
    ".pyc",
    ".pyo",
}

IGNORED_MIGRATION_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
}


def is_packaged_executable() -> bool:
    """Return True if running as a packaged/frozen executable."""
    return getattr(sys, "frozen", False) or os.getenv("SAI_PACKAGED", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def get_data_dir(base_dir: Path | None = None) -> Path:
    """
    Determine the persistent user data directory using the precedence policy:
    1. If SAI_DATA_DIR is configured, use its expanded absolute path.
    2. If running as a packaged executable, use %LOCALAPPDATA%\\sAI\\data.
       (If LOCALAPPDATA is missing or empty, explicitly falls back to the user's
       home directory: %USERPROFILE%\\.sai\\data; never falls back to a protected path).
    3. If running from source, retain the project-local data directory to preserve
       developer workflow.
    """
    override = os.getenv("SAI_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    if is_packaged_executable():
        local_app_data = os.getenv("LOCALAPPDATA", "").strip()
        if local_app_data:
            return (Path(local_app_data) / "sAI" / "data").resolve()

        # Explicit fallback if LOCALAPPDATA is missing or empty
        try:
            home = Path.home()
            return (home / ".sai" / "data").resolve()
        except Exception as exc:
            raise RuntimeError(
                f"Unable to determine a user data directory: LOCALAPPDATA is missing and home is inaccessible ({exc}). "
                "Set the SAI_DATA_DIR environment variable explicitly."
            ) from exc

    # Source-development mode
    base = base_dir or Path(__file__).resolve().parent.parent
    return (base / "data").resolve()


def migrate_legacy_data(source_dir: Path | str, target_dir: Path | str) -> dict[str, int]:
    """
    Safely copy user data from source_dir into target_dir.
    Rules:
    - Never delete or modify source files.
    - Never overwrite an existing destination file.
    - Preserve directory hierarchy and metadata (shutil.copy2).
    - Exclude .env, virtual environments, bytecode, and repo metadata.
    - Repeat-safe: multiple runs do not duplicate or corrupt data.
    """
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()

    if not source.exists() or not source.is_dir():
        return {"migrated": 0, "conflicts": 0, "skipped": 0}

    if source == target:
        return {"migrated": 0, "conflicts": 0, "skipped": 0}

    stats = {"migrated": 0, "conflicts": 0, "skipped": 0}

    try:
        target.mkdir(parents=True, exist_ok=True)

        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in IGNORED_MIGRATION_DIRS]

            root_path = Path(root)
            rel_root = root_path.relative_to(source)
            dest_dir = target / rel_root

            for file_name in files:
                if file_name in IGNORED_MIGRATION_FILENAMES:
                    stats["skipped"] += 1
                    continue

                if any(file_name.endswith(ext) for ext in IGNORED_MIGRATION_EXTENSIONS):
                    stats["skipped"] += 1
                    continue

                src_file = root_path / file_name
                dest_file = dest_dir / file_name

                if dest_file.exists():
                    stats["conflicts"] += 1
                    continue

                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
                stats["migrated"] += 1

        return stats

    except Exception as exc:
        raise RuntimeError(
            f"Legacy data migration failed from '{source}' to '{target}': {exc}. "
            "Please verify filesystem permissions or set SAI_DATA_DIR explicitly."
        ) from exc


def maybe_run_migration(target_dir: Path, base_dir: Path | None = None) -> dict[str, int] | None:
    """
    Detect legacy source data and migrate it if running packaged or explicitly requested.
    """
    override_legacy = os.getenv("SAI_LEGACY_DATA_DIR", "").strip()
    if override_legacy:
        source_path = Path(override_legacy).expanduser().resolve()
        return migrate_legacy_data(source_path, target_dir)

    if is_packaged_executable():
        base = base_dir or Path(__file__).resolve().parent.parent
        legacy_candidate = (base / "data").resolve()
        if (
            legacy_candidate.exists()
            and legacy_candidate.is_dir()
            and legacy_candidate != target_dir.resolve()
        ):
            return migrate_legacy_data(legacy_candidate, target_dir)

    return None

"""
=========================================================
sAI V1 - File Manager
=========================================================
Centralized file and folder management.
=========================================================
"""

from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime
from typing import List

from backend.config import (
    DATA_DIR,
    CACHE_DIR,
    MEMORY_DIR,
    TEMP_DIR,
    UPLOAD_DIR,
)


class FileManager:

    ALLOWED_ROOTS = (
        DATA_DIR,
        CACHE_DIR,
        MEMORY_DIR,
        TEMP_DIR,
        UPLOAD_DIR,
    )

    @classmethod
    def _validated_path(cls, path: str | Path) -> Path:
        resolved = Path(path).resolve()
        roots = [root.resolve() for root in cls.ALLOWED_ROOTS]

        if not any(resolved == root or root in resolved.parents for root in roots):
            raise PermissionError("File operations are limited to sAI data folders.")

        return resolved

    # --------------------------------------------------

    @staticmethod
    def ensure(path: str | Path):

        path = FileManager._validated_path(path)

        path.mkdir(parents=True, exist_ok=True)

        return path

    # --------------------------------------------------

    @staticmethod
    def exists(path: str | Path):

        return FileManager._validated_path(path).exists()

    # --------------------------------------------------

    @staticmethod
    def create_file(path: str | Path, content: str = ""):

        path = FileManager._validated_path(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")

        return path

    # --------------------------------------------------

    @staticmethod
    def read(path: str | Path):

        return FileManager._validated_path(path).read_text(encoding="utf-8")

    # --------------------------------------------------

    @staticmethod
    def write(path: str | Path, content: str):

        FileManager._validated_path(path).write_text(content, encoding="utf-8")

    # --------------------------------------------------

    @staticmethod
    def append(path: str | Path, content: str):

        with open(FileManager._validated_path(path), "a", encoding="utf-8") as file:
            file.write(content)

    # --------------------------------------------------

    @staticmethod
    def delete(path: str | Path, *, approved: bool = False):

        if not approved:
            raise PermissionError("Deleting files requires explicit approval.")

        path = FileManager._validated_path(path)

        if path.exists():

            if path.is_dir():
                shutil.rmtree(path)

            else:
                path.unlink()

    # --------------------------------------------------

    @staticmethod
    def copy(source, destination):

        shutil.copy2(
            FileManager._validated_path(source),
            FileManager._validated_path(destination),
        )

    # --------------------------------------------------

    @staticmethod
    def move(source, destination):

        shutil.move(
            FileManager._validated_path(source),
            FileManager._validated_path(destination),
        )

    # --------------------------------------------------

    @staticmethod
    def rename(source, destination):

        FileManager._validated_path(source).rename(
            FileManager._validated_path(destination)
        )

    # --------------------------------------------------

    @staticmethod
    def list_files(folder) -> List[Path]:

        folder = FileManager._validated_path(folder)

        if not folder.exists():
            return []

        return sorted(
            [
                file
                for file in folder.iterdir()
                if file.is_file()
            ]
        )

    # --------------------------------------------------

    @staticmethod
    def list_folders(folder) -> List[Path]:

        folder = FileManager._validated_path(folder)

        if not folder.exists():
            return []

        return sorted(
            [
                item
                for item in folder.iterdir()
                if item.is_dir()
            ]
        )

    # --------------------------------------------------

    @staticmethod
    def size(path):

        path = FileManager._validated_path(path)

        if path.is_file():
            return path.stat().st_size

        total = 0

        for file in path.rglob("*"):

            if file.is_file():
                total += file.stat().st_size

        return total

    # --------------------------------------------------

    @staticmethod
    def timestamp():

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    # --------------------------------------------------

    @staticmethod
    def clean_temp():

        if not TEMP_DIR.exists():
            return

        for item in TEMP_DIR.iterdir():

            try:

                if item.is_dir():
                    shutil.rmtree(item)

                else:
                    item.unlink()

            except Exception:
                pass

    # --------------------------------------------------

    @staticmethod
    def initialize():

        for folder in (
            DATA_DIR,
            CACHE_DIR,
            MEMORY_DIR,
            TEMP_DIR,
            UPLOAD_DIR,
        ):
            folder.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":

    FileManager.initialize()

    print("File Manager Ready")

    print(FileManager.list_folders(DATA_DIR))

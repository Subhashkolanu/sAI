from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.storage import (
    get_data_dir,
    is_packaged_executable,
    maybe_run_migration,
    migrate_legacy_data,
)
from backend.settings import Settings
from backend.profile_memory import ProfileMemory
from backend.memory import Memory


class StoragePathPolicyTests(unittest.TestCase):
    def test_explicit_sai_data_dir_override(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_data"
            with patch.dict(os.environ, {"SAI_DATA_DIR": str(custom_path)}):
                resolved = get_data_dir()
                self.assertEqual(resolved, custom_path.resolve())

    def test_packaged_application_path_selection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            local_app_data = Path(temp_dir) / "AppData" / "Local"
            with patch.dict(os.environ, {"LOCALAPPDATA": str(local_app_data), "SAI_DATA_DIR": ""}), \
                 patch("backend.storage.is_packaged_executable", return_value=True):
                resolved = get_data_dir()
                expected = (local_app_data / "sAI" / "data").resolve()
                self.assertEqual(resolved, expected)

    def test_packaged_application_path_fallback_when_localappdata_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_home = Path(temp_dir) / "UserHome"
            with patch.dict(os.environ, {"LOCALAPPDATA": "", "SAI_DATA_DIR": ""}), \
                 patch("backend.storage.is_packaged_executable", return_value=True), \
                 patch("pathlib.Path.home", return_value=fake_home):
                resolved = get_data_dir()
                expected = (fake_home / ".sai" / "data").resolve()
                self.assertEqual(resolved, expected)

    def test_source_development_path_preservation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_base = Path(temp_dir) / "my_project"
            with patch.dict(os.environ, {"SAI_DATA_DIR": ""}), \
                 patch("backend.storage.is_packaged_executable", return_value=False):
                resolved = get_data_dir(base_dir=repo_base)
                expected = (repo_base / "data").resolve()
                self.assertEqual(resolved, expected)


class LegacyDataMigrationTests(unittest.TestCase):
    def test_first_run_migration_from_legacy_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source_data"
            target = Path(temp_dir) / "target_data"
            source.mkdir(parents=True)
            (source / "settings.json").write_text('{"theme": "dark"}', encoding="utf-8")
            (source / "profile.json").write_text('{"name": "Subhash"}', encoding="utf-8")

            stats = migrate_legacy_data(source, target)
            self.assertEqual(stats["migrated"], 2)
            self.assertEqual(stats["conflicts"], 0)
            self.assertTrue((target / "settings.json").exists())
            self.assertTrue((target / "profile.json").exists())
            self.assertEqual((target / "settings.json").read_text(encoding="utf-8"), '{"theme": "dark"}')

    def test_existing_destination_files_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source_data"
            target = Path(temp_dir) / "target_data"
            source.mkdir(parents=True)
            target.mkdir(parents=True)

            (source / "settings.json").write_text('{"theme": "source_light"}', encoding="utf-8")
            (target / "settings.json").write_text('{"theme": "target_dark"}', encoding="utf-8")

            stats = migrate_legacy_data(source, target)
            self.assertEqual(stats["migrated"], 0)
            self.assertEqual(stats["conflicts"], 1)
            # Ensure target file was NOT overwritten
            self.assertEqual((target / "settings.json").read_text(encoding="utf-8"), '{"theme": "target_dark"}')

    def test_repeated_migration_is_safe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source_data"
            target = Path(temp_dir) / "target_data"
            source.mkdir(parents=True)
            (source / "file1.txt").write_text("data 1", encoding="utf-8")

            # Run 1
            stats1 = migrate_legacy_data(source, target)
            self.assertEqual(stats1["migrated"], 1)
            self.assertEqual(stats1["conflicts"], 0)

            # Run 2
            stats2 = migrate_legacy_data(source, target)
            self.assertEqual(stats2["migrated"], 0)
            self.assertEqual(stats2["conflicts"], 1)
            self.assertEqual((target / "file1.txt").read_text(encoding="utf-8"), "data 1")

    def test_migration_preserves_nested_directories_and_file_contents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source_data"
            target = Path(temp_dir) / "target_data"
            nested = source / "nested" / "deep"
            nested.mkdir(parents=True)
            binary_content = b"\x00\x01\x02\xFF\xFE\xFD"
            (nested / "blob.bin").write_bytes(binary_content)

            stats = migrate_legacy_data(source, target)
            self.assertEqual(stats["migrated"], 1)
            dest_file = target / "nested" / "deep" / "blob.bin"
            self.assertTrue(dest_file.exists())
            self.assertEqual(dest_file.read_bytes(), binary_content)

    def test_migration_failure_is_reported_clearly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source_data"
            source.mkdir(parents=True)
            (source / "file.txt").write_text("hello", encoding="utf-8")

            # Target exists as a file, so target.mkdir() or writing inside it fails
            target_as_file = Path(temp_dir) / "not_a_dir"
            target_as_file.write_text("blocking file", encoding="utf-8")

            with self.assertRaises(RuntimeError) as context:
                migrate_legacy_data(source, target_as_file / "sub")
            self.assertIn("Legacy data migration failed", str(context.exception))

    def test_settings_and_profile_load_from_migrated_location(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            target = Path(temp_dir) / "target"
            source.mkdir(parents=True)
            (source / "settings.json").write_text(
                '{"theme": "light", "provider": "ollama", "ollama_model": "test-model"}',
                encoding="utf-8",
            )
            (source / "profile.json").write_text(
                '{"user_name": "TestUser", "assistant_name": "sAI"}',
                encoding="utf-8",
            )

            migrate_legacy_data(source, target)

            # Load Settings and ProfileMemory from target
            settings = Settings(target / "settings.json")
            self.assertEqual(settings.get("theme"), "light")
            self.assertEqual(settings.get("ollama_model"), "test-model")

            profile = ProfileMemory(target / "profile.json")
            self.assertEqual(profile.recall("user_name"), "TestUser")
            self.assertEqual(profile.recall("assistant_name"), "sAI")

    def test_sqlite_conversation_history_remains_readable_after_migration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            target = Path(temp_dir) / "target"
            (source / "memory").mkdir(parents=True)

            # Create source database and write conversation records
            source_db_path = source / "memory" / "memory.db"
            source_memory = Memory(source_db_path)
            try:
                source_memory.add("user", "Hello from legacy!")
                source_memory.add("assistant", "Hello! I am migrated sAI.")
            finally:
                source_memory.close()

            # Migrate
            stats = migrate_legacy_data(source, target)
            self.assertGreaterEqual(stats["migrated"], 1)

            # Open migrated database and verify
            target_db_path = target / "memory" / "memory.db"
            self.assertTrue(target_db_path.exists())
            target_memory = Memory(target_db_path)
            try:
                history = target_memory.all()
            finally:
                target_memory.close()

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["role"], "user")
            self.assertEqual(history[0]["message"], "Hello from legacy!")
            self.assertEqual(history[1]["role"], "assistant")
            self.assertEqual(history[1]["message"], "Hello! I am migrated sAI.")

    def test_no_original_user_files_are_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            target = Path(temp_dir) / "target"
            source.mkdir(parents=True)
            test_file = source / "test.txt"
            test_file.write_text("important user data", encoding="utf-8")
            orig_mtime = test_file.stat().st_mtime

            migrate_legacy_data(source, target)

            self.assertTrue(test_file.exists())
            self.assertEqual(test_file.read_text(encoding="utf-8"), "important user data")
            self.assertEqual(test_file.stat().st_mtime, orig_mtime)

    def test_paths_containing_spaces_and_non_ascii_characters_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "Source Data With Spaces & Ûñicøde"
            target = Path(temp_dir) / "Targët Pâth With Spãces"
            source.mkdir(parents=True)

            (source / "döcümënt.txt").write_text("unicode content: \u2603 \u2764", encoding="utf-8")

            stats = migrate_legacy_data(source, target)
            self.assertEqual(stats["migrated"], 1)
            migrated_file = target / "döcümënt.txt"
            self.assertTrue(migrated_file.exists())
            self.assertEqual(
                migrated_file.read_text(encoding="utf-8"),
                "unicode content: \u2603 \u2764",
            )

    def test_env_files_are_excluded_from_migration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            target = Path(temp_dir) / "target"
            source.mkdir(parents=True)
            (source / ".env").write_text("SECRET_KEY=12345", encoding="utf-8")
            (source / "normal.txt").write_text("normal", encoding="utf-8")

            stats = migrate_legacy_data(source, target)
            self.assertEqual(stats["migrated"], 1)
            self.assertEqual(stats["skipped"], 1)
            self.assertFalse((target / ".env").exists())
            self.assertTrue((target / "normal.txt").exists())

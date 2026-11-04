"""
=========================================================
sAI V1 - First-Run Setup Unit Tests
=========================================================
Validates the first-run onboarding detection, wizard steps,
service management, model discovery, and persistence.
=========================================================
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx

from backend.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from backend.memory import Memory
from backend.model_manager import ModelInfo, ModelManager
from backend.settings import Settings
from frontend.setup_wizard import SetupWizard, RECOMMENDED_OLLAMA_MODEL


class FirstRunSetupDetectionTests(unittest.TestCase):
    """Verifies fresh install detection vs existing user handling."""

    def test_first_launch_detected_when_settings_file_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            self.assertFalse(path.exists())

            settings = Settings(path)
            self.assertTrue(settings.needs_setup())
            self.assertFalse(settings.get("setup_completed"))

    def test_existing_user_skips_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            # Pre-existing settings file from earlier release without setup_completed flag
            existing_data = {
                "provider": "ollama",
                "ollama_model": "qwen3:4b-instruct-2507-q4_K_M",
                "ollama_base_url": "http://127.0.0.1:11434",
                "openai_model": "local-model",
                "openai_base_url": "http://127.0.0.1:8080/v1",
                "temperature": 0.7,
                "max_tokens": 1024,
                "theme": "dark",
            }
            path.write_text(json.dumps(existing_data), encoding="utf-8")

            settings = Settings(path)
            self.assertFalse(settings.needs_setup())
            self.assertTrue(settings.get("setup_completed"))

    def test_corrupted_or_invalid_settings_triggers_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            # Invalid endpoint URL
            corrupted = {
                "provider": "ollama",
                "ollama_model": "qwen3:4b-instruct-2507-q4_K_M",
                "ollama_base_url": "not-a-valid-url",
                "setup_completed": True,
            }
            path.write_text(json.dumps(corrupted), encoding="utf-8")

            settings = Settings(path)
            self.assertTrue(settings.needs_setup())

    def test_explicit_setup_completed_false_triggers_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            data = {
                "provider": "ollama",
                "ollama_model": "qwen3:4b-instruct-2507-q4_K_M",
                "ollama_base_url": "http://127.0.0.1:11434",
                "openai_model": "local-model",
                "openai_base_url": "http://127.0.0.1:8080/v1",
                "temperature": 0.7,
                "max_tokens": 1024,
                "theme": "dark",
                "setup_completed": False,
            }
            path.write_text(json.dumps(data), encoding="utf-8")

            settings = Settings(path)
            self.assertTrue(settings.needs_setup())


class OllamaDetectionAndManagementTests(unittest.TestCase):
    """Verifies Ollama detection, service status, and startup."""

    @patch("shutil.which", return_value=None)
    @patch("pathlib.Path.is_file", return_value=False)
    def test_ollama_missing_detection(self, mock_is_file, mock_which):
        manager = ModelManager()
        self.assertIsNone(manager.find_ollama_binary())
        self.assertFalse(manager.is_ollama_installed())

    @patch("shutil.which", return_value=r"C:\Users\User\AppData\Local\Programs\Ollama\ollama.exe")
    def test_ollama_detected_when_binary_present(self, mock_which):
        manager = ModelManager()
        self.assertEqual(manager.find_ollama_binary(), r"C:\Users\User\AppData\Local\Programs\Ollama\ollama.exe")
        self.assertTrue(manager.is_ollama_installed())

    @patch("backend.model_manager.httpx.get")
    def test_ollama_unavailable_detection(self, mock_get):
        mock_get.side_effect = httpx.ConnectError("Connection refused")
        manager = ModelManager()
        self.assertFalse(manager.is_ollama_running())

    @patch("backend.model_manager.httpx.get")
    def test_ollama_running_detection(self, mock_get):
        response = MagicMock(status_code=200)
        mock_get.return_value = response
        manager = ModelManager()
        self.assertTrue(manager.is_ollama_running())

    @patch("subprocess.Popen")
    def test_start_ollama_service_success(self, mock_popen):
        manager = ModelManager()
        with patch.object(manager, "find_ollama_binary", return_value="ollama"), \
             patch.object(manager, "is_ollama_running", side_effect=[False, True]):
            success = manager.start_ollama_service(wait_timeout=2.0)
            self.assertTrue(success)
            mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    def test_start_ollama_service_timeout_failure(self, mock_popen):
        manager = ModelManager()
        with patch.object(manager, "find_ollama_binary", return_value="ollama"), \
             patch.object(manager, "is_ollama_running", return_value=False):
            success = manager.start_ollama_service(wait_timeout=0.1)
            self.assertFalse(success)


class ModelDiscoveryAndSelectionTests(unittest.TestCase):
    """Verifies model discovery, formatting, and empty-state guidance."""

    @patch("backend.model_manager.httpx.get")
    def test_empty_model_list_handling(self, mock_get):
        response = MagicMock(status_code=200)
        response.json.return_value = {"models": []}
        mock_get.return_value = response

        manager = ModelManager()
        models = manager.discover_ollama_models()
        self.assertEqual(models, [])

        with self.assertRaises(ValueError):
            manager.validate_ollama_model("any_model", models)

    def test_model_info_formatted_size(self):
        m1 = ModelInfo("qwen3:4b", size=2684354560)  # ~2.5 GB
        self.assertEqual(m1.formatted_size, "2.5 GB")

        m2 = ModelInfo("tiny", size=52428800)  # ~50 MB
        self.assertEqual(m2.formatted_size, "50 MB")

        m3 = ModelInfo("unknown", size=None)
        self.assertEqual(m3.formatted_size, "")

    def test_model_selection_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = Settings(path)
            manager = ModelManager(settings)

            available = [
                ModelInfo("qwen3:4b-instruct-2507-q4_K_M", 2684354560),
                ModelInfo("llama3.2:3b", 2000000000),
            ]

            manager.select_ollama_model("llama3.2:3b", models=available)
            self.assertEqual(settings.get("ollama_model"), "llama3.2:3b")

            reloaded = Settings(path)
            self.assertEqual(reloaded.get("ollama_model"), "llama3.2:3b")


class SetupWizardWorkflowTests(unittest.TestCase):
    """Verifies end-to-end wizard flow, verification, and persistence."""

    def test_successful_setup_flow(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            settings = Settings(settings_path)
            self.assertTrue(settings.needs_setup())

            models = [ModelInfo("qwen3:4b-instruct-2507-q4_K_M", 2500000000)]
            on_complete = MagicMock()

            wizard = SetupWizard.__new__(SetupWizard)
            wizard.settings = settings
            wizard.assistant = MagicMock()
            wizard.on_complete = on_complete
            wizard.model_manager = ModelManager(settings)
            wizard.provider_choice = SimpleNamespace(get=lambda: "ollama")
            wizard.selected_ollama_model = SimpleNamespace(get=lambda: "qwen3:4b-instruct-2507-q4_K_M")
            wizard.openai_endpoint = SimpleNamespace(get=lambda: "http://127.0.0.1:8080/v1")
            wizard.openai_model = SimpleNamespace(get=lambda: "local-model")
            wizard.next_button = MagicMock()
            wizard.back_button = MagicMock()
            wizard.finish_status_label = MagicMock()
            wizard.winfo_exists = MagicMock(return_value=True)
            wizard.safe_after = lambda func: func()

            with patch.object(wizard.model_manager, "is_ollama_running", return_value=True), \
                 patch.object(wizard.model_manager, "discover_ollama_models", return_value=models):

                wizard.finish_setup()
                time.sleep(0.2)

                self.assertTrue(settings.get("setup_completed"))
                self.assertEqual(settings.get("ollama_model"), "qwen3:4b-instruct-2507-q4_K_M")
                self.assertFalse(settings.needs_setup())
                on_complete.assert_called_once()

    def test_failed_setup_and_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            settings = Settings(settings_path)
            self.assertTrue(settings.needs_setup())

            on_complete = MagicMock()

            wizard = SetupWizard.__new__(SetupWizard)
            wizard.settings = settings
            wizard.assistant = MagicMock()
            wizard.on_complete = on_complete
            wizard.model_manager = ModelManager(settings)
            wizard.provider_choice = SimpleNamespace(get=lambda: "ollama")
            wizard.selected_ollama_model = SimpleNamespace(get=lambda: "non-existent-model")
            wizard.openai_endpoint = SimpleNamespace(get=lambda: "http://127.0.0.1:8080/v1")
            wizard.openai_model = SimpleNamespace(get=lambda: "local-model")
            wizard.next_button = MagicMock()
            wizard.back_button = MagicMock()
            wizard.finish_status_label = MagicMock()
            wizard.winfo_exists = MagicMock(return_value=True)
            wizard.safe_after = lambda func: func()

            with patch.object(wizard.model_manager, "is_ollama_running", return_value=True), \
                 patch.object(wizard.model_manager, "discover_ollama_models", return_value=[ModelInfo("other-model")]):

                wizard.finish_setup()
                time.sleep(0.2)

                self.assertFalse(settings.get("setup_completed"))
                self.assertTrue(settings.needs_setup())
                on_complete.assert_not_called()
                wizard.finish_status_label.configure.assert_called()

    def test_openai_compatible_setup_flow(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            settings = Settings(settings_path)
            self.assertTrue(settings.needs_setup())

            on_complete = MagicMock()

            wizard = SetupWizard.__new__(SetupWizard)
            wizard.settings = settings
            wizard.assistant = MagicMock()
            wizard.on_complete = on_complete
            wizard.model_manager = ModelManager(settings)
            wizard.provider_choice = SimpleNamespace(get=lambda: "openai_compatible")
            wizard.selected_ollama_model = SimpleNamespace(get=lambda: "qwen3")
            wizard.openai_endpoint = SimpleNamespace(get=lambda: "http://127.0.0.1:8080/v1")
            wizard.openai_model = SimpleNamespace(get=lambda: "custom-local-model")
            wizard.next_button = MagicMock()
            wizard.back_button = MagicMock()
            wizard.finish_status_label = MagicMock()
            wizard.winfo_exists = MagicMock(return_value=True)
            wizard.safe_after = lambda func: func()

            with patch.object(ModelManager, "validate_openai_compatible", return_value="Connected"):
                wizard.finish_setup()
                time.sleep(0.2)

                self.assertTrue(settings.get("setup_completed"))
                self.assertEqual(settings.get("provider"), "openai_compatible")
                self.assertEqual(settings.get("openai_model"), "custom-local-model")
                self.assertEqual(settings.get("openai_base_url"), "http://127.0.0.1:8080/v1")
                self.assertFalse(settings.needs_setup())
                on_complete.assert_called_once()

    def test_existing_settings_and_memory_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)
            settings_path = data_dir / "settings.json"
            memory_db_path = data_dir / "memory.db"

            memory = Memory(memory_db_path)
            try:
                memory.add("user", "Hello prior conversation")
                memory.add("assistant", "Hello! I remember this.")
            finally:
                memory.close()

            settings = Settings(settings_path)
            settings.update(theme="light", temperature=1.5, setup_completed=False)
            settings.save()

            on_complete = MagicMock()

            wizard = SetupWizard.__new__(SetupWizard)
            wizard.settings = settings
            wizard.assistant = MagicMock()
            wizard.on_complete = on_complete
            wizard.model_manager = ModelManager(settings)
            wizard.provider_choice = SimpleNamespace(get=lambda: "ollama")
            wizard.selected_ollama_model = SimpleNamespace(get=lambda: "qwen3:4b-instruct-2507-q4_K_M")
            wizard.openai_endpoint = SimpleNamespace(get=lambda: "http://127.0.0.1:8080/v1")
            wizard.openai_model = SimpleNamespace(get=lambda: "local-model")
            wizard.next_button = MagicMock()
            wizard.back_button = MagicMock()
            wizard.finish_status_label = MagicMock()
            wizard.winfo_exists = MagicMock(return_value=True)
            wizard.safe_after = lambda func: func()

            models = [ModelInfo("qwen3:4b-instruct-2507-q4_K_M", 2500000000)]
            with patch.object(wizard.model_manager, "is_ollama_running", return_value=True), \
                 patch.object(wizard.model_manager, "discover_ollama_models", return_value=models):

                wizard.finish_setup()
                time.sleep(0.2)

                reloaded_settings = Settings(settings_path)
                self.assertEqual(reloaded_settings.get("theme"), "light")
                self.assertEqual(reloaded_settings.get("temperature"), 1.5)
                self.assertTrue(reloaded_settings.get("setup_completed"))

                reloaded_memory = Memory(memory_db_path)
                try:
                    history = reloaded_memory.recent(5)
                    self.assertEqual(len(history), 2)
                    self.assertEqual(history[0]["message"], "Hello prior conversation")
                    self.assertEqual(history[1]["message"], "Hello! I remember this.")
                finally:
                    reloaded_memory.close()


class AppIntegrationTests(unittest.TestCase):
    """Verifies SAIApp setup wizard invocation and completion transition."""

    def test_app_displays_setup_wizard_on_first_run(self):
        from frontend.app import SAIApp

        settings = MagicMock()
        settings.needs_setup.return_value = True
        sidebar = MagicMock()
        container = MagicMock()

        app = SimpleNamespace(
            settings=settings,
            assistant=MagicMock(),
            sidebar=sidebar,
            container=container,
            current_page=None,
            setup_wizard=None,
            finish_first_run_setup=MagicMock(),
        )

        with patch("frontend.app.SetupWizard") as mock_wizard_cls:
            mock_wizard_instance = MagicMock()
            mock_wizard_cls.return_value = mock_wizard_instance

            SAIApp.show_setup_wizard(app)

            sidebar.disable.assert_called_once()
            mock_wizard_cls.assert_called_once()
            mock_wizard_instance.grid.assert_called_once()
            self.assertEqual(app.current_page, mock_wizard_instance)

    def test_app_finish_first_run_setup_restores_chat(self):
        from frontend.app import SAIApp

        sidebar = MagicMock()
        setup_wizard = MagicMock()
        apply_settings = MagicMock()
        change_page = MagicMock()
        finish_startup = MagicMock()

        app = SimpleNamespace(
            sidebar=sidebar,
            setup_wizard=setup_wizard,
            apply_settings=apply_settings,
            change_page=change_page,
            finish_startup=finish_startup,
        )

        SAIApp.finish_first_run_setup(app)

        setup_wizard.grid_remove.assert_called_once()
        setup_wizard.destroy.assert_called_once()
        self.assertIsNone(app.setup_wizard)
        sidebar.enable.assert_called_once()
        apply_settings.assert_called_once()
        change_page.assert_called_once_with("chat")
        finish_startup.assert_called_once()


if __name__ == "__main__":
    unittest.main()

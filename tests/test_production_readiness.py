from __future__ import annotations

import tempfile
import threading
import unittest
import sys
import httpx
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.assistant import Assistant
from backend.file_manager import FileManager
from backend.memory import Memory
from backend.model_manager import ModelInfo, ModelManager
from backend.providers import OpenAICompatibleProvider, ProviderFactory
from backend.identity import SYSTEM_PROMPT
from backend.settings import Settings


class SecurityTests(unittest.TestCase):
    def test_desktop_action_requires_approval(self):
        assistant = Assistant.__new__(Assistant)
        assistant.pending_action = None
        assistant.memory = MagicMock()
        assistant.chat_history = []
        with patch("backend.assistant.DesktopController.open_website", return_value=True) as opener:
            pending = assistant.desktop("open github")
            self.assertIn("Approval required", pending)
            opener.assert_not_called()
            self.assertEqual(assistant.reply("approve"), "Completed: open Github.")
            opener.assert_called_once()

    def test_desktop_action_can_be_cancelled(self):
        assistant = Assistant.__new__(Assistant)
        assistant.pending_action = None
        assistant.memory = MagicMock()
        assistant.chat_history = []
        with patch("backend.assistant.DesktopController.open_website") as opener:
            assistant.desktop("open github")
            self.assertEqual(assistant.reply("cancel"), "Cancelled: open Github.")
            opener.assert_not_called()

    def test_desktop_action_can_be_denied(self):
        assistant = Assistant.__new__(Assistant)
        assistant.pending_action = None
        assistant.memory = MagicMock()
        assistant.chat_history = []
        assistant.desktop("open github")
        self.assertEqual(assistant.reply("deny"), "Cancelled: open Github.")

    def test_file_manager_blocks_unapproved_or_outside_delete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "delete-me.txt"
            target.write_text("x")
            original_roots = FileManager.ALLOWED_ROOTS
            FileManager.ALLOWED_ROOTS = (root,)
            try:
                with self.assertRaises(PermissionError):
                    FileManager.delete(target)
                FileManager.delete(target, approved=True)
                self.assertFalse(target.exists())
                with self.assertRaises(PermissionError):
                    FileManager.read(Path.cwd() / "README.md")
            finally:
                FileManager.ALLOWED_ROOTS = original_roots


class StorageTests(unittest.TestCase):
    def test_memory_serializes_concurrent_connections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.db"
            first, second = Memory(path), Memory(path)
            try:
                threads = [
                    threading.Thread(target=first.add, args=("user", f"first {index}"))
                    for index in range(10)
                ] + [
                    threading.Thread(target=second.add, args=("assistant", f"second {index}"))
                    for index in range(10)
                ]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                self.assertEqual(first.count(), 20)
            finally:
                first.close()
                second.close()

    def test_settings_persist_without_api_key(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = Settings(path)
            settings.update(provider="openai_compatible", openai_base_url="http://127.0.0.1:8080/v1")
            settings.save()
            self.assertEqual(Settings(path).get("provider"), "openai_compatible")
            self.assertNotIn("api_key", path.read_text())

    def test_theme_preference_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = Settings(path)
            settings.update(theme="light")
            settings.save()
            self.assertEqual(Settings(path).get("theme"), "light")


class ProviderTests(unittest.TestCase):
    def test_factory_uses_ollama_by_default_config(self):
        provider = ProviderFactory.create(Settings.DEFAULTS)
        self.assertEqual(provider.__class__.__name__, "OllamaProvider")

    def test_provider_switch_persists(self):
        from backend.llm import LLM
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(Path(directory) / "settings.json")
            LLM(settings).set_provider("openai_compatible")
            self.assertEqual(Settings(settings.path).get("provider"), "openai_compatible")

    @patch("backend.providers.httpx.post")
    def test_openai_compatible_provider_uses_chat_completions(self, post):
        response = MagicMock()
        response.json.return_value = {"choices": [{"message": {"content": " ok "}}]}
        post.return_value = response
        provider = OpenAICompatibleProvider("http://localhost:8080/v1", "local", 0.2, 100)
        self.assertEqual(provider.generate("hello"), "ok")
        self.assertEqual(post.call_args.args[0], "http://localhost:8080/v1/chat/completions")

    def test_ollama_provider_forwards_the_configured_model(self):
        from backend.providers import OllamaProvider
        ollama = MagicMock()
        ollama.Client.return_value.chat.return_value = {"message": {"content": " ok "}}
        with patch.dict(sys.modules, {"ollama": ollama}):
            provider = OllamaProvider("qwen3:4b-instruct-2507-q4_K_M", 0.7, 10, "http://localhost:11434")
            self.assertEqual(provider.generate("hello"), "ok")
        ollama.Client.assert_called_once_with(host="http://localhost:11434")
        self.assertEqual(ollama.Client.return_value.chat.call_args.kwargs["model"], "qwen3:4b-instruct-2507-q4_K_M")

    def test_ollama_request_contains_one_identity_message_and_history(self):
        from backend.providers import OllamaProvider
        ollama = MagicMock()
        ollama.Client.return_value.chat.return_value = {"message": {"content": "ok"}}
        history = [{"role": "user", "message": "Earlier question"}]
        with patch.dict(sys.modules, {"ollama": ollama}):
            OllamaProvider("model", 0.7, 10).generate("Current question", history)
        messages = ollama.Client.return_value.chat.call_args.kwargs["messages"]
        self.assertEqual([item["role"] for item in messages], ["system", "user", "user"])
        self.assertEqual(messages[0]["content"], SYSTEM_PROMPT)
        self.assertEqual(sum(item["role"] == "system" for item in messages), 1)

    def test_openai_compatible_request_contains_identity_message(self):
        response = MagicMock()
        response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        with patch("backend.providers.httpx.post", return_value=response) as post:
            OpenAICompatibleProvider("http://localhost:8080/v1", "local", 0.2, 100).generate("hello")
        self.assertEqual(post.call_args.kwargs["json"]["messages"][0]["content"], SYSTEM_PROMPT)


class ModelManagerTests(unittest.TestCase):
    @patch("backend.model_manager.httpx.get")
    def test_discovers_installed_models(self, get):
        response = MagicMock()
        response.json.return_value = {"models": [{"name": "local", "size": 42, "modified_at": "now"}]}
        get.return_value = response
        models = ModelManager(Settings(Path(tempfile.gettempdir()) / "unused-settings.json")).discover_ollama_models()
        self.assertEqual(models, [ModelInfo("local", 42, "now")])

    @patch("backend.model_manager.httpx.get")
    def test_handles_empty_model_list(self, get):
        response = MagicMock()
        response.json.return_value = {"models": []}
        get.return_value = response
        self.assertEqual(ModelManager(Settings(Path(tempfile.gettempdir()) / "unused-settings.json")).discover_ollama_models(), [])

    @patch("backend.model_manager.httpx.get", side_effect=httpx.ConnectError("offline"))
    def test_ollama_unavailable_reports_connection_error(self, get):
        with self.assertRaises(RuntimeError):
            ModelManager(Settings(Path(tempfile.gettempdir()) / "unused-settings.json")).discover_ollama_models()

    def test_selection_persists_and_updates_shared_assistant(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(Path(directory) / "settings.json")
            shared_settings = Settings(Path(directory) / "assistant-settings.json")
            assistant = SimpleNamespace(llm=SimpleNamespace(settings=shared_settings))
            manager = ModelManager(settings)
            manager.select_ollama_model("local", assistant, [ModelInfo("local")])
            self.assertEqual(Settings(settings.path).get("ollama_model"), "local")
            self.assertEqual(assistant.llm.settings.get("ollama_model"), "local")

    def test_selection_rejects_undiscovered_model(self):
        manager = ModelManager(Settings(Path(tempfile.gettempdir()) / "unused-settings.json"))
        with self.assertRaises(ValueError):
            manager.select_ollama_model("missing", models=[])

    @patch("backend.model_manager.httpx.get", side_effect=httpx.ConnectError("offline"))
    def test_invalid_openai_compatible_endpoint_reports_error(self, get):
        with self.assertRaises(RuntimeError):
            ModelManager(Settings(Path(tempfile.gettempdir()) / "unused-settings.json")).validate_openai_compatible()


class IdentityTests(unittest.TestCase):
    def test_assistant_identifies_as_sai(self):
        assistant = Assistant.__new__(Assistant)
        assistant.memory = MagicMock()
        assistant.chat_history = []
        assistant.pending_action = None
        self.assertIn("Scalable AI Interface", assistant.reply("What is sAI?"))

    def test_assistant_forwards_prior_history_to_llm(self):
        assistant = Assistant.__new__(Assistant)
        assistant.memory = MagicMock()
        assistant.profile = MagicMock()
        assistant.search = MagicMock()
        assistant.llm = MagicMock()
        assistant.llm.generate.return_value = "response"
        assistant.chat_history = [{"role": "user", "message": "Earlier", "time": "00:00:00"}]
        assistant.pending_action = None

        assistant.reply("Current")

        self.assertEqual(assistant.llm.generate.call_args.kwargs["history"][0]["message"], "Earlier")


class UIRuntimeCallbackTests(unittest.TestCase):
    @patch("frontend.app.ctk.set_appearance_mode")
    def test_restored_app_applies_settings_to_shared_assistant(self, set_appearance_mode):
        from frontend.app import SAIApp
        settings = MagicMock()
        assistant = MagicMock()
        settings.llm_config.return_value = {"provider": "ollama"}
        settings.get.return_value = "dark"
        app = SimpleNamespace(settings=settings, assistant=assistant)

        SAIApp.apply_settings(app)

        self.assertEqual(assistant.llm.settings.data, {"provider": "ollama"})
        set_appearance_mode.assert_called_once_with("dark")

    def test_restored_sidebar_navigation_swaps_pages(self):
        from frontend.app import SAIApp
        previous, target = MagicMock(), MagicMock()
        app = SimpleNamespace(
            pages={"chat": target}, current_page=previous, sidebar=MagicMock()
        )

        SAIApp.change_page(app, "chat")

        previous.grid_remove.assert_called_once()
        target.grid.assert_called_once()
        app.sidebar.highlight.assert_called_once_with("chat")

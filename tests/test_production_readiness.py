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

    @patch("backend.providers.httpx.post", side_effect=httpx.ConnectError("offline"))
    def test_openai_compatible_connection_error_identifies_endpoint(self, post):
        provider = OpenAICompatibleProvider("http://127.0.0.1:8080/v1", "local", 0.2, 100)
        with self.assertRaisesRegex(RuntimeError, "127.0.0.1:8080/v1/chat/completions"):
            provider.generate("hello")


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

    def test_typed_model_validation_rejects_unknown_model(self):
        with self.assertRaises(ValueError):
            ModelManager.validate_ollama_model("typo", [ModelInfo("local")])

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

    def test_chat_first_startup_defers_optional_and_data_pages(self):
        from frontend.app import SAIApp
        chat = MagicMock()
        voice_page = MagicMock()
        memory_page = MagicMock()
        search_page = MagicMock()
        page = MagicMock()
        vision = MagicMock(return_value=page)
        with patch("frontend.app.ChatPanel", return_value=chat), \
             patch("frontend.app.VoicePage", return_value=voice_page) as voice, \
             patch("frontend.app.MemoryPage", return_value=memory_page) as memory, \
             patch("frontend.app.SearchPage", return_value=search_page) as search, \
             patch("frontend.app.SettingsPage", return_value=MagicMock()), \
             patch("frontend.app.AboutPage", return_value=MagicMock()), \
             patch("frontend.app.VisionPage", vision):
            app = SimpleNamespace(container=MagicMock(), assistant=MagicMock(), settings=MagicMock(), apply_settings=MagicMock())
            SAIApp.create_pages(app)
            vision.assert_not_called()
            voice.assert_not_called()
            memory.assert_not_called()
            search.assert_not_called()
            self.assertNotIn("vision", app.pages)
            self.assertNotIn("voice", app.pages)
            self.assertNotIn("memory", app.pages)
            self.assertNotIn("search", app.pages)
            self.assertEqual(set(app.page_factories), {"voice", "vision", "memory", "search"})

            app.page_factories["memory"]()

        memory.assert_called_once_with(app.container, memory=app.assistant.memory)

    def test_deferred_page_navigation_keeps_sidebar_flow(self):
        from frontend.app import SAIApp
        page = MagicMock()
        app = SimpleNamespace(
            container=MagicMock(),
            assistant=MagicMock(),
            pages={},
            page_factories={"memory": lambda: page},
            current_page=MagicMock(),
            sidebar=MagicMock(),
        )

        SAIApp.change_page(app, "memory")

        self.assertIs(app.current_page, page)
        app.sidebar.highlight.assert_called_once_with("memory")

    def test_voice_sidebar_navigation_is_disabled_in_release_ui(self):
        from frontend.sidebar import Sidebar
        callback = MagicMock()
        sidebar = Sidebar.__new__(Sidebar)
        sidebar.callback = callback
        voice_btn = MagicMock()
        other_btn = MagicMock()
        sidebar.buttons = {"voice": voice_btn, "chat": other_btn}

        sidebar.change_page("voice")
        callback.assert_not_called()

        sidebar.enable()
        other_btn.configure.assert_called_once_with(state="normal")
        voice_btn.configure.assert_not_called()

    def test_change_page_voice_does_not_initialize_voice_page(self):
        from frontend.app import SAIApp
        voice_factory = MagicMock()
        current = MagicMock()
        app = SimpleNamespace(
            pages={},
            page_factories={"voice": voice_factory},
            current_page=current,
            sidebar=MagicMock(),
        )

        SAIApp.change_page(app, "voice")

        voice_factory.assert_not_called()
        self.assertIs(app.current_page, current)


class SettingsSaveTests(unittest.TestCase):
    def test_invalid_typed_ollama_model_is_not_persisted(self):
        from frontend.settings import SettingsPage
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(Path(directory) / "settings.json")
            original = settings.get("ollama_model")
            status = MagicMock()
            page = SimpleNamespace(
                settings=settings,
                status=status,
                model_manager=MagicMock(),
            )
            page.model_manager.discover_ollama_models.return_value = [ModelInfo("installed")]
            page.model_manager.validate_ollama_model.side_effect = ValueError("invalid model")
            page.after = lambda _delay, callback: callback()

            SettingsPage._validate_and_save_ollama(page, {"ollama_model": "typo"})

            self.assertEqual(settings.get("ollama_model"), original)
            status.configure.assert_called_with(text="invalid model")

    def test_validated_model_is_saved_after_discovery(self):
        from frontend.settings import SettingsPage
        saved = []
        page = SimpleNamespace(status=MagicMock(), model_manager=MagicMock())
        page.model_manager.discover_ollama_models.return_value = [ModelInfo("installed")]
        page.model_manager.validate_ollama_model.return_value = "installed"
        page.after = lambda _delay, callback: callback()
        page._save_values = lambda values: saved.append(values.copy())

        SettingsPage._validate_and_save_ollama(page, {"ollama_model": "installed"})

        self.assertEqual(saved, [{"ollama_model": "installed"}])


class DeferredMemoryTests(unittest.TestCase):
    def test_history_query_is_deferred_until_requested(self):
        from frontend.memory import MemoryPage
        memory = MagicMock()
        page = MemoryPage.__new__(MemoryPage)
        page.memory = memory
        page.text = MagicMock()
        page._load_token = 0
        thread = MagicMock()
        with patch("frontend.memory.threading.Thread", return_value=thread):
            MemoryPage.load_history(page)

        memory.all.assert_not_called()
        thread.start.assert_called_once()
        self.assertIn("Loading conversation history...", str(page.text.insert.call_args))

    def test_requested_history_renders_in_after_batches(self):
        from frontend.memory import MemoryPage
        history = [
            {"timestamp": "2026-11-04T10:00:00", "role": "user", "message": f"message {index}"}
            for index in range(55)
        ]
        page = MemoryPage.__new__(MemoryPage)
        page.memory = MagicMock()
        page.text = MagicMock()
        page._load_token = 1
        scheduled_delays = []

        def run_after(delay, callback):
            scheduled_delays.append(delay)
            callback()

        page.after = run_after
        MemoryPage._begin_history_render(page, history, 1)

        rendered = "".join(
            call.args[1] for call in page.text.insert.call_args_list if len(call.args) > 1
        )
        self.assertIn("message 0", rendered)
        self.assertIn("message 54", rendered)
        self.assertIn(1, scheduled_delays)

    def test_shared_assistant_memory_is_used_by_memory_and_search_factories(self):
        from frontend.app import SAIApp
        shared_memory = MagicMock()
        assistant = SimpleNamespace(memory=shared_memory)
        memory_page, search_page = MagicMock(), MagicMock()
        app = SimpleNamespace(
            container=MagicMock(),
            assistant=assistant,
            settings=MagicMock(),
            apply_settings=MagicMock(),
        )
        with patch("frontend.app.ChatPanel"), \
             patch("frontend.app.SettingsPage"), \
             patch("frontend.app.AboutPage"), \
             patch("frontend.app.MemoryPage", return_value=memory_page) as memory, \
             patch("frontend.app.SearchPage", return_value=search_page) as search:
            SAIApp.create_pages(app)
            app.page_factories["memory"]()
            app.page_factories["search"]()

        memory.assert_called_once_with(app.container, memory=shared_memory)
        search.assert_called_once_with(app.container, memory=shared_memory)


class VoiceInitializationTests(unittest.TestCase):
    def test_voice_engine_completion_enables_existing_voice_controls(self):
        from frontend.voice import VoicePage
        page = VoicePage.__new__(VoicePage)
        page.status = MagicMock()
        page.listen_button = MagicMock()
        engine = MagicMock()

        VoicePage.finish_engine_initialization(page, engine, None)

        self.assertIs(page.engine, engine)
        self.assertIsNone(page.unavailable_reason)
        page.listen_button.configure.assert_called_once_with(state="normal")

    def test_voice_engine_failure_keeps_listening_disabled(self):
        from frontend.voice import VoicePage
        page = VoicePage.__new__(VoicePage)
        page.status = MagicMock()
        page.listen_button = MagicMock()

        VoicePage.finish_engine_initialization(page, None, "Install requirements-voice.txt to enable voice.")

        self.assertIsNone(page.engine)
        page.listen_button.configure.assert_not_called()


class LauncherTests(unittest.TestCase):
    def test_launcher_uses_selected_ollama_settings(self):
        import run
        settings = SimpleNamespace(llm_config=lambda: {
            "provider": "ollama",
            "ollama_base_url": "http://127.0.0.1:11435",
            "ollama_model": "selected-model",
        })
        with patch("run.ensure_ollama", return_value=True) as ensure_ollama:
            self.assertTrue(run.ensure_provider(settings))
        ensure_ollama.assert_called_once_with("http://127.0.0.1:11435", "selected-model")

    def test_launcher_does_not_require_ollama_for_openai_compatible_settings(self):
        import run
        settings = SimpleNamespace(llm_config=lambda: {
            "provider": "openai_compatible",
            "openai_base_url": "http://127.0.0.1:8080/v1",
            "openai_model": "local-model",
        })
        with patch("run.ensure_ollama") as ensure_ollama:
            self.assertTrue(run.ensure_provider(settings))
        ensure_ollama.assert_not_called()


class PackagingDocumentationTests(unittest.TestCase):
    def test_web_search_dependencies_are_optional_and_documented(self):
        root = Path(__file__).resolve().parents[1]
        requirements = (root / "requirements-search.txt").read_text(encoding="utf-8")
        self.assertIn("requests", requirements)
        self.assertIn("beautifulsoup4", requirements)
        self.assertIn("duckduckgo-search", requirements)
        self.assertIn("WINDOWS_INSTALLATION.md", (root / "README.md").read_text(encoding="utf-8"))

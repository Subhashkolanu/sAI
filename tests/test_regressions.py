"""Regression tests for repaired application entry points and storage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.memory import Memory
from backend.profile_memory import ProfileMemory


class MemorySearchTests(unittest.TestCase):
    def test_search_returns_matching_conversation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            memory = Memory(Path(temporary_directory) / "memory.db")
            try:
                memory.add("user", "find the audit record")

                self.assertEqual(
                    memory.search("audit"),
                    [
                        {
                            "role": "user",
                            "message": "find the audit record",
                            "timestamp": memory.all()[0]["timestamp"],
                        }
                    ],
                )
            finally:
                memory.close()


class ProfileMemoryTests(unittest.TestCase):
    def test_custom_path_is_persisted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "profile.json"
            profile = ProfileMemory(path)
            profile.remember("name", "Ada")

            self.assertEqual(ProfileMemory(path).recall("name"), "Ada")


class TerminalRoutingTests(unittest.TestCase):
    @patch("backend.main.Assistant")
    def test_non_command_is_sent_to_assistant(self, assistant_class):
        assistant = MagicMock()
        assistant.reply.return_value = "assistant response"
        assistant_class.return_value = assistant

        from backend.main import SAI

        app = SAI()
        app.process("hello")

        assistant.reply.assert_called_once_with("hello")

    @patch("backend.main.Assistant")
    def test_exit_command_does_not_call_assistant(self, assistant_class):
        assistant = MagicMock()
        assistant_class.return_value = assistant

        from backend.main import SAI

        app = SAI()
        app.process("exit")

        self.assertFalse(app.running)
        assistant.reply.assert_not_called()

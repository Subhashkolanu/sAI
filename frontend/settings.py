"""
=========================================================
sAI V1 - Settings Page
=========================================================
"""

from __future__ import annotations

import threading
import customtkinter as ctk

from backend.config import (
    ASSISTANT_NAME,
    VERSION,
    DEFAULT_PROVIDER,
    OLLAMA_MODEL,
    OPENAI_MODEL,
)
from backend.settings import Settings
from backend.model_manager import ModelManager


class SettingsPage(ctk.CTkFrame):

    def __init__(self, master, settings=None, assistant=None, on_save=None, on_run_setup=None):

        super().__init__(master)

        self.settings = settings or Settings()
        self.assistant = assistant
        self.model_manager = ModelManager(self.settings)
        self.installed_models = []
        self.on_save = on_save
        self.on_run_setup = on_run_setup

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Settings",
            font=("Segoe UI", 24, "bold"),
        )

        title.pack(pady=(20, 10))

        info = ctk.CTkFrame(self)

        info.pack(fill="x", padx=20, pady=10)

        values = [("Assistant", ASSISTANT_NAME), ("Version", VERSION)]

        for key, value in values:

            row = ctk.CTkFrame(info)

            row.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                row,
                text=key,
                width=180,
                anchor="w",
            ).pack(side="left", padx=5)

            ctk.CTkLabel(
                row,
                text=str(value),
                anchor="w",
            ).pack(side="left", padx=5)

        self.provider = ctk.StringVar(value=self.settings.get("provider"))
        self.model = ctk.StringVar(value=self.settings.get("ollama_model"))
        self.openai_model = ctk.StringVar(value=self.settings.get("openai_model"))
        self.endpoint = ctk.StringVar(value=self.settings.get("openai_base_url"))
        self.theme = ctk.StringVar(value=self.settings.get("theme"))
        self.installed_model = ctk.StringVar(value=self.settings.get("ollama_model"))

        ctk.CTkOptionMenu(
            self,
            values=["ollama", "openai_compatible"],
            variable=self.provider,
        ).pack(pady=5)
        ctk.CTkOptionMenu(self, values=["dark", "light", "system"], variable=self.theme).pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.model, placeholder_text="Ollama model").pack(fill="x", padx=20, pady=5)
        models_row = ctk.CTkFrame(self)
        models_row.pack(fill="x", padx=20, pady=5)
        self.model_selector = ctk.CTkOptionMenu(models_row, values=[self.installed_model.get()], variable=self.installed_model, command=self.select_installed_model)
        self.model_selector.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(models_row, text="Refresh models", width=120, command=self.refresh_models).pack(side="right")
        self.models_info = ctk.CTkLabel(self, text="Refresh to list installed Ollama models.", anchor="w")
        self.models_info.pack(fill="x", padx=20, pady=(0, 5))
        ctk.CTkEntry(self, textvariable=self.openai_model, placeholder_text="OpenAI-compatible model").pack(fill="x", padx=20, pady=5)
        ctk.CTkEntry(self, textvariable=self.endpoint, placeholder_text="OpenAI-compatible endpoint").pack(fill="x", padx=20, pady=5)
        self.status = ctk.CTkLabel(self, text="API keys remain in environment variables.")
        self.status.pack(pady=5)
        ctk.CTkButton(self, text="Test connection", command=self.test_connection).pack(pady=(0, 5))
        ctk.CTkButton(self, text="Save Settings", command=self.save).pack(pady=10)

        if self.on_run_setup is not None:
            ctk.CTkButton(
                self,
                text="Run First-Run Setup Wizard",
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray40"),
                command=self.on_run_setup,
            ).pack(pady=(0, 15))

    def refresh_models(self):
        self.status.configure(text="Checking Ollama models...")
        threading.Thread(target=self._discover_models, daemon=True).start()

    def _discover_models(self):
        try:
            models = self.model_manager.discover_ollama_models()
            self.after(0, lambda: self._show_models(models))
        except RuntimeError as exc:
            self.after(0, lambda: self.status.configure(text=str(exc)))

    def _show_models(self, models):
        self.installed_models = models
        names = [model.name for model in models]
        self.model_selector.configure(values=names or ["No models found"])
        if not names:
            self.models_info.configure(text="Ollama connected, but no installed models were reported.")
            self.status.configure(text="No Ollama models found.")
            return
        selected = self.settings.get("ollama_model")
        self.installed_model.set(selected if selected in names else names[0])
        details = []
        for model in models:
            size = f" ({model.size / (1024 ** 3):.1f} GB)" if model.size is not None else ""
            details.append(f"{model.name}{size}")
        self.models_info.configure(text="Installed: " + ", ".join(details))
        self.status.configure(text=f"Found {len(models)} installed Ollama model(s).")

    def select_installed_model(self, name):
        if name == "No models found":
            return
        try:
            self.model_manager.select_ollama_model(name, self.assistant, self.installed_models)
            self.model.set(name)
            self.status.configure(text=f"Using {name} for new requests.")
        except ValueError as exc:
            self.status.configure(text=str(exc))

    def test_connection(self):
        self.status.configure(text="Testing provider connection...")
        threading.Thread(target=self._test_connection, daemon=True).start()

    def _test_connection(self):
        try:
            if self.provider.get() == "ollama":
                count = len(self.model_manager.discover_ollama_models())
                message = f"Ollama connected ({count} installed model(s))."
            else:
                message = f"OpenAI-compatible endpoint: {self.model_manager.validate_openai_compatible()}."
            self.after(0, lambda: self.status.configure(text=message))
        except RuntimeError as exc:
            self.after(0, lambda: self.status.configure(text=str(exc)))

    def save(self):
        values = {
            "provider": self.provider.get(),
            "ollama_model": self.model.get().strip(),
            "openai_model": self.openai_model.get().strip(),
            "openai_base_url": self.endpoint.get().strip(),
            "theme": self.theme.get(),
        }
        if values["provider"] == "ollama":
            self.status.configure(text="Validating the selected Ollama model...")
            threading.Thread(target=self._validate_and_save_ollama, args=(values,), daemon=True).start()
            return
        self._save_values(values)

    def _validate_and_save_ollama(self, values):
        try:
            models = self.model_manager.discover_ollama_models()
            values["ollama_model"] = self.model_manager.validate_ollama_model(
                values["ollama_model"], models
            )
        except (RuntimeError, ValueError) as exc:
            self.after(0, lambda: self.status.configure(text=str(exc)))
            return
        self.after(0, lambda: self._save_values(values))

    def _save_values(self, values):
        try:
            self.settings.update(**values)
            self.settings.save()
            if self.assistant is not None:
                self.assistant.llm.settings.data = self.settings.llm_config()
            self.status.configure(text="Settings saved. New chats use these settings.")
            if self.on_save:
                self.on_save()
        except ValueError as exc:
            self.status.configure(text=str(exc))


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("700x500")

    SettingsPage(app).pack(fill="both", expand=True)

    app.mainloop()

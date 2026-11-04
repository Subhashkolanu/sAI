"""
=========================================================
sAI V1 - First-Run Setup Wizard
=========================================================
Accessible, non-technical onboarding experience for new users.
=========================================================
"""

from __future__ import annotations

import os
import sys
import threading
import webbrowser
from pathlib import Path

import customtkinter as ctk

from backend.config import (
    ASSISTANT_NAME,
    DATA_DIR,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)
from backend.model_manager import ModelInfo, ModelManager
from backend.settings import Settings

RECOMMENDED_OLLAMA_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
OLLAMA_DOWNLOAD_URL = "https://ollama.com/download"


class SetupWizard(ctk.CTkFrame):
    """Four-step first-run onboarding wizard."""

    def __init__(self, master, settings: Settings | None = None, assistant=None, on_complete=None):
        super().__init__(master)
        self.settings = settings or Settings()
        self.assistant = assistant
        self.on_complete = on_complete
        self.model_manager = ModelManager(self.settings)

        self.current_step = 1
        self.is_checking = False

        # State tracking
        self.provider_choice = ctk.StringVar(value="ollama")
        self.selected_ollama_model = ctk.StringVar(value=self.settings.get("ollama_model") or RECOMMENDED_OLLAMA_MODEL)
        self.openai_endpoint = ctk.StringVar(value=self.settings.get("openai_base_url") or OPENAI_BASE_URL)
        self.openai_model = ctk.StringVar(value=self.settings.get("openai_model") or OPENAI_MODEL)

        self.discovered_models: list[ModelInfo] = []
        self.ollama_status: str = "unknown"  # "checking", "connected", "stopped", "missing"
        self.ollama_error_message: str = ""

        self.build_ui()
        self.show_step(1)

    # --------------------------------------------------
    # UI Structure
    # --------------------------------------------------

    def build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Frame (Persistent across all steps)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        title_label = ctk.CTkLabel(
            self.header_frame,
            text=f"{ASSISTANT_NAME} — Scalable AI Interface",
            font=("Segoe UI", 24, "bold"),
        )
        title_label.pack(anchor="w")

        motto_label = ctk.CTkLabel(
            self.header_frame,
            text="Simple AI for everyone, without charge.",
            font=("Segoe UI", 13, "italic"),
            text_color=("gray40", "gray70"),
        )
        motto_label.pack(anchor="w", pady=(2, 10))

        # Step indicator pills
        self.steps_bar = ctk.CTkFrame(self.header_frame, height=36, fg_color=("gray85", "gray20"), corner_radius=8)
        self.steps_bar.pack(fill="x", pady=(5, 5))

        self.step_indicators: list[ctk.CTkLabel] = []
        step_titles = ["1. Welcome", "2. AI Engine", "3. Model Selection", "4. Ready"]
        for idx, title in enumerate(step_titles, start=1):
            lbl = ctk.CTkLabel(
                self.steps_bar,
                text=title,
                font=("Segoe UI", 12, "bold" if idx == 1 else "normal"),
                text_color=("#1F6AA5", "#3B8ED0") if idx == 1 else ("gray50", "gray60"),
            )
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=4)
            self.step_indicators.append(lbl)

        # Content Frame (Swapped per step)
        self.content_container = ctk.CTkFrame(self, corner_radius=10)
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Footer Frame (Navigation buttons)
        self.footer_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 20))

        self.back_button = ctk.CTkButton(
            self.footer_frame,
            text="← Back",
            width=110,
            height=36,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self.prev_step,
        )
        self.back_button.pack(side="left")

        self.status_footer = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=("Segoe UI", 12),
            text_color=("gray40", "gray65"),
        )
        self.status_footer.pack(side="left", padx=20)

        self.next_button = ctk.CTkButton(
            self.footer_frame,
            text="Next →",
            width=130,
            height=36,
            command=self.next_step,
        )
        self.next_button.pack(side="right")

    def update_step_indicators(self, step_number: int):
        for idx, lbl in enumerate(self.step_indicators, start=1):
            if idx == step_number:
                lbl.configure(
                    font=("Segoe UI", 12, "bold"),
                    text_color=("#1F6AA5", "#3B8ED0"),
                )
            elif idx < step_number:
                lbl.configure(
                    font=("Segoe UI", 12),
                    text_color=("#2CC985", "#2CC985"),
                )
            else:
                lbl.configure(
                    font=("Segoe UI", 12),
                    text_color=("gray50", "gray60"),
                )

    def safe_after(self, func):
        try:
            if self.winfo_exists():
                self.after(0, func)
        except Exception:
            pass

    # --------------------------------------------------
    # Step Controller
    # --------------------------------------------------

    def show_step(self, step: int):
        self.current_step = step
        self.update_step_indicators(step)
        self.status_footer.configure(text="")

        # Clear container
        for widget in self.content_container.winfo_children():
            widget.destroy()

        if step == 1:
            self.render_step_1_welcome()
        elif step == 2:
            self.render_step_2_engine()
        elif step == 3:
            self.render_step_3_models()
        elif step == 4:
            self.render_step_4_finish()

    def prev_step(self):
        if self.current_step > 1:
            self.show_step(self.current_step - 1)

    def next_step(self):
        if self.current_step < 4:
            self.show_step(self.current_step + 1)

    # --------------------------------------------------
    # Step 1: Welcome
    # --------------------------------------------------

    def render_step_1_welcome(self):
        self.back_button.configure(state="disabled")
        self.next_button.configure(text="Begin Setup →", state="normal", command=lambda: self.show_step(2))

        panel = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        panel.pack(fill="both", expand=True, padx=25, pady=25)

        heading = ctk.CTkLabel(
            panel,
            text="Welcome to sAI",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        )
        heading.pack(fill="x", pady=(0, 10))

        intro = ctk.CTkLabel(
            panel,
            text=(
                "sAI (Scalable AI Interface) is a free, local-first desktop AI assistant for Windows.\n"
                "It enables you to chat with powerful modern AI models directly on your PC without "
                "requiring paid cloud subscriptions or sharing your data with external servers."
            ),
            font=("Segoe UI", 13),
            justify="left",
            anchor="w",
            wraplength=700,
        )
        intro.pack(fill="x", pady=(0, 20))

        # Highlight Cards
        cards = [
            ("🔒 100% Local & Private", "Conversations, documents, and memory stay strictly on your machine."),
            ("⚡ Powered by Ollama", "Runs open-source models (like Qwen3) directly on your CPU/GPU at no cost."),
            ("🛠 Simple Desktop Experience", "Pre-configured for Windows 10/11 with zero terminal setup required."),
            ("🌐 Optional Provider Support", "Connect to external OpenAI-compatible local servers whenever desired."),
        ]

        for title, desc in cards:
            card = ctk.CTkFrame(panel, fg_color=("gray90", "gray17"), corner_radius=8)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 13, "bold"), anchor="w").pack(
                anchor="w", padx=15, pady=(8, 2)
            )
            ctk.CTkLabel(
                card,
                text=desc,
                font=("Segoe UI", 12),
                text_color=("gray40", "gray70"),
                anchor="w",
            ).pack(anchor="w", padx=15, pady=(0, 8))

        note = ctk.CTkLabel(
            panel,
            text="Click 'Begin Setup' to verify your local AI runtime and select an installed model.",
            font=("Segoe UI", 12, "italic"),
            text_color=("gray40", "gray60"),
            anchor="w",
        )
        note.pack(fill="x", pady=(20, 0))

    # --------------------------------------------------
    # Step 2: AI Engine (Ollama Detection)
    # --------------------------------------------------

    def render_step_2_engine(self):
        self.back_button.configure(state="normal", command=lambda: self.show_step(1))
        self.next_button.configure(text="Next: Select Model →", state="disabled", command=lambda: self.show_step(3))

        panel = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        panel.pack(fill="both", expand=True, padx=25, pady=20)

        heading = ctk.CTkLabel(
            panel,
            text="Step 2: Connect AI Engine",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        )
        heading.pack(fill="x", pady=(0, 5))

        desc = ctk.CTkLabel(
            panel,
            text="sAI uses Ollama to run intelligence models locally on your computer.",
            font=("Segoe UI", 13),
            anchor="w",
        )
        desc.pack(fill="x", pady=(0, 15))

        # Status Display Box
        self.engine_card = ctk.CTkFrame(panel, corner_radius=10)
        self.engine_card.pack(fill="x", pady=10)

        self.engine_icon_label = ctk.CTkLabel(self.engine_card, text="⏳", font=("Segoe UI", 24))
        self.engine_icon_label.pack(side="left", padx=18, pady=15)

        info_box = ctk.CTkFrame(self.engine_card, fg_color="transparent")
        info_box.pack(side="left", fill="both", expand=True, pady=12)

        self.engine_status_title = ctk.CTkLabel(
            info_box,
            text="Checking Ollama...",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        self.engine_status_title.pack(fill="x")

        self.engine_status_desc = ctk.CTkLabel(
            info_box,
            text="Verifying local service at http://127.0.0.1:11434...",
            font=("Segoe UI", 12),
            text_color=("gray40", "gray70"),
            anchor="w",
            wraplength=520,
        )
        self.engine_status_desc.pack(fill="x", pady=(2, 0))

        # Contextual Action Area
        self.action_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=10)

        # Advanced / OpenAI-compatible Toggle
        advanced_frame = ctk.CTkFrame(panel, fg_color="transparent")
        advanced_frame.pack(fill="x", pady=(20, 5))

        self.use_openai_var = ctk.BooleanVar(value=(self.provider_choice.get() == "openai_compatible"))
        openai_chk = ctk.CTkCheckBox(
            advanced_frame,
            text="Advanced: Use custom OpenAI-compatible local server instead (e.g. LM Studio, vLLM)",
            variable=self.use_openai_var,
            command=self._on_provider_toggle,
        )
        openai_chk.pack(anchor="w")

        # OpenAI Configuration Fields (hidden by default)
        self.openai_frame = ctk.CTkFrame(panel, fg_color=("gray90", "gray17"), corner_radius=8)
        ctk.CTkLabel(
            self.openai_frame,
            text="OpenAI-Compatible Local Endpoint:",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(10, 2))
        endpoint_entry = ctk.CTkEntry(self.openai_frame, textvariable=self.openai_endpoint, placeholder_text="http://127.0.0.1:1234/v1")
        endpoint_entry.pack(fill="x", padx=15, pady=2)

        ctk.CTkLabel(
            self.openai_frame,
            text="Model Identifier:",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(8, 2))
        model_entry = ctk.CTkEntry(self.openai_frame, textvariable=self.openai_model, placeholder_text="local-model")
        model_entry.pack(fill="x", padx=15, pady=2)

        test_btn = ctk.CTkButton(
            self.openai_frame,
            text="Test Custom Endpoint",
            width=160,
            command=self._test_custom_endpoint,
        )
        test_btn.pack(anchor="w", padx=15, pady=(10, 10))

        if self.use_openai_var.get():
            self.openai_frame.pack(fill="x", pady=10)

        # Trigger automatic Ollama detection on entering Step 2
        self.check_ollama_engine()

    def _on_provider_toggle(self):
        if self.use_openai_var.get():
            self.openai_frame.pack(fill="x", pady=10)
            self.provider_choice.set("openai_compatible")
            self.next_button.configure(state="normal")
        else:
            self.openai_frame.pack_forget()
            self.provider_choice.set("ollama")
            if self.ollama_status == "connected":
                self.next_button.configure(state="normal")
            else:
                self.next_button.configure(state="disabled")

    def check_ollama_engine(self):
        """Asynchronously checks whether Ollama is installed and running."""
        if self.is_checking:
            return
        self.is_checking = True
        self.engine_icon_label.configure(text="⏳")
        self.engine_status_title.configure(text="Checking Ollama Service...")
        self.engine_status_desc.configure(text="Verifying connection to Ollama at http://127.0.0.1:11434...")
        self.next_button.configure(state="disabled")

        for child in self.action_frame.winfo_children():
            child.destroy()

        threading.Thread(target=self._run_ollama_detection, daemon=True).start()

    def _run_ollama_detection(self):
        running = self.model_manager.is_ollama_running()
        if running:
            self.safe_after(self._apply_ollama_connected)
            return

        installed = self.model_manager.is_ollama_installed()
        if installed:
            self.safe_after(self._apply_ollama_stopped)
        else:
            self.safe_after(self._apply_ollama_missing)

    def _apply_ollama_connected(self):
        self.is_checking = False
        self.ollama_status = "connected"
        self.engine_icon_label.configure(text="✓", text_color="#2CC985")
        self.engine_status_title.configure(text="Ollama is Running and Ready", text_color="#2CC985")
        self.engine_status_desc.configure(
            text="Connected to local service at http://127.0.0.1:11434. Ready to select a model."
        )

        for child in self.action_frame.winfo_children():
            child.destroy()

        ctk.CTkButton(
            self.action_frame,
            text="🔄 Re-check Connection",
            width=160,
            command=self.check_ollama_engine,
        ).pack(side="left")

        if not self.use_openai_var.get():
            self.next_button.configure(state="normal")

    def _apply_ollama_stopped(self):
        self.is_checking = False
        self.ollama_status = "stopped"
        self.engine_icon_label.configure(text="⚠", text_color="#FFA000")
        self.engine_status_title.configure(text="Ollama is Installed, but Not Running", text_color="#FFA000")
        self.engine_status_desc.configure(
            text="The Ollama binary was detected on your PC, but the background service is not running."
        )

        for child in self.action_frame.winfo_children():
            child.destroy()

        start_btn = ctk.CTkButton(
            self.action_frame,
            text="▶ Start Ollama Service",
            width=180,
            command=self._start_service,
        )
        start_btn.pack(side="left", padx=(0, 10))

        retry_btn = ctk.CTkButton(
            self.action_frame,
            text="🔄 Retry Connection",
            width=150,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self.check_ollama_engine,
        )
        retry_btn.pack(side="left")

        if not self.use_openai_var.get():
            self.next_button.configure(state="disabled")

    def _apply_ollama_missing(self):
        self.is_checking = False
        self.ollama_status = "missing"
        self.engine_icon_label.configure(text="❌", text_color="#E57373")
        self.engine_status_title.configure(text="Ollama Not Detected", text_color="#E57373")
        self.engine_status_desc.configure(
            text=(
                "Ollama is required to run local AI models privately without API charges. "
                "Download and run the free Windows installer from the official website."
            )
        )

        for child in self.action_frame.winfo_children():
            child.destroy()

        download_btn = ctk.CTkButton(
            self.action_frame,
            text="🌐 Download Ollama (ollama.com)",
            width=220,
            command=lambda: webbrowser.open(OLLAMA_DOWNLOAD_URL),
        )
        download_btn.pack(side="left", padx=(0, 10))

        check_btn = ctk.CTkButton(
            self.action_frame,
            text="🔄 Check Again",
            width=130,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self.check_ollama_engine,
        )
        check_btn.pack(side="left")

        if not self.use_openai_var.get():
            self.next_button.configure(state="disabled")

    def _start_service(self):
        self.engine_status_title.configure(text="Starting Ollama Service...")
        self.engine_status_desc.configure(text="Launching ollama serve in the background, please wait...")
        for child in self.action_frame.winfo_children():
            child.configure(state="disabled")

        def task():
            success = self.model_manager.start_ollama_service(wait_timeout=10.0)
            if success:
                self.safe_after(self._apply_ollama_connected)
            else:
                self.safe_after(self._apply_ollama_stopped)

        threading.Thread(target=task, daemon=True).start()

    def _test_custom_endpoint(self):
        endpoint = self.openai_endpoint.get().strip()
        model = self.openai_model.get().strip()
        if not endpoint:
            self.status_footer.configure(text="Endpoint URL cannot be empty.", text_color="#E57373")
            return

        self.status_footer.configure(text="Testing custom endpoint...", text_color=("gray40", "gray70"))

        def task():
            try:
                temp_settings = Settings()
                temp_settings.update(openai_base_url=endpoint, openai_model=model)
                msg = ModelManager(temp_settings).validate_openai_compatible()
                self.safe_after(lambda: self._on_custom_endpoint_success(msg))
            except Exception as exc:
                self.safe_after(lambda: self._on_custom_endpoint_error(str(exc)))

        threading.Thread(target=task, daemon=True).start()

    def _on_custom_endpoint_success(self, msg: str):
        self.status_footer.configure(text=f"✓ Endpoint verified: {msg}", text_color="#2CC985")
        self.next_button.configure(state="normal")

    def _on_custom_endpoint_error(self, err: str):
        self.status_footer.configure(text=f"Connection failed: {err}", text_color="#E57373")

    # --------------------------------------------------
    # Step 3: Model Selection
    # --------------------------------------------------

    def render_step_3_models(self):
        self.back_button.configure(state="normal", command=lambda: self.show_step(2))
        self.next_button.configure(text="Next: Ready →", state="disabled", command=lambda: self.show_step(4))

        panel = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        panel.pack(fill="both", expand=True, padx=25, pady=20)

        heading = ctk.CTkLabel(
            panel,
            text="Step 3: Select an AI Model",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        )
        heading.pack(fill="x", pady=(0, 5))

        desc = ctk.CTkLabel(
            panel,
            text="Choose the intelligence model sAI will use for chatting and reasoning.",
            font=("Segoe UI", 13),
            anchor="w",
        )
        desc.pack(fill="x", pady=(0, 15))

        if self.provider_choice.get() == "openai_compatible":
            # OpenAI-compatible provider selected
            info_card = ctk.CTkFrame(panel, fg_color=("gray90", "gray17"), corner_radius=8)
            info_card.pack(fill="x", pady=10)
            ctk.CTkLabel(info_card, text="OpenAI-Compatible Model", font=("Segoe UI", 14, "bold"), anchor="w").pack(
                anchor="w", padx=15, pady=(10, 2)
            )
            ctk.CTkLabel(
                info_card,
                text=f"Using model: {self.openai_model.get()} at {self.openai_endpoint.get()}",
                font=("Segoe UI", 12),
                anchor="w",
            ).pack(anchor="w", padx=15, pady=(0, 10))
            self.next_button.configure(state="normal")
            return

        # Ollama Model Discovery
        self.models_container = ctk.CTkFrame(panel, fg_color="transparent")
        self.models_container.pack(fill="both", expand=True)

        self.models_status_label = ctk.CTkLabel(
            self.models_container,
            text="Discovering installed Ollama models...",
            font=("Segoe UI", 13),
            anchor="w",
        )
        self.models_status_label.pack(fill="x", pady=10)

        self.discover_models()

    def discover_models(self):
        self.models_status_label.configure(text="Checking installed Ollama models...")
        self.next_button.configure(state="disabled")

        for child in self.models_container.winfo_children():
            if child != self.models_status_label:
                child.destroy()

        def task():
            try:
                models = self.model_manager.discover_ollama_models()
                self.safe_after(lambda: self._apply_discovered_models(models))
            except Exception as exc:
                self.safe_after(lambda: self._apply_models_error(str(exc)))

        threading.Thread(target=task, daemon=True).start()

    def _apply_discovered_models(self, models: list[ModelInfo]):
        self.discovered_models = models
        for child in self.models_container.winfo_children():
            if child != self.models_status_label:
                child.destroy()

        if not models:
            self._render_empty_models_guide()
            return

        self.models_status_label.configure(
            text=f"Found {len(models)} installed model(s):",
            text_color=("gray30", "gray80"),
        )

        selector_frame = ctk.CTkFrame(self.models_container, fg_color=("gray90", "gray17"), corner_radius=8)
        selector_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(selector_frame, text="Select Active Model:", font=("Segoe UI", 12, "bold"), anchor="w").pack(
            anchor="w", padx=15, pady=(10, 4)
        )

        names = [m.name for m in models]
        current = self.selected_ollama_model.get()
        if current not in names:
            current = names[0]
            self.selected_ollama_model.set(current)

        self.model_dropdown = ctk.CTkOptionMenu(
            selector_frame,
            values=names,
            variable=self.selected_ollama_model,
            command=self._on_model_selected,
            height=36,
        )
        self.model_dropdown.pack(fill="x", padx=15, pady=(0, 10))

        self.model_details_label = ctk.CTkLabel(
            selector_frame,
            text=self._format_model_details(current),
            font=("Segoe UI", 12),
            text_color=("gray40", "gray70"),
            anchor="w",
        )
        self.model_details_label.pack(fill="x", padx=15, pady=(0, 10))

        # Refresh button
        actions = ctk.CTkFrame(self.models_container, fg_color="transparent")
        actions.pack(fill="x", pady=5)
        ctk.CTkButton(
            actions,
            text="🔄 Refresh Models",
            width=140,
            command=self.discover_models,
        ).pack(side="left")

        self.next_button.configure(state="normal")

    def _render_empty_models_guide(self):
        self.models_status_label.configure(
            text="No models installed in Ollama yet.",
            text_color="#FFA000",
        )

        guide_box = ctk.CTkFrame(self.models_container, fg_color=("gray90", "gray17"), corner_radius=8)
        guide_box.pack(fill="x", pady=10)

        ctk.CTkLabel(
            guide_box,
            text="Download Your First Model",
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            guide_box,
            text=(
                "sAI does not download large model files automatically to protect your disk space and bandwidth.\n"
                "To install the recommended model for sAI, open Windows Terminal (or Command Prompt) and run:"
            ),
            font=("Segoe UI", 12),
            anchor="w",
            wraplength=650,
            justify="left",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Command Snippet Box
        cmd_box = ctk.CTkFrame(guide_box, fg_color=("gray80", "gray12"), corner_radius=6)
        cmd_box.pack(fill="x", padx=15, pady=(0, 10))

        cmd_text = f"ollama pull {RECOMMENDED_OLLAMA_MODEL}"
        cmd_lbl = ctk.CTkLabel(cmd_box, text=f"  {cmd_text}  ", font=("Consolas", 13, "bold"), anchor="w")
        cmd_lbl.pack(side="left", padx=10, pady=8)

        copy_btn = ctk.CTkButton(
            cmd_box,
            text="📋 Copy Command",
            width=130,
            command=lambda: self._copy_to_clipboard(cmd_text, copy_btn),
        )
        copy_btn.pack(side="right", padx=10, pady=8)

        ctk.CTkLabel(
            guide_box,
            text="Once the download finishes in your terminal, click 'Refresh Models' below.",
            font=("Segoe UI", 12, "italic"),
            text_color=("gray40", "gray70"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(0, 12))

        # Action row
        actions = ctk.CTkFrame(self.models_container, fg_color="transparent")
        actions.pack(fill="x", pady=5)

        ctk.CTkButton(
            actions,
            text="🔄 Refresh Models",
            width=150,
            command=self.discover_models,
        ).pack(side="left")

        self.next_button.configure(state="disabled")

    def _copy_to_clipboard(self, text: str, button: ctk.CTkButton):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            button.configure(text="✓ Copied!")
            self.after(2000, lambda: button.configure(text="📋 Copy Command"))
        except Exception:
            pass

    def _format_model_details(self, model_name: str) -> str:
        for m in self.discovered_models:
            if m.name == model_name:
                size_str = f"Size: {m.formatted_size}" if m.formatted_size else "Size: Unknown"
                modified = f" | Modified: {m.modified_at[:10]}" if m.modified_at else ""
                return f"{size_str}{modified}"
        return ""

    def _on_model_selected(self, model_name: str):
        if hasattr(self, "model_details_label"):
            self.model_details_label.configure(text=self._format_model_details(model_name))

    def _apply_models_error(self, err: str):
        self.models_status_label.configure(text=f"Error connecting to Ollama: {err}", text_color="#E57373")
        self.next_button.configure(state="disabled")

    # --------------------------------------------------
    # Step 4: Finish & Launch
    # --------------------------------------------------

    def render_step_4_finish(self):
        self.back_button.configure(state="normal", command=lambda: self.show_step(3))
        self.next_button.configure(text="🚀 Launch sAI", state="normal", command=self.finish_setup)

        panel = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        panel.pack(fill="both", expand=True, padx=25, pady=20)

        heading = ctk.CTkLabel(
            panel,
            text="Step 4: Ready to Launch",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        )
        heading.pack(fill="x", pady=(0, 5))

        desc = ctk.CTkLabel(
            panel,
            text="Setup is complete. Review your configuration and start chatting with sAI.",
            font=("Segoe UI", 13),
            anchor="w",
        )
        desc.pack(fill="x", pady=(0, 15))

        # Summary Card
        summary_card = ctk.CTkFrame(panel, fg_color=("gray90", "gray17"), corner_radius=10)
        summary_card.pack(fill="x", pady=10)

        provider_name = (
            "Local Ollama Service"
            if self.provider_choice.get() == "ollama"
            else "OpenAI-Compatible Local Endpoint"
        )
        active_model = (
            self.selected_ollama_model.get()
            if self.provider_choice.get() == "ollama"
            else self.openai_model.get()
        )
        endpoint_display = (
            OLLAMA_BASE_URL
            if self.provider_choice.get() == "ollama"
            else self.openai_endpoint.get()
        )

        rows = [
            ("AI Engine:", provider_name),
            ("Active Model:", active_model),
            ("Service Endpoint:", endpoint_display),
            ("Privacy:", "100% Local — No data leaves your computer"),
            ("User Data Path:", str(DATA_DIR)),
        ]

        for label, val in rows:
            row = ctk.CTkFrame(summary_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(row, text=label, width=150, font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Segoe UI", 12), anchor="w").pack(side="left")

        self.finish_status_label = ctk.CTkLabel(
            panel,
            text="Click 'Launch sAI' to save settings and open the assistant.",
            font=("Segoe UI", 12),
            text_color=("gray40", "gray70"),
            anchor="w",
        )
        self.finish_status_label.pack(fill="x", pady=(15, 5))

    def finish_setup(self):
        """Verifies configuration, persists settings, and invokes completion callback."""
        self.next_button.configure(state="disabled", text="Verifying & Saving...")
        self.back_button.configure(state="disabled")
        self.finish_status_label.configure(text="Validating model and saving preferences...", text_color=("gray40", "gray70"))

        provider = self.provider_choice.get()
        ollama_model = self.selected_ollama_model.get().strip()
        openai_endpoint = self.openai_endpoint.get().strip()
        openai_model = self.openai_model.get().strip()

        def task():
            try:
                if provider == "ollama":
                    # Verify Ollama is still reachable
                    if not self.model_manager.is_ollama_running():
                        raise RuntimeError("Ollama service is not responding at http://127.0.0.1:11434.")
                    # Verify model exists
                    models = self.model_manager.discover_ollama_models()
                    validated_model = self.model_manager.validate_ollama_model(ollama_model, models)
                    self.settings.update(
                        provider="ollama",
                        ollama_model=validated_model,
                        setup_completed=True,
                    )
                else:
                    temp_mgr = ModelManager(self.settings)
                    self.settings.update(
                        provider="openai_compatible",
                        openai_base_url=openai_endpoint,
                        openai_model=openai_model,
                        setup_completed=True,
                    )
                    temp_mgr.validate_openai_compatible()

                self.settings.save()

                if self.assistant is not None:
                    self.assistant.llm.settings.data = self.settings.llm_config()

                self.safe_after(self._on_setup_success)

            except Exception as exc:
                self.safe_after(lambda: self._on_setup_failure(str(exc)))

        threading.Thread(target=task, daemon=True).start()

    def _on_setup_success(self):
        if self.on_complete:
            self.on_complete()

    def _on_setup_failure(self, err_msg: str):
        self.next_button.configure(state="normal", text="Retry Launch")
        self.back_button.configure(state="normal")
        self.finish_status_label.configure(
            text=f"Verification failed: {err_msg}",
            text_color="#E57373",
        )

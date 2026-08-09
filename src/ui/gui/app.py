from __future__ import annotations

import logging
import os
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from src.config.voices import VoicesConfigError, load_voices
from src.models.generation import GenerationRequest, GenerationResult
from src.services.audio_service import get_output_dir
from src.ui.batch_csv import BatchCsvResult, BatchProgressEvent
from src.ui.gui.workers import UNEXPECTED_ERROR, BatchWorker, GenerateWorker
from src.ui.messages import message_for

logger = logging.getLogger(__name__)

_CONFIG_ERROR_STATUS = "Voice configuration could not be loaded."
_UNEXPECTED_STATUS = "An unexpected error occurred. See logs for details."
_PLAY_ERROR = "Could not open the audio file with the default player."
_OPEN_FOLDER_ERROR = "Could not open the output folder."


class UzbekTTSApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Uzbek Voice Generator")
        self.geometry("720x560")
        self.minsize(640, 520)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._generating = False
        self._batch_running = False
        self._voice_load_failed = False
        self._last_output_path: str | None = None
        self._last_batch_dir: Path | None = None
        self._last_filename_input: str = ""
        self._batch_abort_message: str | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._tabs = ctk.CTkTabview(self)
        self._tabs.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self._tabs.add("Single text")
        self._tabs.add("Batch CSV")

        self._build_single_tab(self._tabs.tab("Single text"))
        self._build_batch_tab(self._tabs.tab("Batch CSV"))

    def selected_gender(self) -> str:
        return self._voice_var.get()

    def _busy(self) -> bool:
        return self._generating or self._batch_running

    def _load_voice_genders(self) -> list[str]:
        genders: list[str] = []
        seen: set[str] = set()
        for voice in load_voices():
            if voice.gender not in seen:
                seen.add(voice.gender)
                genders.append(voice.gender)
        return genders

    def _build_single_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Uzbek text").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4)
        )
        self._text_box = ctk.CTkTextbox(parent, height=140)
        self._text_box.grid(row=1, column=0, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(parent, text="Voice").grid(
            row=2, column=0, sticky="w", padx=8, pady=(12, 4)
        )

        voice_load_failed = False
        try:
            genders = self._load_voice_genders()
        except VoicesConfigError:
            genders = []
            voice_load_failed = True

        if not genders:
            voice_load_failed = True
            genders = [""]

        self._voice_load_failed = voice_load_failed

        default_gender = genders[0]
        self._voice_var = ctk.StringVar(value=default_gender)
        self._voice_menu = ctk.CTkOptionMenu(
            parent,
            values=genders,
            variable=self._voice_var,
        )
        self._voice_menu.grid(row=3, column=0, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(parent, text="Output filename").grid(
            row=4, column=0, sticky="w", padx=8, pady=(12, 4)
        )
        self._filename_entry = ctk.CTkEntry(parent, placeholder_text="hello.mp3")
        self._filename_entry.grid(row=5, column=0, sticky="ew", padx=8, pady=4)

        action_row = ctk.CTkFrame(parent, fg_color="transparent")
        action_row.grid(row=6, column=0, sticky="w", padx=8, pady=(16, 8))

        self._generate_btn = ctk.CTkButton(
            action_row,
            text="Generate",
            command=self._on_generate,
        )
        self._generate_btn.grid(row=0, column=0, padx=(0, 8))

        self._play_btn = ctk.CTkButton(
            action_row,
            text="Play",
            command=self._on_play,
            state="disabled",
        )
        self._play_btn.grid(row=0, column=1, padx=(0, 8))

        self._open_folder_btn = ctk.CTkButton(
            action_row,
            text="Open folder",
            command=self._on_open_single_folder,
        )
        self._open_folder_btn.grid(row=0, column=2)

        status_text = (
            _CONFIG_ERROR_STATUS
            if voice_load_failed
            else "Ready — MP3s save to the output folder."
        )
        self._single_status = ctk.CTkLabel(
            parent,
            text=status_text,
            anchor="w",
        )
        self._single_status.grid(row=7, column=0, sticky="ew", padx=8, pady=4)

        if voice_load_failed:
            self._voice_menu.configure(state="disabled")
            self._generate_btn.configure(state="disabled")

    def _build_batch_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(parent, text="CSV file (columns: text, gender, filename)").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4)
        )

        path_row = ctk.CTkFrame(parent, fg_color="transparent")
        path_row.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        path_row.grid_columnconfigure(0, weight=1)

        self._csv_path_var = ctk.StringVar(value="")
        self._csv_entry = ctk.CTkEntry(
            path_row,
            textvariable=self._csv_path_var,
            placeholder_text="Select a UTF-8 CSV file…",
        )
        self._csv_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._browse_btn = ctk.CTkButton(
            path_row,
            text="Browse…",
            width=100,
            command=self._on_browse,
        )
        self._browse_btn.grid(row=0, column=1)

        batch_actions = ctk.CTkFrame(parent, fg_color="transparent")
        batch_actions.grid(row=2, column=0, sticky="w", padx=8, pady=(16, 8))

        self._batch_btn = ctk.CTkButton(
            batch_actions,
            text="Run batch",
            command=self._on_run_batch,
        )
        self._batch_btn.grid(row=0, column=0, padx=(0, 8))

        self._open_batch_folder_btn = ctk.CTkButton(
            batch_actions,
            text="Open folder",
            command=self._on_open_batch_folder,
        )
        self._open_batch_folder_btn.grid(row=0, column=1)

        self._progress = ctk.CTkProgressBar(parent)
        self._progress.grid(row=3, column=0, sticky="ew", padx=8, pady=4)
        self._progress.set(0)

        self._batch_log = ctk.CTkTextbox(parent, height=140)
        self._batch_log.grid(row=4, column=0, sticky="nsew", padx=8, pady=4)
        self._batch_log.configure(state="disabled")

        self._batch_status = ctk.CTkLabel(
            parent,
            text="Select a UTF-8 CSV, then Run batch.",
            anchor="w",
        )
        self._batch_status.grid(row=5, column=0, sticky="ew", padx=8, pady=4)

    def _set_play_enabled(self, enabled: bool) -> None:
        self._play_btn.configure(state="normal" if enabled else "disabled")

    def _set_single_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self._text_box.configure(state=state)
        self._filename_entry.configure(state=state)
        if self._voice_load_failed:
            self._voice_menu.configure(state="disabled")
            self._generate_btn.configure(state="disabled")
        else:
            self._voice_menu.configure(state=state)
            self._generate_btn.configure(state=state)

    def _set_batch_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self._csv_entry.configure(state=state)
        self._browse_btn.configure(state=state)
        self._batch_btn.configure(state=state)

    def _set_busy_ui(self, busy: bool) -> None:
        enabled = not busy
        self._set_single_controls_enabled(enabled)
        self._set_batch_controls_enabled(enabled)

    def _append_batch_log(self, line: str) -> None:
        self._batch_log.configure(state="normal")
        self._batch_log.insert("end", line + "\n")
        self._batch_log.see("end")
        self._batch_log.configure(state="disabled")

    def _clear_batch_log(self) -> None:
        self._batch_log.configure(state="normal")
        self._batch_log.delete("1.0", "end")
        self._batch_log.configure(state="disabled")

    def _open_path(self, path: Path) -> None:
        try:
            path.mkdir(parents=True, exist_ok=True)
            os.startfile(str(path))  # type: ignore[attr-defined]
        except OSError:
            logger.exception("Failed to open folder %s", path)
            messagebox.showerror("Open folder failed", _OPEN_FOLDER_ERROR)

    def _on_generate(self) -> None:
        if self._busy() or self._voice_load_failed:
            return

        text = self._text_box.get("1.0", "end-1c")
        gender = self.selected_gender()
        filename = self._filename_entry.get()
        request = GenerationRequest(text=text, gender=gender, filename=filename)

        self._generating = True
        self._last_output_path = None
        self._last_filename_input = filename.strip()
        self._set_play_enabled(False)
        self._set_busy_ui(True)
        self._single_status.configure(text="Generating...")

        worker = GenerateWorker(request, on_done=self._on_generate_done)
        worker.start()

    def _on_generate_done(self, outcome: GenerationResult | str) -> None:
        self.after(0, lambda: self._finish_generate(outcome))

    def _finish_generate(self, outcome: GenerationResult | str) -> None:
        self._generating = False
        self._set_busy_ui(False)

        if outcome == UNEXPECTED_ERROR:
            self._last_output_path = None
            self._set_play_enabled(False)
            self._single_status.configure(text=_UNEXPECTED_STATUS)
            messagebox.showerror("Generation failed", _UNEXPECTED_STATUS)
            return

        result = outcome
        if result.success:
            self._last_output_path = result.output_path
            self._set_play_enabled(True)
            saved_name = Path(result.output_path).name
            saved = f"Saved: {result.output_path}"
            if self._last_filename_input and self._last_filename_input != saved_name:
                saved = f"Saved as {saved_name} (.mp3 normalized): {result.output_path}"
            self._single_status.configure(text=saved)
            messagebox.showinfo("Success", saved)
            return

        self._last_output_path = None
        self._set_play_enabled(False)
        msg = message_for(result)
        self._single_status.configure(text=msg)
        messagebox.showerror("Generation failed", msg)

    def _on_play(self) -> None:
        if not self._last_output_path:
            return
        try:
            os.startfile(self._last_output_path)  # type: ignore[attr-defined]
        except OSError:
            logger.exception("Failed to open audio file for preview")
            messagebox.showerror("Playback failed", _PLAY_ERROR)

    def _on_open_single_folder(self) -> None:
        if self._last_output_path:
            folder = Path(self._last_output_path).parent
        else:
            folder = get_output_dir()
        self._open_path(folder)

    def _on_browse(self) -> None:
        if self._busy():
            return
        path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self._csv_path_var.set(path)

    def _on_run_batch(self) -> None:
        if self._busy():
            return
        raw = self._csv_path_var.get().strip()
        if not raw:
            messagebox.showerror("Batch failed", "Select a CSV file first.")
            return

        csv_path = Path(raw)
        self._batch_running = True
        self._batch_abort_message = None
        self._last_batch_dir = get_output_dir() / csv_path.stem
        self._set_busy_ui(True)
        self._progress.set(0)
        self._clear_batch_log()
        self._batch_status.configure(text="Running batch...")

        worker = BatchWorker(
            csv_path,
            on_progress=self._on_batch_progress,
            on_done=self._on_batch_done,
        )
        worker.start()

    def _on_batch_progress(self, event: BatchProgressEvent) -> None:
        self.after(0, lambda e=event: self._apply_batch_progress(e))

    def _apply_batch_progress(self, event: BatchProgressEvent) -> None:
        if event.kind == "abort":
            self._batch_abort_message = event.message
            self._batch_status.configure(text=event.message)
            return

        if event.total > 0:
            self._progress.set(event.completed / event.total)

        if event.kind in ("row_ok", "row_fail"):
            self._append_batch_log(event.message)
        elif event.kind == "row_skip" and event.message:
            pass

        if event.kind == "summary":
            self._batch_status.configure(text=event.message)

    def _on_batch_done(self, outcome: BatchCsvResult | str) -> None:
        self.after(0, lambda: self._finish_batch(outcome))

    def _finish_batch(self, outcome: BatchCsvResult | str) -> None:
        self._batch_running = False
        self._set_busy_ui(False)

        if outcome == UNEXPECTED_ERROR:
            self._batch_status.configure(text=_UNEXPECTED_STATUS)
            messagebox.showerror("Batch failed", _UNEXPECTED_STATUS)
            return

        result = outcome
        if result.aborted:
            msg = self._batch_abort_message or "Batch aborted."
            self._progress.set(0)
            self._batch_status.configure(text=msg)
            messagebox.showerror("Batch failed", msg)
            return

        summary = f"OK={result.ok} FAIL={result.failed} SKIPPED={result.skipped}"
        self._batch_status.configure(text=summary)

    def _on_open_batch_folder(self) -> None:
        if self._last_batch_dir is not None and self._last_batch_dir.is_dir():
            self._open_path(self._last_batch_dir)
            return
        self._batch_status.configure(
            text="Batch folder not found yet — opening output/."
        )
        self._open_path(get_output_dir())


def run_gui() -> None:
    app = UzbekTTSApp()
    app.mainloop()

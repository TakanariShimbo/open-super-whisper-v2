"""
Main Controller

This module provides the controller component for the main application window,
mediating between the main model and main window view.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

from ..utils.clipboard_utils import ClipboardUtils
from ..managers.settings_manager import SettingsManager
from ..models.main_model import MainModel
from ..views.factories.status_indicator_factory import StatusIndicatorFactory
from ..views.factories.api_key_dialog_factory import APIKeyDialogFactory
from ..views.factories.instruction_dialog_factory import InstructionDialogFactory
from ..views.factories.settings_dialog_factory import SettingsDialogFactory


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "error_message_format": "Error: {error}",
            "llm_output_copied_message": "LLM output copied to clipboard",
            "stt_output_copied_message": "STT output copied to clipboard",
            "processing_cancelled_message": "Processing cancelled",
        },
        "Japanese": {
            "error_message_format": "エラー: {error}",
            "llm_output_copied_message": "LLM出力をクリップボードにコピーしました",
            "stt_output_copied_message": "STT出力をクリップボードにコピーしました",
            "processing_cancelled_message": "処理がキャンセルされました",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def error_message_format(self) -> str:
        return self._labels["error_message_format"]

    @property
    def llm_output_copied_message(self) -> str:
        return self._labels["llm_output_copied_message"]

    @property
    def stt_output_copied_message(self) -> str:
        return self._labels["stt_output_copied_message"]

    @property
    def processing_cancelled_message(self) -> str:
        return self._labels["processing_cancelled_message"]


class MainController(QObject):
    """
    Main application controller.

    This class serves as the central coordinator between the user interface (view)
    and the application's model. It processes user input from the view, interacts
    with the model, and updates the view with results.

    Attributes
    ----------
    recording_started : pyqtSignal
        Signal emitted when recording starts
    processing_started : pyqtSignal
        Signal emitted when audio processing starts
    processing_complete : pyqtSignal
        Signal emitted when processing completes with results
    processing_cancelled : pyqtSignal
        Signal emitted when processing is cancelled
    streaming_llm_chunk : pyqtSignal
        Signal emitted when a chunk is received from the LLM stream
    instruction_set_activated : pyqtSignal
        Signal emitted when an instruction set is activated
    showing_message : pyqtSignal
        Signal emitted when there's a message to show in the UI
    """

    #
    # Signals
    #
    # Pipeline signals
    recording_started = pyqtSignal()
    processing_started = pyqtSignal()
    processing_completed = pyqtSignal(PipelineResult)
    processing_cancelled = pyqtSignal()
    streaming_llm_chunk = pyqtSignal(str)

    # Instruction set signals
    instruction_set_activated = pyqtSignal(str)

    # UI signals
    showing_message = pyqtSignal(str, int)

    def __init__(self, main_window: QObject | None = None) -> None:
        """
        Initialize the MainController.

        Parameters
        ----------
        main_window : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=main_window)

        # Initialize label manager
        self._label_manager = LabelManager()

        # Get the settings manager
        self._settings_manager = SettingsManager.instance()

        # Get the API key
        api_key = self._settings_manager.get_api_key()

        # Initialize the model
        self._model = MainModel(
            api_key=api_key,
            main_window=main_window,
        )

        # Connect model signals
        self._connect_model_signals()

        # Create status indicator view and controller
        self._status_indicator_view = StatusIndicatorFactory.create_indicator(main_window=main_window)
        self._status_indicator_controller = self._status_indicator_view.get_controller()

    #
    # Model Signals
    #
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model to the controller.
        """
        # Pipeline signals
        self._model.processing_started.connect(self.processing_started)
        self._model.processing_completed.connect(self._handle_processing_completed)
        self._model.processing_cancelled.connect(self._handle_processing_cancelled)
        self._model.processing_error.connect(
            lambda error: self.showing_message.emit(self._label_manager.error_message_format.format(error=error), 2000)
        )
        self._model.streaming_llm_chunk.connect(self._handle_streamling_llm_chunk)

        # Instruction set signals
        self._model.instruction_set_activated.connect(self._handle_instruction_set_activated)

        # Hotkey signals
        self._model.hotkey_triggered.connect(self._handle_hotkey_triggered)

    #
    # Model Events
    #
    @pyqtSlot(str)
    def _handle_instruction_set_activated(self, set_name: str) -> None:
        """
        Handle instruction set activation.
        """
        self.instruction_set_activated.emit(set_name)

    @pyqtSlot(str)
    def _handle_streamling_llm_chunk(self, chunk: str) -> None:
        """
        Handle streaming chunks from the LLM processor.

        Parameters
        ----------
        chunk : str
            The text chunk from the LLM stream
        """
        # Forward the stream chunk to any listening views
        self.streaming_llm_chunk.emit(chunk)

    @pyqtSlot(PipelineResult)
    def _handle_processing_completed(self, result: PipelineResult) -> None:
        """
        Handle processing completion.

        Parameters
        ----------
        result : PipelineResult
            The result of the processing
        """
        # Set status indicator to complete mode
        self._status_indicator_controller.complete_processing()

        # Check if auto-clipboard is enabled and copy results if needed
        if self._settings_manager.get_auto_clipboard():
            # Copy the most appropriate output to clipboard
            if result.is_llm_processed and result.llm_output:
                # If LLM was processed, copy LLM output
                ClipboardUtils.set_text(text=result.llm_output)
                self.showing_message.emit(self._label_manager.llm_output_copied_message, 2000)
            elif result.stt_output:
                # Otherwise, copy STT output
                ClipboardUtils.set_text(text=result.stt_output)
                self.showing_message.emit(self._label_manager.stt_output_copied_message, 2000)

        # Disable recording mode for hotkeys
        self._model.disable_filtered_mode_and_start_listening()

        # Forward the signal to views
        self.processing_completed.emit(result)

    @pyqtSlot()
    def _handle_processing_cancelled(self) -> None:
        """
        Handle processing cancellation.
        """
        # Set status indicator to cancelled mode
        self._status_indicator_controller.cancel_processing()

        # Forward the signal to views
        self.processing_cancelled.emit()

    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle hotkey trigger events.

        Parameters
        ----------
        hotkey : str
            The hotkey that was triggered
        """
        # If processing is active, cancel it
        if self.is_processing:
            self.cancel_processing()
            return

        # If recording is active, stop it
        if self.is_recording:
            self.stop_recording()
            return

        # Otherwise start recording with the selected instruction set
        instruction_set = self._model.get_instruction_set_by_hotkey(hotkey=hotkey)
        if instruction_set is None:
            return
        self.start_recording(set_name=instruction_set.name, hotkey=hotkey)

    #
    # Controller Methods
    #
    @property
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.

        Returns
        -------
        bool
            True if recording is in progress, False otherwise
        """
        return self._model.is_recording

    @property
    def is_processing(self) -> bool:
        """
        Check if audio processing is in progress.

        Returns
        -------
        bool
            True if processing is in progress, False otherwise
        """
        return self._model.is_processing

    def get_instruction_sets(self) -> list[InstructionSet]:
        """
        Get all available instruction sets.

        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._model.get_instruction_sets()

    def get_selected_instruction_set(self) -> InstructionSet | None:
        """
        Get the currently selected instruction set.

        Returns
        -------
        InstructionSet | None
            The currently selected instruction set, or None if none selected
        """
        return self._model.get_selected_instruction_set()

    def get_instruction_set_by_name(self, name: str) -> InstructionSet | None:
        """
        Get an instruction set by name.

        Parameters
        ----------
        name : str
            The name of the instruction set to get

        Returns
        -------
        InstructionSet | None
            The instruction set with the given name, or None if not found
        """
        return self._model.get_instruction_set_by_name(name=name)

    def register_hotkey(self, hotkey: str) -> bool:
        """
        Register a global hotkey.

        Parameters
        ----------
        hotkey : str
            The hotkey string to register (e.g., "ctrl+shift+r")

        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        return self._model.register_hotkey(hotkey=hotkey)

    def start_recording(self, set_name: str, hotkey: str) -> bool:
        """
        Start recording audio with a specific hotkey as the trigger.

        Parameters
        ----------
        set_name : str
            The name of the instruction set to use
        hotkey : str
            The hotkey that triggered recording

        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """
        # Set the selected instruction set
        is_set = self._model.set_selected_instruction_set(name=set_name)
        if not is_set:
            return False

        # Start recording
        is_started = self._model.start_recording()
        if not is_started:
            return False

        # Set recording mode for hotkeys with the active hotkey
        self._model.enable_filtered_mode_and_start_listening(active_hotkey=hotkey)

        # Start status indicator in recording mode
        self._status_indicator_controller.start_recording()

        # Emit recording started signal
        self.recording_started.emit()

    def stop_recording(self) -> bool:
        """
        Stop recording audio and begin processing.

        Returns
        -------
        bool
            True if recording was stopped successfully, False otherwise
        """
        if not self.is_recording:
            return False

        # Stop recording
        audio_file_path = self._model.stop_recording()

        # Update status indicator to processing mode
        self._status_indicator_controller.start_processing()

        # Process the audio if we have a file
        if audio_file_path:
            # Get clipboard content (text and image)
            clipboard_text, clipboard_image = None, None
            selected_set = self._model.get_selected_instruction_set()
            if selected_set and selected_set.llm_enabled:
                # Only get clipboard if LLM is enabled in the instruction set
                clipboard_text, clipboard_image = ClipboardUtils.get_content()

                if not selected_set.llm_clipboard_text_enabled:
                    clipboard_text = None
                if not selected_set.llm_clipboard_image_enabled:
                    clipboard_image = None

                print(f"Retrieved clipboard content: Text: {'Yes' if clipboard_text else 'No'}, " f"Image: {'Yes' if clipboard_image else 'No'}")

            # Process the audio with clipboard content asynchronously
            self._model.process_audio(
                audio_file_path=audio_file_path,
                clipboard_text=clipboard_text,
                clipboard_image=clipboard_image,
            )

        return True

    def cancel_processing(self) -> bool:
        """
        Cancel the current processing task if one is in progress.

        Returns
        -------
        bool
            True if cancellation was initiated, False if no processing to cancel
        """
        if not self.is_processing:
            return False

        # Cancel processing through model
        result = self._model.cancel_processing()

        if result:
            # Show cancelled status in indicator
            self._status_indicator_controller.cancel_processing()

            self.showing_message.emit(self._label_manager.processing_cancelled_message, 2000)

        return result

    def show_api_key_dialog(self, main_window: QWidget | None = None) -> bool:
        """
        Show the API key dialog.

        This method creates and displays an API key dialog,
        allowing the user to update their API key.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        bool
            True if the API key was successfully updated, False otherwise
        """
        # Create and show the API key settings dialog through factory
        dialog = APIKeyDialogFactory.create_settings_dialog(main_window=main_window)

        # Show dialog and handle result
        result = dialog.exec()

        # Handle dialog result
        if result == dialog.DialogCode.Accepted:
            return True
        else:
            return False

    def show_instruction_dialog(self, main_window: QWidget | None = None) -> bool:
        """
        Show the instruction dialog and handle the result.

        This method creates, displays, and handles the result of an instruction dialog,
        encapsulating the dialog flow logic.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        bool
            True if the dialog was accepted, False otherwise
        """
        # Create instruction dialog using factory
        dialog = InstructionDialogFactory.create_dialog(main_window=main_window)

        # Show dialog and get result
        result = dialog.exec()

        # Handle dialog result
        if result == dialog.DialogCode.Accepted:
            return True
        else:
            return False

    def show_settings_dialog(self, main_window: QWidget | None = None) -> bool:
        """
        Show the settings dialog and handle the result.

        This method creates, displays, and handles the result of a settings dialog,
        encapsulating the dialog flow logic.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        bool
            True if the dialog was accepted, False otherwise
        """
        # Create settings dialog using factory
        dialog = SettingsDialogFactory.create_dialog(main_window=main_window)

        # Show dialog and get result
        result = dialog.exec()

        # Handle dialog result
        if result == dialog.DialogCode.Accepted:
            return True
        else:
            return False

    def shutdown(self) -> None:
        """
        Clean up resources when the application is shutting down.
        """
        # Forward to model to handle cleanup
        self._model.shutdown()

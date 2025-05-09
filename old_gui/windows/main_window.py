"""
Main Window Module with LLM Integration

This module provides the main application window and core functionality
with integrated LLM processing support.
"""

import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QCheckBox,
    QGridLayout, QFormLayout, QTabWidget,
    QSystemTrayIcon, QMenu, QStyle, QToolBar, QDialog
)
from PyQt6.QtCore import QBuffer, QIODevice

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings, QUrl, QSize, QBuffer, QIODevice
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult

from core.hotkey.hotkey_manager import HotkeyManager
from old_gui.resources.config import AppConfig
from old_gui.resources.labels import AppLabels
from old_gui.dialogs.api_key_dialog import APIKeyDialog
from old_gui.dialogs.instruction_sets_dialog import InstructionSetsDialog, GUIInstructionSetManager
from old_gui.dialogs.simple_message_dialog import SimpleMessageDialog
from old_gui.components.widgets.status_indicator import StatusIndicatorWindow
from old_gui.components.widgets.markdown_text_browser import MarkdownTextBrowser
from old_gui.utils.resource_helper import get_resource_path

# Thread management imports
from old_gui.thread_management.thread_manager import ThreadManager
from old_gui.thread_management.ui_updater import UIUpdater
from old_gui.thread_management.hotkey_bridge import HotkeyBridge


class MainWindow(QMainWindow):
    """
    Main application window.
    
    This class provides the main user interface and integrates the audio
    recording, transcription, and LLM (Large Language Model) processing functionality.
    It manages the core application flow and user interactions.
    """
    
    # Custom signals
    processing_complete = pyqtSignal(PipelineResult)
    recording_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        """
        Initialize the MainWindow.
        """
        super().__init__()
        
        # Load settings
        self.settings = QSettings(AppConfig.APP_ORGANIZATION, AppConfig.APP_NAME)
        self.api_key = self.settings.value("api_key", AppConfig.DEFAULT_API_KEY)
        
        # Clipboard settings
        self.auto_copy = self.settings.value("auto_copy", AppConfig.DEFAULT_AUTO_COPY, type=bool)
        
        # Initialize thread manager for safe thread operations
        self.thread_manager = ThreadManager()
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager()
        
        # Initialize instruction set manager
        self.instruction_set_manager = GUIInstructionSetManager(self.settings)
        
        # For storing instruction set hotkeys during recording
        self.instruction_set_hotkeys = []
        
        # Initialize core components
        self.pipeline = None
        
        # Recording state
        self.is_recording = False
        
        # Sound settings
        self.enable_sound = self.settings.value("enable_sound", AppConfig.DEFAULT_ENABLE_SOUND, type=bool)
        
        # Indicator display settings
        self.show_indicator = self.settings.value("show_indicator", AppConfig.DEFAULT_SHOW_INDICATOR, type=bool)
        
        # Initialize sound players
        self.setup_sound_players()
        
        # Status indicator window
        self.status_indicator_window = StatusIndicatorWindow()
        self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
        
        # Initialize transcription processor if API key is available
        try:
            self.pipeline = Pipeline(api_key=self.api_key)
        except ValueError:
            self.pipeline = None
        
        # Set up UI
        self.init_ui()
        
        # Apply settings from selected instruction set - must be after UI initialization
        if self.pipeline:
            self.apply_instruction_set_settings()
        
        # Set up ThreadManager signal connections
        self._setup_thread_manager_connections()
        
        # Connect signals
        self.processing_complete.connect(self.on_processing_complete, Qt.ConnectionType.QueuedConnection)
        self.recording_status_changed.connect(self.update_recording_status, Qt.ConnectionType.QueuedConnection)
        
        # Connect status indicator window to ThreadManager
        self.status_indicator_window.connect_to_thread_manager(self.thread_manager)
        
        # Connect HotkeyBridge recordingHotkeyPressed signal to stop_recording
        HotkeyBridge.instance().recordingHotkeyPressed.connect(self.on_recording_hotkey_pressed, Qt.ConnectionType.QueuedConnection)
        
        # Check API key
        if not self.api_key:
            self.thread_manager.run_in_main_thread(self.show_api_key_dialog)
            
        # Set up additional connections
        self.setup_connections()
        
        # Set up global hotkey
        self.setup_global_hotkey()
        
        # Set up system tray
        self.setup_system_tray()
        
    def _setup_thread_manager_connections(self):
        """
        Set up connections between ThreadManager signals and MainWindow slots.
        """
        # Status update connection
        self.thread_manager.statusUpdate.connect(
            lambda msg, timeout: self.status_bar.showMessage(msg, timeout),
            Qt.ConnectionType.QueuedConnection
        )
        
        # Timer update connection
        self.thread_manager.timerUpdate.connect(
            lambda time_str: self.recording_timer_label.setText(time_str),
            Qt.ConnectionType.QueuedConnection
        )
        
        # Processing complete connection
        self.thread_manager.processingComplete.connect(
            self.on_processing_complete,
            Qt.ConnectionType.QueuedConnection
        )
        
        # Recording status connection
        self.thread_manager.recordingStatusChanged.connect(
            self.update_recording_status,
            Qt.ConnectionType.QueuedConnection
        )
        
        # Indicator update connections
        self.thread_manager.indicatorUpdate.connect(
            lambda mode: self.status_indicator_window.set_mode(mode),
            Qt.ConnectionType.QueuedConnection
        )
        
        self.thread_manager.indicatorTimerUpdate.connect(
            lambda time_str: self.status_indicator_window.update_timer(time_str),
            Qt.ConnectionType.QueuedConnection
        )
        
        # Stream update connection
        self.thread_manager.streamUpdate.connect(
            self.on_stream_update,
            Qt.ConnectionType.QueuedConnection
        )
    
    def apply_instruction_set_settings(self):
        """Apply settings from the selected instruction set to the transcription processor."""
        if not self.pipeline:
            return
        
        # Get the selected instruction set from dropdown
        selected_set = self.get_current_instruction_set()
        if not selected_set:
            return
        
        # Apply the instruction set to the pipeline
        self.pipeline.apply_instruction_set(selected_set)
        
    def get_current_instruction_set(self):
        """
        Get the currently selected instruction set from the dropdown.
        
        Returns
        -------
        InstructionSet or None
            The selected instruction set, or None if not found
        """
        if self.instruction_set_combo.count() == 0:
            return None
            
        selected_name = self.instruction_set_combo.currentText()
        
        # Save the selection in the instruction set manager for persistence
        self.instruction_set_manager.set_selected(selected_name)
        
        # Get and return the instruction set
        return self.instruction_set_manager.get_set_by_name(selected_name)
    
    def init_ui(self):
        """
        Initialize the user interface components.
        
        This method sets up the window size, title, style, layout,
        and places all UI widgets including the toolbar, control panel,
        tab widget for transcription and LLM output, and status bar.
        """
        self.setWindowTitle(AppLabels.APP_TITLE)
        self.setMinimumSize(700, 600)
        
        # Set application icon
        icon_path = get_resource_path(AppConfig.ICON_PATH)
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Use standard icon if icon file is not found
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            print(f"Warning: Icon file not found: {icon_path}")
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create toolbar
        self.create_toolbar()
        
        # Control panel
        control_panel = QWidget()
        control_layout = QGridLayout()
        
        # Recording control
        self.record_button = QPushButton(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
        self.record_button.setMinimumHeight(50)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.clicked.connect(self.toggle_recording)
        
        # Control form
        control_form = QWidget()
        form_layout = QFormLayout(control_form)
        
        # Instruction set selection dropdown
        instruction_set_label = QLabel(AppLabels.MAIN_WIN_INSTRUCTION_SET_LABEL)
        self.instruction_set_combo = QComboBox()
        self.instruction_set_combo.setMinimumWidth(200)
        self.populate_instruction_set_combo()
        self.instruction_set_combo.currentIndexChanged.connect(self.on_instruction_set_changed)
        form_layout.addRow(instruction_set_label, self.instruction_set_combo)
        
        # Add to layout
        control_layout.addWidget(self.record_button, 0, 0, 2, 1)
        control_layout.addWidget(control_form, 0, 1, 2, 5)
        control_layout.setColumnStretch(0, 1)  # Recording button column
        control_layout.setColumnStretch(1, 3)  # Form column
        
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel)
        
        # Output panel with tabs
        self.tab_widget = QTabWidget()
        
        # Transcription tab
        transcription_tab = QWidget()
        transcription_layout = QVBoxLayout(transcription_tab)
        
        # Transcription output
        transcription_label = QLabel(AppLabels.MAIN_WIN_TRANSCRIPTION_OUTPUT_LABEL)
        transcription_layout.addWidget(transcription_label)
        
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText(AppLabels.MAIN_WIN_TRANSCRIPTION_PLACEHOLDER)
        self.transcription_text.setReadOnly(False)  # Editable
        self.transcription_text.setMinimumHeight(250)
        
        transcription_layout.addWidget(self.transcription_text)
        
        # LLM output tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        # LLM output
        llm_label = QLabel(AppLabels.MAIN_WIN_LLM_OUTPUT_LABEL)
        llm_layout.addWidget(llm_label)
        
        self.llm_text = QTextEdit()
        self.llm_text.setPlaceholderText(AppLabels.MAIN_WIN_LLM_PLACEHOLDER)
        self.llm_text.setReadOnly(False)  # Editable
        self.llm_text.setMinimumHeight(250)
        
        llm_layout.addWidget(self.llm_text)
        
        # Markdown output tab
        markdown_tab = QWidget()
        markdown_layout = QVBoxLayout(markdown_tab)
        
        # Markdown output
        markdown_label = QLabel(AppLabels.MAIN_WIN_MARKDOWN_OUTPUT_LABEL)
        markdown_layout.addWidget(markdown_label)
        
        self.markdown_browser = MarkdownTextBrowser()
        self.markdown_browser.setPlaceholderText(AppLabels.MAIN_WIN_MARKDOWN_PLACEHOLDER)
        self.markdown_browser.setMinimumHeight(250)
        
        markdown_layout.addWidget(self.markdown_browser)
        
        # Add tabs
        self.tab_widget.addTab(transcription_tab, AppLabels.MAIN_WIN_TRANSCRIPTION_TAB_TITLE)
        self.tab_widget.addTab(llm_tab, AppLabels.MAIN_WIN_LLM_TAB_TITLE)
        self.tab_widget.addTab(markdown_tab, AppLabels.MAIN_WIN_MARKDOWN_TAB_TITLE)
        
        main_layout.addWidget(self.tab_widget, 1)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(AppLabels.STATUS_READY)
        
        # Recording indicator
        self.recording_indicator = QLabel(AppLabels.STATUS_RECORDING_INDICATOR_STOPPED)
        
        self.recording_timer_label = QLabel(AppLabels.STATUS_TIMER_INITIAL)
        
        self.status_bar.addPermanentWidget(self.recording_indicator)
        self.status_bar.addPermanentWidget(self.recording_timer_label)
        
        # Recording timer setup
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)
        self.recording_start_time = 0
        
        # Complete layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Initialize UIUpdater for thread-safe UI updates
        self.ui_updater = UIUpdater(
            self.status_bar,
            self.recording_indicator,
            self.recording_timer_label
        )
    
    def create_toolbar(self):
        """
        Create the application toolbar.
        
        This method sets up the toolbar with actions for various
        application functions.
        """
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        
        # API key settings
        api_action = QAction(AppLabels.MAIN_WIN_API_KEY_SETTINGS, self)
        api_action.triggered.connect(self.show_api_key_dialog)
        self.toolbar.addAction(api_action)
        
        self.toolbar.addSeparator()
        
        # Instruction sets management
        instruction_sets_action = QAction(AppLabels.MAIN_WIN_INSTRUCTION_SETS_BUTTON, self)
        instruction_sets_action.triggered.connect(self.show_instruction_sets_dialog)
        self.toolbar.addAction(instruction_sets_action)
        
        self.toolbar.addSeparator()
        
        # Copy to clipboard actions
        copy_menu = QMenu(AppLabels.MAIN_WIN_COPY_TO_CLIPBOARD, self)
        
        copy_transcription_action = QAction(AppLabels.MAIN_WIN_COPY_TRANSCRIPTION, self)
        copy_transcription_action.triggered.connect(self.copy_transcription_to_clipboard)
        copy_menu.addAction(copy_transcription_action)
        
        copy_llm_action = QAction(AppLabels.MAIN_WIN_COPY_LLM, self)
        copy_llm_action.triggered.connect(self.copy_llm_to_clipboard)
        copy_menu.addAction(copy_llm_action)
        
        copy_all_action = QAction(AppLabels.MAIN_WIN_COPY_ALL, self)
        copy_all_action.triggered.connect(self.copy_all_to_clipboard)
        copy_menu.addAction(copy_all_action)
        
        copy_action = QAction(AppLabels.MAIN_WIN_COPY_TO_CLIPBOARD, self)
        copy_action.setMenu(copy_menu)
        self.toolbar.addAction(copy_action)
        
        self.toolbar.addSeparator()
        
        # Auto copy setting
        self.auto_copy_action = QAction(AppLabels.MAIN_WIN_AUTO_COPY_BUTTON, self)
        self.auto_copy_action.setCheckable(True)
        self.auto_copy_action.setChecked(self.auto_copy)
        self.auto_copy_action.triggered.connect(self.toggle_auto_copy)
        self.toolbar.addAction(self.auto_copy_action)
        
        self.toolbar.addSeparator()
        
        # Sound setting
        self.sound_action = QAction(AppLabels.MAIN_WIN_SOUND_BUTTON, self)
        self.sound_action.setCheckable(True)
        self.sound_action.setChecked(self.enable_sound)
        self.sound_action.triggered.connect(self.toggle_sound_option)
        self.toolbar.addAction(self.sound_action)
        
        self.toolbar.addSeparator()
        
        # Indicator display setting
        self.indicator_action = QAction(AppLabels.MAIN_WIN_INDICATOR_BUTTON, self)
        self.indicator_action.setCheckable(True)
        self.indicator_action.setChecked(self.show_indicator)
        self.indicator_action.triggered.connect(self.toggle_indicator_option)
        self.toolbar.addAction(self.indicator_action)
        
        self.toolbar.addSeparator()
        
        # Exit application
        exit_action = QAction(AppLabels.MAIN_WIN_EXIT_APP, self)
        exit_action.triggered.connect(self.quit_application)
        self.toolbar.addAction(exit_action)
        
        self.addToolBar(self.toolbar)
    
    def show_api_key_dialog(self):
        """
        Show the OpenAI API key input dialog.
        
        This method displays a dialog for entering, saving, and
        validating the API key.
        """
        dialog = APIKeyDialog(self, self.api_key)
        if dialog.exec():
            self.api_key = dialog.get_api_key()
            self.settings.setValue("api_key", self.api_key)
            
            # Reinitialize processor with new API key
            try:
                self.pipeline = Pipeline(api_key=self.api_key)
                self.apply_instruction_set_settings()
                self.status_bar.showMessage(AppLabels.STATUS_API_KEY_SAVED, 3000)
            except ValueError as e:
                self.pipeline = None
                SimpleMessageDialog.show_message(self, AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE, AppLabels.MAIN_WIN_API_KEY_ERROR_MISSING, SimpleMessageDialog.WARNING)
    
    def toggle_recording(self):
        """
        Toggle recording start/stop.
        
        This method starts or stops recording based on the current state.
        Uses ThreadManager to ensure thread-safe execution in the GUI thread.
        """
        # Use ThreadManager to run in main thread instead of QTimer.singleShot
        self.thread_manager.run_in_main_thread(self._toggle_recording_impl)
    
    def _toggle_recording_impl(self):
        """
        Actual recording toggle implementation.
        
        This method checks the recording state and starts or stops
        recording accordingly.
        """
        if self.pipeline.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self, recording_hotkey=None):
        """
        Start audio recording.
        
        This method starts recording and updates the UI state. It also
        displays the timer during recording and shows the indicator window.
        During recording, only the recording hotkey is active to stop recording.
        
        Parameters
        ----------
        recording_hotkey : str, optional
            The hotkey that triggered recording, by default None
            If None, the main recording hotkey is used
        """
        if not self.pipeline:
            SimpleMessageDialog.show_message(self, AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE, AppLabels.MAIN_WIN_API_KEY_ERROR_REQUIRED, SimpleMessageDialog.WARNING)
            return
        
        try:
            # Try to start recording, which will check for microphone availability
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_STOP_BUTTON)
            self.pipeline.start_recording()
            
            # Use the provided instruction set hotkey
            active_hotkey = recording_hotkey if recording_hotkey else ""
            
            # Signal recording status change through ThreadManager with the active hotkey
            self.thread_manager.recordingStatusChanged.emit(True, active_hotkey)
            
            # Start recording timer using ThreadManager
            self.thread_manager.start_recording_timer()
            
            # Show recording status
            if self.show_indicator:
                # Reset window first
                self.status_indicator_window.hide()
                # Update indicator using ThreadManager
                self.thread_manager.update_indicator(StatusIndicatorWindow.MODE_RECORDING)
                self.status_indicator_window.show()
            
            # Enable recording mode via HotkeyBridge to ensure thread safety
            HotkeyBridge.instance().set_recording_mode(True, active_hotkey)
            
            # Update status using ThreadManager
            self.thread_manager.update_status(AppLabels.STATUS_RECORDING)
            
            # Play start sound
            self.play_start_sound()
            
        except Exception as e:
            # Handle other errors
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
            SimpleMessageDialog.show_message(
                self, 
                AppLabels.MAIN_WIN_MIC_ERROR_TITLE, 
                str(e), 
                SimpleMessageDialog.WARNING
            )
            self.thread_manager.update_status(f"Recording error: {str(e)}", 3000)
    
    def stop_recording(self):
        """
        Stop recording and start processing.
        
        This method stops the recording, saves the temporary file,
        and starts the processing (transcription + optional LLM).
        It also updates the UI state. When recording stops, all
        previously disabled instruction set hotkeys are re-enabled.
        """
        # Use UIUpdater for button text update
        self.ui_updater.update_timer_label(AppLabels.STATUS_TIMER_INITIAL)
        self.record_button.setText(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
        audio_file = self.pipeline.stop_recording()
        
        # Signal recording status change through ThreadManager
        self.thread_manager.recordingStatusChanged.emit(False, "")
        
        # Stop recording timer using ThreadManager
        self.thread_manager.stop_recording_timer()
        
        # Disable recording mode via HotkeyBridge to ensure thread safety
        HotkeyBridge.instance().set_recording_mode(False)
        
        if audio_file:
            # Update status using ThreadManager
            self.thread_manager.update_status(AppLabels.STATUS_TRANSCRIBING)
            self.start_processing(audio_file)
        else:
            # Hide status indicator if no file was created
            self.status_indicator_window.hide()
        
        # Play stop sound
        self.play_stop_sound()
    
    def update_recording_status(self, is_recording, active_hotkey=""):
        """
        Update UI based on recording status.
        
        Parameters
        ----------
        is_recording : bool
            Whether recording is in progress.
        active_hotkey : str, optional
            The hotkey that started recording, by default ""
        """
        self.is_recording = is_recording
        
        if is_recording:
            # Recording active - use UIUpdater for thread safety
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_STOP_BUTTON)
            self.ui_updater.update_status(AppLabels.STATUS_RECORDING)
            self.ui_updater.update_recording_indicator(AppLabels.STATUS_RECORDING_INDICATOR_RECORDING)
            
            if self.show_indicator:
                # Show recording indicator via ThreadManager
                self.thread_manager.update_indicator(StatusIndicatorWindow.MODE_RECORDING)
                self.status_indicator_window.show()
        else:
            # Recording stopped - use UIUpdater for thread safety
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
            self.ui_updater.update_status(AppLabels.STATUS_READY)
            self.ui_updater.update_recording_indicator(AppLabels.STATUS_RECORDING_INDICATOR_STOPPED)
            
            # Reset timer
            self.ui_updater.update_timer_label(AppLabels.STATUS_TIMER_INITIAL)
    
    def update_recording_time(self):
        """
        Update the recording time display.
        
        DEPRECATED: This method is now handled by ThreadManager.
        Kept for backward compatibility only.
        """
        # This functionality has been moved to ThreadManager._update_recording_time
        # which sends signals for both the main UI and indicator window
        pass
        
    def on_recording_hotkey_pressed(self, hotkey_str):
        """
        Handle when the recording hotkey is pressed during recording.
        
        This is called when the HotkeyBridge emits the recordingHotkeyPressed signal.
        It stops the current recording.
        
        Parameters
        ----------
        hotkey_str : str
            The hotkey string that was pressed
        """
        # We're in recording mode and the active recording hotkey was pressed
        # So we should stop recording
        print(f"Recording hotkey '{hotkey_str}' pressed during recording - stopping recording")
        self.thread_manager.run_in_main_thread(self.stop_recording)
    
    def get_clipboard_content(self):
        """
        Get text and/or image from clipboard when LLM clipboard options are enabled.
        
        Returns
        -------
        tuple
            (clipboard_text, clipboard_image) - either may be None if not available or disabled
        """
        clipboard_text = None
        clipboard_image = None
        
        # Only proceed if LLM is enabled
        if self.pipeline and self.pipeline.is_llm_processing_enabled:
            # Get the clipboard manager
            clipboard = QApplication.clipboard()
            
            # Get selected instruction set
            selected_set = self.get_current_instruction_set()
            if selected_set:
                # Check if text clipboard option is enabled
                if selected_set.llm_clipboard_text_enabled:
                    # Get clipboard text
                    clipboard_text = clipboard.text()
                
                # Check if image clipboard option is enabled
                if selected_set.llm_clipboard_image_enabled:
                    # Check if clipboard has an image
                    image = clipboard.image()
                    if not image.isNull():
                        # Convert QImage to bytes
                        buffer = QBuffer()
                        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                        image.save(buffer, "JPEG")
                        clipboard_image = buffer.data().data()  # Get bytes from QByteArray
        
        return clipboard_text, clipboard_image
        
    def start_processing(self, audio_file=None):
        """
        Start audio processing (transcription + optional LLM).
        
        Parameters
        ----------
        audio_file : str, optional
            Path to the audio file to process.
            
        This method starts the processing chain and updates the UI state.
        """
        # Update status using ThreadManager
        self.thread_manager.update_status(AppLabels.STATUS_TRANSCRIBING)
        
        # Show transcribing status
        if self.show_indicator:
            # Reset window first
            self.status_indicator_window.hide()
            # Update indicator using ThreadManager
            self.thread_manager.update_indicator(StatusIndicatorWindow.MODE_PROCESSING)
            self.status_indicator_window.show()
        
        # Get language from selected instruction set
        selected_set = self.get_current_instruction_set()
        selected_language = selected_set.stt_language if selected_set else None
        
        # Get clipboard content (text and/or image) if LLM clipboard option is enabled
        clipboard_text, clipboard_image = self.get_clipboard_content()
        
        # Run processing in worker thread using ThreadManager
        if audio_file:
            self.thread_manager.run_in_worker_thread(
                "audio_processing",
                self.perform_processing,
                audio_file, 
                selected_language,
                clipboard_text,
                clipboard_image
            )
    
    def perform_processing(self, audio_file, language=None, clipboard_text=None, clipboard_image=None):
        """
        Perform audio processing in a background thread.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process.
        language : str, optional
            Language code for transcription.
        clipboard_text : str, optional
            Text from clipboard to include in LLM input, by default None.
        clipboard_image : bytes, optional
            Image data from clipboard to include in LLM input, by default None.
            
        This method uses UnifiedProcessor to process the audio
        and signals the result. It also handles errors appropriately.
        """
        try:
            # Clear LLM text area before streaming starts - using thread manager for thread safety
            self.thread_manager.run_in_main_thread(lambda: self.llm_text.clear())
            
            # Define a streaming callback function that emits streamUpdate signals
            def stream_callback(chunk):
                self.thread_manager.update_stream(chunk)
            
            # Process audio with optional clipboard content (text and/or image) and streaming
            result = self.pipeline.process(
                audio_file, 
                language, 
                clipboard_text, 
                clipboard_image,
                stream_callback=stream_callback
            )
            
            # Signal the result
            self.processing_complete.emit(result)
            
        except Exception as e:
            # Handle errors
            error_msg = f"Error occurred during processing: {str(e)}"
            print(error_msg)
            
            # Create error result
            error_result = PipelineResult(transcription=f"Error: {str(e)}")
            
            # Signal the error result
            self.processing_complete.emit(error_result)
            
            # Show error in status bar using ThreadManager for thread safety
            self.thread_manager.update_status(AppLabels.MAIN_WIN_PROCESSING_ERROR, 5000)
    
    def on_stream_update(self, chunk: str):
        """
        Handle streaming LLM updates.
        
        Parameters
        ----------
        chunk : str
            Text chunk from streaming response.
        """
        # Get current text
        current_text = self.llm_text.toPlainText()
        
        # Append new chunk
        new_text = current_text + chunk
        self.llm_text.setText(new_text)
        
        # Move cursor to end
        cursor = self.llm_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.llm_text.setTextCursor(cursor)
        
        # Update Markdown view with the accumulated text
        self.markdown_browser.setMarkdownText(new_text)
        
        # Ensure Formatted LLM tab is visible during streaming
        self.tab_widget.setCurrentIndex(2)  # Formatted LLM tab
    
    def switch_to_markdown_tab(self):
        """
        Switch to the Markdown view tab.
        
        This method can be used as a convenience method to quickly
        switch to the Markdown view tab.
        """
        # Find the index of the Markdown tab (should be 2, but this is more robust)
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == AppLabels.MAIN_WIN_MARKDOWN_TAB_TITLE:
                self.tab_widget.setCurrentIndex(i)
                break
    
    def on_processing_complete(self, result: PipelineResult):
        """
        Handle processing completion.
        
        Parameters
        ----------
        result : TranscriptionAndLLMResult
            The processing result containing transcription and optional LLM response.
        """
        # Update UI via ThreadManager for thread safety
        if self.show_indicator:
            # Show processing complete indicator via ThreadManager
            self.thread_manager.update_indicator(StatusIndicatorWindow.MODE_COMPLETE)
            
            # Schedule hiding the indicator with ThreadManager instead of QTimer
            self.thread_manager.run_in_main_thread(
                lambda: self.status_indicator_window.hide(),
                delay_ms=AppConfig.DEFAULT_INDICATOR_DISPLAY_TIME
            )
        
        # Show transcription text
        self.transcription_text.setText(result.transcription)
        
        # Show LLM response if available (this may already be shown via streaming)
        if result.llm_processed and result.llm_response:
            # Only set the text if it's not already set by streaming
            if self.llm_text.toPlainText() != result.llm_response:
                self.llm_text.setText(result.llm_response)
            
            # Update the Markdown view with the LLM response
            self.markdown_browser.setMarkdownText(result.llm_response)
            
            # Switch to Formatted LLM tab if LLM processing was performed
            self.tab_widget.setCurrentIndex(2)  # Formatted LLM tab
        else:
            self.llm_text.clear()
            self.markdown_browser.setMarkdownText("")
            # Switch to transcription tab if no LLM processing
            self.tab_widget.setCurrentIndex(0)  # Transcription tab
        
        # Update status via UIUpdater for thread safety
        self.ui_updater.update_status(AppLabels.STATUS_COMPLETE)
        
        # Auto-copy if enabled
        if self.auto_copy:
            if self.pipeline.is_llm_processing_enabled and result.llm_processed and result.llm_response:
                # Copy LLM output if LLM is enabled and result is available
                self.copy_llm_to_clipboard()
            else:
                # Otherwise copy transcription
                self.copy_transcription_to_clipboard()
            
        # Play complete sound
        if self.enable_sound:
            self.play_complete_sound()
    
    def copy_transcription_to_clipboard(self):
        """Copy transcription text to clipboard."""
        text = self.transcription_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.ui_updater.update_status(AppLabels.STATUS_TRANSCRIPTION_COPIED, 2000)
    
    def copy_llm_to_clipboard(self):
        """Copy LLM analysis text to clipboard."""
        text = self.llm_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.ui_updater.update_status(AppLabels.STATUS_LLM_COPIED, 2000)
    
    def copy_all_to_clipboard(self):
        """
        Copy all text (transcription + LLM) to clipboard.
        
        This method formats the combined output with headers.
        """
        transcription = self.transcription_text.toPlainText()
        llm_text = self.llm_text.toPlainText()
        
        # Format with headers if LLM text exists
        if llm_text:
            combined = f"Transcription:\n{transcription}\n\nRaw LLM:\n{llm_text}"
        else:
            combined = transcription
        
        QApplication.clipboard().setText(combined)
        self.ui_updater.update_status(AppLabels.STATUS_ALL_COPIED, 2000)
    
    def setup_connections(self):
        """Set up additional connections."""
        # No additional connections needed
        pass

    def setup_global_hotkey(self):
        """
        Set up the global hotkeys.
        
        Returns
        -------
        bool
            Whether hotkey setup was successful.
            
        This method sets up the global hotkeys for instruction sets.
        The single recording start/stop hotkey has been removed.
        Errors are handled gracefully to allow the application to
        continue functioning.
        """
        try:
            # Clear any existing hotkeys from HotkeyBridge
            HotkeyBridge.instance().clear_all_hotkeys()
            
            # Register instruction set hotkeys
            self.register_instruction_set_hotkeys()
            
            # We consider it a success if we get here without exception
            return True
            
        except Exception as e:
            error_msg = f"Hotkey setup error: {e}"
            print(error_msg)
            # Show error message to user using ThreadManager
            self.thread_manager.update_status(
                AppLabels.HOTKEY_VALIDATION_ERROR_TITLE + ": " + str(e), 
                5000
            )
            # Continue with application even if hotkey fails
            return False
    
    def register_instruction_set_hotkeys(self):
        """
        Register hotkeys for all instruction sets.
        
        Each instruction set hotkey will start recording when pressed, and stop recording
        when pressed again during recording.
        """
        # Register hotkeys for all instruction sets with defined hotkeys
        for instruction_set in self.instruction_set_manager.get_all_sets():
            if instruction_set.hotkey:
                # Register the hotkey using ThreadManager
                handler_id = f"instruction_set_{instruction_set.name}"
                # Create a lambda with the instruction set - use default argument to capture current value
                callback = lambda set_name=instruction_set.name: self.handle_instruction_set_hotkey(set_name)
                
                # Register the hotkey
                if self.thread_manager.register_hotkey_handler(instruction_set.hotkey, handler_id, callback):
                    print(f"Instruction set hotkey '{instruction_set.hotkey}' registered for '{instruction_set.name}'")
                else:
                    print(f"Failed to register hotkey '{instruction_set.hotkey}' for instruction set '{instruction_set.name}'")
    
    def select_instruction_set_by_name(self, name: str):
        """
        Select an instruction set by name and apply its settings.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select.
        """
        if self.instruction_set_manager.set_selected(name):
            # Update dropdown selection to match, blocking signals to avoid recursion
            self.instruction_set_combo.blockSignals(True)
            index = self.instruction_set_combo.findText(name)
            if index >= 0:
                self.instruction_set_combo.setCurrentIndex(index)
            self.instruction_set_combo.blockSignals(False)
            
            # Apply settings
            self.apply_instruction_set_settings()
            
            # Show status message
            self.status_bar.showMessage(
                AppLabels.STATUS_INSTRUCTION_SET_SELECTED_BY_HOTKEY.format(name),
                3000
            )
    
    def handle_instruction_set_hotkey(self, set_name: str):
        """
        Handle instruction set hotkey press.
        
        If not recording, activate the instruction set and start recording.
        If already recording, stop recording only if the pressed hotkey
        is the same as the one that started recording.
        
        Parameters
        ----------
        set_name : str
            The name of the instruction set to activate.
        """
        hotkey_bridge = HotkeyBridge.instance()
        instruction_set = self.instruction_set_manager.get_set_by_name(set_name)
        
        if not instruction_set:
            print(f"Warning: Instruction set '{set_name}' not found")
            return
            
        # Get the hotkey for this instruction set
        hotkey = instruction_set.hotkey
        
        # Check if we're currently recording
        if self.pipeline.is_recording:
            # Only stop recording if this is the same hotkey that started recording
            if hotkey == hotkey_bridge.get_active_recording_hotkey():
                self.stop_recording()
            # Otherwise ignore the hotkey
        else:
            # Select the instruction set
            self.select_instruction_set_by_name(set_name)
            
            # Start recording
            self.start_recording(hotkey)
        
    def activate_instruction_set_by_name(self, name: str):
        """
        For backward compatibility - delegates to select_instruction_set_by_name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to activate.
        """
        self.select_instruction_set_by_name(name)
    
    def show_instruction_sets_dialog(self):
        """
        Show the instruction sets management dialog.
        
        This method displays a dialog for managing instruction sets,
        including vocabulary, system instructions, and LLM settings.
        It requires an API key to be set.
        
        Note: Hotkeys are automatically disabled/re-enabled by the InstructionSetsDialog class.
        """
        if not self.pipeline:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE,
                AppLabels.MAIN_WIN_API_KEY_ERROR_REQUIRED,
                SimpleMessageDialog.WARNING,
                self.thread_manager
            )
            return
            
        # Create dialog with thread manager for thread-safe operations
        dialog = InstructionSetsDialog(self, self.instruction_set_manager, self.hotkey_manager, self.thread_manager)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get updated manager
            updated_manager = dialog.get_manager()
            self.instruction_set_manager = updated_manager
            
            # Apply settings from selected instruction set
            self.apply_instruction_set_settings()
            
            # Re-register hotkeys
            self.setup_global_hotkey()
            
            # Update the instruction set dropdown
            self.populate_instruction_set_combo()
            
            # Show status message using ThreadManager for thread safety
            selected_set_name = self.instruction_set_manager.get_selected_set_name()
            if selected_set_name:
                self.thread_manager.update_status(
                    AppLabels.STATUS_INSTRUCTION_SET_SELECTED.format(selected_set_name),
                    3000
                )
    
    def toggle_auto_copy(self):
        """
        Toggle auto-copy feature on/off.
        
        This method toggles whether processing results are
        automatically copied to the clipboard, and saves the setting.
        """
        self.auto_copy = self.auto_copy_action.isChecked()
        self.settings.setValue("auto_copy", self.auto_copy)
        if self.auto_copy:
            self.ui_updater.update_status(AppLabels.STATUS_AUTO_COPY_ENABLED, 2000)
        else:
            self.ui_updater.update_status(AppLabels.STATUS_AUTO_COPY_DISABLED, 2000)
    
    def toggle_sound_option(self):
        """
        Toggle notification sounds on/off.
        
        Saves the setting and shows status in the status bar.
        """
        self.enable_sound = self.sound_action.isChecked()
        self.settings.setValue("enable_sound", self.enable_sound)
        if self.enable_sound:
            self.ui_updater.update_status(AppLabels.STATUS_SOUND_ENABLED, 2000)
        else:
            self.ui_updater.update_status(AppLabels.STATUS_SOUND_DISABLED, 2000)

    def toggle_indicator_option(self):
        """
        Toggle indicator display on/off.
        
        Saves the setting and shows status in the status bar.
        Also hides the indicator if turned off.
        """
        self.show_indicator = self.indicator_action.isChecked()
        self.settings.setValue("show_indicator", self.show_indicator)
        
        # Hide indicator if disabled
        if not self.show_indicator:
            self.status_indicator_window.hide()
            
        if self.show_indicator:
            self.ui_updater.update_status(AppLabels.STATUS_INDICATOR_SHOWN, 2000)
        else:
            self.ui_updater.update_status(AppLabels.STATUS_INDICATOR_HIDDEN, 2000)
    
    def quit_application(self):
        """
        Completely exit the application.
        
        This method hides the tray icon, saves settings, and exits
        the application.
        """
        # Stop keyboard listener
        self.hotkey_manager.stop_listening()
            
        # Hide tray icon
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        # Save settings
        self.settings.sync()
        
        # Exit application
        QApplication.quit()
    
    def setup_sound_players(self):
        """Initialize the sound players."""
        # Start recording sound player
        self.start_player = QMediaPlayer()
        self.start_audio_output = QAudioOutput()
        self.start_player.setAudioOutput(self.start_audio_output)
        
        # Stop recording sound player
        self.stop_player = QMediaPlayer()
        self.stop_audio_output = QAudioOutput()
        self.stop_player.setAudioOutput(self.stop_audio_output)
        
        # Transcription complete sound player
        self.complete_player = QMediaPlayer()
        self.complete_audio_output = QAudioOutput()
        self.complete_player.setAudioOutput(self.complete_audio_output)
    
    def play_start_sound(self):
        """
        Play recording start sound.
        
        Only plays if enable_sound is True.
        """
        if not self.enable_sound:
            return
        # Use sound file from assets
        sound_path = get_resource_path(AppConfig.START_SOUND_PATH)
        self.start_player.setSource(QUrl.fromLocalFile(sound_path))
        self.start_audio_output.setVolume(0.5)
        self.start_player.play()
    
    def play_stop_sound(self):
        """
        Play recording stop sound.
        
        Only plays if enable_sound is True.
        """
        if not self.enable_sound:
            return
        # Use sound file from assets
        sound_path = get_resource_path(AppConfig.STOP_SOUND_PATH)
        self.stop_player.setSource(QUrl.fromLocalFile(sound_path))
        self.stop_audio_output.setVolume(0.5)
        self.stop_player.play()
    
    def play_complete_sound(self):
        """
        Play processing complete sound.
        
        Only plays if enable_sound is True.
        """
        if not self.enable_sound:
            return
        # Use sound file from assets
        sound_path = get_resource_path(AppConfig.COMPLETE_SOUND_PATH)
        self.complete_player.setSource(QUrl.fromLocalFile(sound_path))
        self.complete_audio_output.setVolume(0.5)
        self.complete_player.play()

    def setup_system_tray(self):
        """
        Set up system tray icon and menu.
        
        This method initializes the system tray icon and creates a
        context menu with options to show the application, start/stop
        recording, and exit the application.
        """
        # Get icon file path
        icon_path = get_resource_path(AppConfig.ICON_PATH)
        
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            # Use standard icon if icon file is not found
            self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), self)
            print(f"Warning: System tray icon file not found: {icon_path}")
        
        self.tray_icon.setToolTip(AppLabels.APP_TITLE)
        
        # Create tray menu
        menu = QMenu()
        
        # Add show/hide action
        show_action = QAction(AppLabels.TRAY_SHOW, self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        # Add separator
        menu.addSeparator()
        
        # Add recording action
        record_action = QAction(AppLabels.TRAY_RECORD, self)
        record_action.triggered.connect(self.toggle_recording)
        menu.addAction(record_action)
        
        # Add separator
        menu.addSeparator()
        
        # Add exit action
        exit_action = QAction(AppLabels.TRAY_EXIT, self)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """
        Handle tray icon activation.
        
        Parameters
        ----------
        reason : QSystemTrayIcon.ActivationReason
            The reason for activation.
            
        This method toggles the window's visibility when the tray
        icon is clicked.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def closeEvent(self, event):
        """
        Handle window close event.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event.
            
        This method handles window close button clicks. Alt+F4
        completely exits, other close actions minimize to tray.
        """
        # Called by Alt+F4 or system close request
        
        # Alt key pressed = complete exit
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            self.quit_application()
            event.accept()
        # Normal close = minimize to tray
        elif self.tray_icon.isVisible():
            SimpleMessageDialog.show_message(self, AppLabels.MAIN_WIN_INFO_TRAY_TITLE, AppLabels.MAIN_WIN_INFO_TRAY_MESSAGE, SimpleMessageDialog.INFO)
            self.hide()
            event.ignore()
        else:
            event.accept()
            
    def populate_instruction_set_combo(self):
        """
        Populate the instruction set selection dropdown.
        
        This method adds all available instruction sets to the dropdown
        and selects the currently selected one from the instruction set manager.
        """
        # Temporarily block signals to prevent triggering the change event
        self.instruction_set_combo.blockSignals(True)
        
        # Clear existing items
        self.instruction_set_combo.clear()
        
        # Add all instruction sets
        for instruction_set in self.instruction_set_manager.get_all_sets():
            self.instruction_set_combo.addItem(instruction_set.name)
            
            # Add tooltip with hotkey if available
            if instruction_set.hotkey:
                self.instruction_set_combo.setItemData(
                    self.instruction_set_combo.count() - 1,
                    f"Hotkey: {instruction_set.hotkey}",
                    Qt.ItemDataRole.ToolTipRole
                )
        
        # Select the currently selected set from manager
        selected_set_name = self.instruction_set_manager.get_selected_set_name()
        if selected_set_name:
            index = self.instruction_set_combo.findText(selected_set_name)
            if index >= 0:
                self.instruction_set_combo.setCurrentIndex(index)
        elif self.instruction_set_combo.count() > 0:
            # If no selected set but we have items, select the first one
            self.instruction_set_combo.setCurrentIndex(0)
            # Save this selection in the manager
            self.instruction_set_manager.set_selected(self.instruction_set_combo.currentText())
        
        # Unblock signals
        self.instruction_set_combo.blockSignals(False)
    
    def on_instruction_set_changed(self, index):
        """
        Handle instruction set selection change.
        
        Parameters
        ----------
        index : int
            The index of the selected instruction set.
        """
        if index < 0:
            return
            
        # Get the selected instruction set name
        set_name = self.instruction_set_combo.itemText(index)
        
        # Save the selection and apply settings
        self.instruction_set_manager.set_selected(set_name)
        self.apply_instruction_set_settings()
        
        # Show status message
        self.status_bar.showMessage(
            f"Selected instruction set: {set_name}",
            3000
        )


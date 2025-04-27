"""
Main Window Module with LLM Integration

This module provides the main application window and core functionality
with integrated LLM processing support.
"""

import os
import sys
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QCheckBox,
    QGridLayout, QFormLayout, QTabWidget, QSplitter,
    QSystemTrayIcon, QMenu, QStyle, QStatusBar, QToolBar, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings, QUrl, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.recorder import AudioRecorder
from core.processor import UnifiedProcessor, ProcessingResult

from core.hotkeys import HotkeyManager
from gui.resources.config import AppConfig
from gui.resources.labels import AppLabels
from gui.dialogs.api_key_dialog import APIKeyDialog
from gui.dialogs.hotkey_dialog import HotkeyDialog
from gui.dialogs.instruction_sets_dialog import InstructionSetsDialog, GUIInstructionSetManager
from gui.dialogs.simple_message_dialog import SimpleMessageDialog
from gui.components.widgets.status_indicator import StatusIndicatorWindow
from gui.utils.resource_helper import getResourcePath

# Thread management imports
from gui.thread_management.thread_manager import ThreadManager
from gui.thread_management.ui_updater import UIUpdater


class MainWindow(QMainWindow):
    """
    Main application window.
    
    This class provides the main user interface and integrates the audio
    recording, transcription, and LLM (Large Language Model) processing functionality.
    It manages the core application flow and user interactions.
    """
    
    # Custom signals
    processing_complete = pyqtSignal(ProcessingResult)
    recording_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        """
        Initialize the MainWindow.
        """
        super().__init__()
        
        # Load settings
        self.settings = QSettings(AppConfig.APP_ORGANIZATION, AppConfig.APP_NAME)
        self.api_key = self.settings.value("api_key", AppConfig.DEFAULT_API_KEY)
        
        # Hotkey and clipboard settings
        self.hotkey = self.settings.value("hotkey", AppConfig.DEFAULT_HOTKEY)
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
        self.audio_recorder = None
        self.unified_processor = None
        
        # Recording state
        self.is_recording = False
        
        # Sound settings
        self.enable_sound = self.settings.value("enable_sound", AppConfig.DEFAULT_ENABLE_SOUND, type=bool)
        
        # Indicator display settings
        self.show_indicator = self.settings.value("show_indicator", AppConfig.DEFAULT_SHOW_INDICATOR, type=bool)
        
        # Initialize sound players
        self.setup_sound_players()
        
        # Initialize components
        self.audio_recorder = AudioRecorder()
        
        # Status indicator window
        self.status_indicator_window = StatusIndicatorWindow()
        self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
        
        # Initialize unified processor if API key is available
        try:
            self.unified_processor = UnifiedProcessor(api_key=self.api_key)
            
            # Apply settings from active instruction set
            if self.instruction_set_manager.active_set:
                self.apply_instruction_set_settings()
                
        except ValueError:
            self.unified_processor = None
        
        # Set up UI
        self.init_ui()
        
        # Set up ThreadManager signal connections
        self._setup_thread_manager_connections()
        
        # Connect signals
        self.processing_complete.connect(self.on_processing_complete, Qt.ConnectionType.QueuedConnection)
        self.recording_status_changed.connect(self.update_recording_status, Qt.ConnectionType.QueuedConnection)
        
        # Connect status indicator window to ThreadManager
        self.status_indicator_window.connect_to_thread_manager(self.thread_manager)
        
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
    
    def apply_instruction_set_settings(self):
        """Apply settings from the active instruction set to the unified processor."""
        if not self.unified_processor or not self.instruction_set_manager.active_set:
            return
        
        active_set = self.instruction_set_manager.active_set
        
        # Clear existing settings
        self.unified_processor.clear_custom_vocabulary()
        self.unified_processor.clear_transcription_instructions()
        self.unified_processor.clear_llm_instructions()
        
        # Apply vocabulary
        self.unified_processor.add_custom_vocabulary(active_set.vocabulary)
        
        # Apply transcription instructions
        self.unified_processor.add_transcription_instruction(active_set.instructions)
        
        # Set whisper model
        if active_set.model:
            self.unified_processor.set_whisper_model(active_set.model)
        
        # LLM settings
        self.unified_processor.enable_llm(active_set.llm_enabled)
        
        # Set LLM model
        if active_set.llm_model:
            self.unified_processor.set_llm_model(active_set.llm_model)
        
        # Apply LLM instructions
        self.unified_processor.add_llm_instruction(active_set.llm_instructions)
    
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
        icon_path = getResourcePath("assets/icon.png")
        
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
        
        # LLM Processing control
        self.llm_enabled_checkbox = QCheckBox(AppLabels.MAIN_WIN_LLM_ENABLED)
        self.llm_enabled_checkbox.setChecked(
            self.unified_processor.is_llm_enabled() if self.unified_processor else False
        )
        self.llm_enabled_checkbox.toggled.connect(self.toggle_llm_processing)
        
        # Control form
        control_form = QWidget()
        form_layout = QFormLayout(control_form)
        
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
        
        # Add tabs
        self.tab_widget.addTab(transcription_tab, AppLabels.MAIN_WIN_TRANSCRIPTION_TAB_TITLE)
        self.tab_widget.addTab(llm_tab, AppLabels.MAIN_WIN_LLM_TAB_TITLE)
        
        main_layout.addWidget(self.tab_widget, 1)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(AppLabels.STATUS_READY)
        
        # Recording indicator
        self.recording_indicator = QLabel(AppLabels.STATUS_RECORDING_INDICATOR)
        
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
        
        # Hotkey settings
        hotkey_action = QAction(AppLabels.MAIN_WIN_HOTKEY_SETTINGS, self)
        hotkey_action.triggered.connect(self.show_hotkey_dialog)
        self.toolbar.addAction(hotkey_action)
        
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
                self.unified_processor = UnifiedProcessor(api_key=self.api_key)
                self.apply_instruction_set_settings()
                self.status_bar.showMessage(AppLabels.STATUS_API_KEY_SAVED, 3000)
            except ValueError as e:
                self.unified_processor = None
                SimpleMessageDialog.show_message(self, AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE, AppLabels.MAIN_WIN_API_KEY_ERROR_MISSING, SimpleMessageDialog.WARNING)
    
    def toggle_llm_processing(self, enabled):
        """
        Toggle LLM processing on/off.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable LLM processing.
        """
        if self.unified_processor:
            self.unified_processor.enable_llm(enabled)
            
            # Update active instruction set
            if self.instruction_set_manager.active_set:
                self.instruction_set_manager.update_set(
                    self.instruction_set_manager.active_set.name,
                    llm_enabled=enabled
                )
            
            # Update status bar via UIUpdater for thread safety
            if enabled:
                self.ui_updater.update_status(AppLabels.STATUS_LLM_ENABLED, 2000)
            else:
                self.ui_updater.update_status(AppLabels.STATUS_LLM_DISABLED, 2000)
    
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
        if self.audio_recorder.is_recording():
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """
        Start audio recording.
        
        This method starts recording and updates the UI state. It also
        displays the timer during recording and shows the indicator window.
        When recording starts, all instruction set hotkeys are temporarily
        disabled so only the main recording hotkey works.
        """
        if not self.unified_processor:
            SimpleMessageDialog.show_message(self, AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE, AppLabels.MAIN_WIN_API_KEY_ERROR_REQUIRED, SimpleMessageDialog.WARNING)
            return
            
        # Use UIUpdater for button text update
        self.record_button.setText(AppLabels.MAIN_WIN_RECORD_STOP_BUTTON)
        self.audio_recorder.start_recording()
        
        # Signal recording status change through ThreadManager
        self.thread_manager.recordingStatusChanged.emit(True)
        
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
        from gui.thread_management.hotkey_bridge import HotkeyBridge
        HotkeyBridge.instance().set_recording_mode(True, self.hotkey)
        
        # Disable instruction set hotkeys during recording (for backward compatibility)
        self.disable_instruction_set_hotkeys()
        
        # Update status using ThreadManager
        self.thread_manager.update_status(AppLabels.STATUS_RECORDING)
        
        # Play start sound
        self.play_start_sound()
    
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
        audio_file = self.audio_recorder.stop_recording()
        
        # Signal recording status change through ThreadManager
        self.thread_manager.recordingStatusChanged.emit(False)
        
        # Stop recording timer using ThreadManager
        self.thread_manager.stop_recording_timer()
        
        # Disable recording mode via HotkeyBridge to ensure thread safety
        from gui.thread_management.hotkey_bridge import HotkeyBridge
        HotkeyBridge.instance().set_recording_mode(False)
        
        # Re-enable instruction set hotkeys (for backward compatibility)
        self.restore_instruction_set_hotkeys()
        
        if audio_file:
            # Update status using ThreadManager
            self.thread_manager.update_status(AppLabels.STATUS_TRANSCRIBING)
            self.start_processing(audio_file)
        else:
            # Hide status indicator if no file was created
            self.status_indicator_window.hide()
        
        # Play stop sound
        self.play_stop_sound()
    
    def update_recording_status(self, is_recording):
        """
        Update UI based on recording status.
        
        Parameters
        ----------
        is_recording : bool
            Whether recording is in progress.
        """
        self.is_recording = is_recording
        
        if is_recording:
            # Recording active - use UIUpdater for thread safety
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_STOP_BUTTON)
            self.ui_updater.update_status(AppLabels.STATUS_RECORDING)
            self.ui_updater.update_recording_indicator(is_recording)
            
            if self.show_indicator:
                # Show recording indicator via ThreadManager
                self.thread_manager.update_indicator(StatusIndicatorWindow.MODE_RECORDING)
                self.status_indicator_window.show()
        else:
            # Recording stopped - use UIUpdater for thread safety
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
            self.ui_updater.update_status(AppLabels.STATUS_READY)
            self.ui_updater.update_recording_indicator(is_recording)
            
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
        
        # Get language from active instruction set
        selected_language = self.instruction_set_manager.get_active_language()
        
        # Run processing in worker thread using ThreadManager
        if audio_file:
            self.thread_manager.run_in_worker_thread(
                "audio_processing",
                self.perform_processing,
                audio_file, 
                selected_language
            )
    
    def perform_processing(self, audio_file, language=None):
        """
        Perform audio processing in a background thread.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process.
        language : str, optional
            Language code for transcription.
            
        This method uses UnifiedProcessor to process the audio
        and signals the result. It also handles errors appropriately.
        """
        try:
            # Process audio
            result = self.unified_processor.process(audio_file, language)
            
            # Signal the result
            self.processing_complete.emit(result)
            
        except Exception as e:
            # Handle errors
            error_msg = f"Error occurred during processing: {str(e)}"
            print(error_msg)
            
            # Create error result
            error_result = ProcessingResult(transcription=f"Error: {str(e)}")
            
            # Signal the error result
            self.processing_complete.emit(error_result)
            
            # Show error in status bar using ThreadManager for thread safety
            self.thread_manager.update_status(AppLabels.MAIN_WIN_PROCESSING_ERROR, 5000)
    
    def on_processing_complete(self, result):
        """
        Handle processing completion.
        
        Parameters
        ----------
        result : ProcessingResult
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
        
        # Show LLM response if available
        if result.llm_processed and result.llm_response:
            self.llm_text.setText(result.llm_response)
            # Switch to LLM tab if LLM processing was performed
            self.tab_widget.setCurrentIndex(1)  # LLM tab
        else:
            self.llm_text.clear()
            # Switch to transcription tab if no LLM processing
            self.tab_widget.setCurrentIndex(0)  # Transcription tab
        
        # Update status via UIUpdater for thread safety
        self.ui_updater.update_status(AppLabels.STATUS_COMPLETE)
        
        # Auto-copy if enabled
        if self.auto_copy:
            if self.unified_processor.is_llm_enabled() and result.llm_processed and result.llm_response:
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
            combined = f"Transcription:\n{transcription}\n\nLLM Analysis:\n{llm_text}"
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
        Set up the global hotkey.
        
        Returns
        -------
        bool
            Whether hotkey setup was successful.
            
        This method sets up the global hotkey for the application.
        Errors are handled gracefully to allow the application to
        continue functioning.
        """
        try:
            # Clear any existing hotkeys from HotkeyBridge
            from gui.thread_management.hotkey_bridge import HotkeyBridge
            HotkeyBridge.instance().clear_all_hotkeys()
            
            # Register the main recording toggle hotkey using ThreadManager
            result = self.thread_manager.register_hotkey_handler(
                self.hotkey,
                "main_recording_toggle",
                self.toggle_recording
            )
            
            if result:
                print(f"Hotkey '{self.hotkey}' has been set successfully")
                
                # Register instruction set hotkeys
                self.register_instruction_set_hotkeys()
                
                return True
            else:
                raise ValueError(f"Failed to register hotkey: {self.hotkey}")
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
        """Register hotkeys for all instruction sets."""
        # Register hotkeys for all instruction sets with defined hotkeys
        for instruction_set in self.instruction_set_manager.get_all_sets():
            if instruction_set.hotkey:
                # Check for conflict with main hotkey
                if instruction_set.hotkey == self.hotkey:
                    print(f"Warning: Instruction set '{instruction_set.name}' hotkey '{instruction_set.hotkey}' conflicts with main recording hotkey")
                    continue
                
                # Register the hotkey using ThreadManager
                handler_id = f"instruction_set_{instruction_set.name}"
                # Create a lambda with the instruction set - use default argument to capture current value
                callback = lambda set_name=instruction_set.name: self.handle_instruction_set_hotkey(set_name)
                
                # Register the hotkey
                if self.thread_manager.register_hotkey_handler(instruction_set.hotkey, handler_id, callback):
                    print(f"Instruction set hotkey '{instruction_set.hotkey}' registered for '{instruction_set.name}'")
                else:
                    print(f"Failed to register hotkey '{instruction_set.hotkey}' for instruction set '{instruction_set.name}'")
    
    def activate_instruction_set_by_name(self, name: str):
        """
        Activate an instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to activate.
        """
        if self.instruction_set_manager.set_active(name):
            self.apply_instruction_set_settings()
            self.status_bar.showMessage(
                AppLabels.STATUS_INSTRUCTION_SET_ACTIVATED_BY_HOTKEY.format(name),
                3000
            )
    
    def handle_instruction_set_hotkey(self, set_name: str):
        """
        Handle instruction set hotkey press.
        
        Parameters
        ----------
        set_name : str
            The name of the instruction set to activate.
        """
        self.activate_instruction_set_by_name(set_name)
    
    def disable_instruction_set_hotkeys(self):
        """
        Temporarily disable all instruction set hotkeys during recording.
        
        This method saves the current instruction set hotkeys and then
        unregisters them to ensure only the main recording hotkey works
        during recording.
        """
        # Clear the saved hotkeys list
        self.instruction_set_hotkeys = []
        
        # Get HotkeyBridge instance
        from gui.thread_management.hotkey_bridge import HotkeyBridge
        hotkey_bridge = HotkeyBridge.instance()
        
        # Save and unregister instruction set hotkeys
        for instruction_set in self.instruction_set_manager.get_all_sets():
            if instruction_set.hotkey and instruction_set.hotkey != self.hotkey:
                # Save hotkey info for later restoration
                self.instruction_set_hotkeys.append({
                    'name': instruction_set.name,
                    'hotkey': instruction_set.hotkey
                })
                
                # Unregister the hotkey using HotkeyBridge
                hotkey_bridge.unregister_hotkey(instruction_set.hotkey)
                
        print(f"Disabled {len(self.instruction_set_hotkeys)} instruction set hotkeys during recording")
    
    def restore_instruction_set_hotkeys(self):
        """
        Restore previously disabled instruction set hotkeys after recording.
        
        This method re-registers all instruction set hotkeys that were
        disabled during recording.
        """
        # Re-register saved hotkeys
        for hotkey_info in self.instruction_set_hotkeys:
            set_name = hotkey_info['name']
            hotkey = hotkey_info['hotkey']
            
            # Create handler ID for ThreadManager
            handler_id = f"instruction_set_{set_name}"
            
            # Create callback function
            callback = lambda name=set_name: self.handle_instruction_set_hotkey(name)
            
            # Register the hotkey using ThreadManager
            if self.thread_manager.register_hotkey_handler(hotkey, handler_id, callback):
                print(f"Restored hotkey '{hotkey}' for instruction set '{set_name}'")
            else:
                print(f"Failed to restore hotkey '{hotkey}' for instruction set '{set_name}'")
        
        # Clear the saved hotkeys list
        self.instruction_set_hotkeys = []
    
    def show_hotkey_dialog(self):
        """
        Show the global hotkey settings dialog.
        
        This method displays a dialog for changing the hotkey setting.
        The current hotkey is temporarily released during dialog display.
        Hotkeys are automatically disabled/re-enabled by the HotkeyDialog class.
        """
        # Create dialog with thread manager for thread-safe operations
        dialog = HotkeyDialog(self, self.hotkey, self.thread_manager)
        
        # Show dialog
        if dialog.exec():
            new_hotkey = dialog.get_hotkey()
            if new_hotkey:
                self.hotkey = new_hotkey
                self.settings.setValue("hotkey", self.hotkey)
                self.setup_global_hotkey()
                
                # Show status message using ThreadManager for thread safety
                self.thread_manager.update_status(
                    AppLabels.STATUS_HOTKEY_SET.format(self.hotkey), 
                    3000
                )
        else:
            # Restore original hotkey if dialog was canceled
            # HotkeyDialog.reject() already handles restoring the original hotkey value
            # We just need to make sure the hotkey is properly registered
            self.setup_global_hotkey()
            
    def show_instruction_sets_dialog(self):
        """
        Show the instruction sets management dialog.
        
        This method displays a dialog for managing instruction sets,
        including vocabulary, system instructions, and LLM settings.
        It requires an API key to be set.
        
        Note: Hotkeys are automatically disabled/re-enabled by the InstructionSetsDialog class.
        """
        if not self.unified_processor:
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
            
            # Apply settings from active instruction set
            self.apply_instruction_set_settings()
            
            # Update UI to reflect LLM enabled state
            self.llm_enabled_checkbox.setChecked(self.unified_processor.is_llm_enabled())
            
            # Re-register hotkeys
            self.setup_global_hotkey()
            
            # Show status message using ThreadManager for thread safety
            if self.instruction_set_manager.active_set:
                self.thread_manager.update_status(
                    AppLabels.STATUS_INSTRUCTION_SET_ACTIVE.format(self.instruction_set_manager.active_set.name),
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
        self.hotkey_manager.stop_listener()
            
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
        sound_path = getResourcePath(AppConfig.START_SOUND_PATH)
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
        sound_path = getResourcePath(AppConfig.STOP_SOUND_PATH)
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
        sound_path = getResourcePath(AppConfig.COMPLETE_SOUND_PATH)
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
        icon_path = getResourcePath("assets/icon.png")
        
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

"""
Main Window Module with LLM Integration

This module provides the main application window and core functionality
with integrated LLM processing support.
"""

import os
import sys
import threading
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
        
        # Initialize hotkey manager
        self.hotkey_manager = HotkeyManager()
        
        # Initialize instruction set manager
        self.instruction_set_manager = GUIInstructionSetManager(self.settings)
        
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
        
        # Connect signals
        self.processing_complete.connect(self.on_processing_complete)
        self.recording_status_changed.connect(self.update_recording_status)
        
        # Check API key
        if not self.api_key:
            self.show_api_key_dialog()
            
        # Set up additional connections
        self.setup_connections()
        
        # Set up global hotkey
        self.setup_global_hotkey()
        
        # Set up system tray
        self.setup_system_tray()
    
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
            
            # Update status bar
            if enabled:
                self.status_bar.showMessage(AppLabels.STATUS_LLM_ENABLED, 2000)
            else:
                self.status_bar.showMessage(AppLabels.STATUS_LLM_DISABLED, 2000)
    
    def toggle_recording(self):
        """
        Toggle recording start/stop.
        
        This method starts or stops recording based on the current state.
        """
        # Use QTimer.singleShot to ensure execution in GUI thread
        QTimer.singleShot(0, self._toggle_recording_impl)
    
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
        """
        if not self.unified_processor:
            SimpleMessageDialog.show_message(self, AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE, AppLabels.MAIN_WIN_API_KEY_ERROR_REQUIRED, SimpleMessageDialog.WARNING)
            return
            
        self.record_button.setText(AppLabels.MAIN_WIN_RECORD_STOP_BUTTON)
        self.audio_recorder.start_recording()
        self.recording_status_changed.emit(True)
        
        # Start recording timer
        self.recording_start_time = time.time()
        self.recording_timer.start(1000)  # Update every second
        
        # Show recording status
        if self.show_indicator:
            # Reset window first
            self.status_indicator_window.hide()
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
            self.status_indicator_window.show()
        
        self.status_bar.showMessage(AppLabels.STATUS_RECORDING)
        
        # Play start sound
        self.play_start_sound()
    
    def stop_recording(self):
        """
        Stop recording and start processing.
        
        This method stops the recording, saves the temporary file,
        and starts the processing (transcription + optional LLM).
        It also updates the UI state.
        """
        self.record_button.setText(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
        audio_file = self.audio_recorder.stop_recording()
        self.recording_status_changed.emit(False)
        
        # Stop recording timer
        self.recording_timer.stop()
        
        if audio_file:
            self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBING)
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
            # Recording active
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_STOP_BUTTON)
            self.status_bar.showMessage(AppLabels.STATUS_RECORDING)
            
            if self.show_indicator:
                # Show recording indicator
                self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
                self.status_indicator_window.show()
        else:
            # Recording stopped
            self.record_button.setText(AppLabels.MAIN_WIN_RECORD_START_BUTTON)
            self.status_bar.showMessage(AppLabels.STATUS_READY)
            
            # Reset timer
            self.recording_timer_label.setText(AppLabels.STATUS_TIMER_INITIAL)
    
    def update_recording_time(self):
        """
        Update the recording time display.
        
        This method calculates elapsed time and updates the timer display.
        It also updates the timer in the indicator window.
        """
        if self.audio_recorder.is_recording():
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.recording_timer_label.setText(time_str)
            
            # Update timer in recording indicator window
            self.status_indicator_window.update_timer(time_str)
    
    def start_processing(self, audio_file=None):
        """
        Start audio processing (transcription + optional LLM).
        
        Parameters
        ----------
        audio_file : str, optional
            Path to the audio file to process.
            
        This method starts the processing chain and updates the UI state.
        """
        self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBING)
        
        # Show transcribing status
        if self.show_indicator:
            # Reset window first
            self.status_indicator_window.hide()
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_PROCESSING)
            self.status_indicator_window.show()
        
        # Get language from active instruction set
        selected_language = self.instruction_set_manager.get_active_language()
        
        # Run processing in background thread
        if audio_file:
            processing_thread = threading.Thread(
                target=self.perform_processing,
                args=(audio_file, selected_language)
            )
            processing_thread.daemon = True
            processing_thread.start()
    
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
            # Create error result
            error_result = ProcessingResult(transcription=f"Error: {str(e)}")
            # Signal the error result
            self.processing_complete.emit(error_result)
            # Show error in status bar
            QTimer.singleShot(0, lambda: self.status_bar.showMessage(AppLabels.MAIN_WIN_PROCESSING_ERROR, 5000))
    
    def on_processing_complete(self, result):
        """
        Handle processing completion.
        
        Parameters
        ----------
        result : ProcessingResult
            The processing result containing transcription and optional LLM response.
        """
        # Update UI
        if self.show_indicator:
            # Show processing complete indicator
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_COMPLETE)
            
            # Set timer to hide indicator after configured time
            QTimer.singleShot(AppConfig.DEFAULT_INDICATOR_DISPLAY_TIME, lambda: self.status_indicator_window.hide())
        
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
        
        # Update status
        self.status_bar.showMessage(AppLabels.STATUS_COMPLETE)
        
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
        self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIPTION_COPIED, 2000)
    
    def copy_llm_to_clipboard(self):
        """Copy LLM analysis text to clipboard."""
        text = self.llm_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage(AppLabels.STATUS_LLM_COPIED, 2000)
    
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
        self.status_bar.showMessage(AppLabels.STATUS_ALL_COPIED, 2000)
    
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
            result = self.hotkey_manager.register_hotkey(self.hotkey, self.toggle_recording)
            
            if result:
                print(f"Hotkey '{self.hotkey}' has been set successfully")
                return True
            else:
                raise ValueError(f"Failed to register hotkey: {self.hotkey}")
        except Exception as e:
            error_msg = f"Hotkey setup error: {e}"
            print(error_msg)
            # Show error message to user
            self.status_bar.showMessage(AppLabels.HOTKEY_VALIDATION_ERROR_TITLE + ": " + str(e), 5000)
            # Continue with application even if hotkey fails
            return False
    
    def show_hotkey_dialog(self):
        """
        Show the global hotkey settings dialog.
        
        This method displays a dialog for changing the hotkey setting.
        The current hotkey is temporarily released during dialog display.
        """
        # Temporarily stop the listener
        self.hotkey_manager.stop_listener()
        
        dialog = HotkeyDialog(self, self.hotkey)
        if dialog.exec():
            new_hotkey = dialog.get_hotkey()
            if new_hotkey:
                self.hotkey = new_hotkey
                self.settings.setValue("hotkey", self.hotkey)
                self.setup_global_hotkey()
                self.status_bar.showMessage(AppLabels.STATUS_HOTKEY_SET.format(self.hotkey), 3000)
        else:
            # Restore original hotkey if dialog was canceled
            self.setup_global_hotkey()
            
    def show_instruction_sets_dialog(self):
        """
        Show the instruction sets management dialog.
        
        This method displays a dialog for managing instruction sets,
        including vocabulary, system instructions, and LLM settings.
        It requires an API key to be set.
        """
        if not self.unified_processor:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.MAIN_WIN_API_KEY_ERROR_TITLE,
                AppLabels.MAIN_WIN_API_KEY_ERROR_REQUIRED,
                SimpleMessageDialog.WARNING
            )
            return
            
        dialog = InstructionSetsDialog(self, self.instruction_set_manager)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get updated manager
            updated_manager = dialog.get_manager()
            self.instruction_set_manager = updated_manager
            
            # Apply settings from active instruction set
            self.apply_instruction_set_settings()
            
            # Update UI to reflect LLM enabled state
            self.llm_enabled_checkbox.setChecked(self.unified_processor.is_llm_enabled())
            
            # Show status message
            if self.instruction_set_manager.active_set:
                self.status_bar.showMessage(
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
            self.status_bar.showMessage(AppLabels.STATUS_AUTO_COPY_ENABLED, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_AUTO_COPY_DISABLED, 2000)
    
    def toggle_sound_option(self):
        """
        Toggle notification sounds on/off.
        
        Saves the setting and shows status in the status bar.
        """
        self.enable_sound = self.sound_action.isChecked()
        self.settings.setValue("enable_sound", self.enable_sound)
        if self.enable_sound:
            self.status_bar.showMessage(AppLabels.STATUS_SOUND_ENABLED, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_SOUND_DISABLED, 2000)

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
            self.status_bar.showMessage(AppLabels.STATUS_INDICATOR_SHOWN, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_INDICATOR_HIDDEN, 2000)
    
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

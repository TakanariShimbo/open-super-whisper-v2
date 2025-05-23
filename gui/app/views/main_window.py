"""
Main Window View

This module provides the main application window for the Open Super Whisper application,
implementing the view component of the MVC architecture.
"""

import sys

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QGridLayout,
    QFormLayout,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QSystemTrayIcon,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QAction, QCloseEvent

from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

from ..controllers.main_controller import MainController
from ..managers.icon_manager import IconManager
from ..utils.clipboard_utils import ClipboardUtils
from ..managers.audio_manager import AudioManager
from ..managers.settings_manager import SettingsManager
from .tray.system_tray import SystemTray
from .widgets.markdown_text_browser import MarkdownTextBrowser


class MainWindow(QMainWindow):
    """
    Main application window.

    This class represents the main user interface for the Open Super Whisper application.
    It presents the recording controls, STT output, and application settings.
    """

    def __init__(self) -> None:
        """
        Initialize the MainWindow.
        """
        super().__init__()

        # Initialize managers
        self._icon_manager = IconManager.instance()
        self._audio_manager = AudioManager.instance()

        # Create controller
        self._controller = MainController(main_window=self)

        # Set application icon
        self.setWindowIcon(self._icon_manager.get_app_icon())

        # Flag to track if the application is actually closing
        self._is_closing = False

        # Set up UI
        self._setup_ui()

        # Set up system tray
        self._setup_system_tray()

        # Connect signals from controller
        self._connect_controller_signals()

        # Register instruction set hotkeys
        self._register_hotkeys()

    def _setup_ui(self) -> None:
        """
        Set up the user interface.
        """
        # Set window properties
        self.setWindowTitle("Open Super Whisper App")
        self.setMinimumSize(700, 500)

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create toolbar
        self._create_toolbar()

        # Create control panel
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)

        # Create output tabs
        output_tabs = self._create_output_tabs()
        main_layout.addWidget(output_tabs, 1)

        # Create status bar
        self._create_status_bar()

        # Set central widget
        self.setCentralWidget(central_widget)

        # Populate instruction sets combo
        self._populate_instruction_set_combo()

    def _create_toolbar(self) -> None:
        """
        Create the application toolbar.
        """
        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)

        # API key action
        api_action = QAction("API Key", self)
        api_action.triggered.connect(self._on_click_api_key)
        self.toolbar.addAction(api_action)
        self.toolbar.addSeparator()

        # Instruction sets action
        instruction_sets_action = QAction("Instruction Sets", self)
        instruction_sets_action.triggered.connect(self._on_click_instruction_sets)
        self.toolbar.addAction(instruction_sets_action)
        self.toolbar.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._on_click_settings)
        self.toolbar.addAction(settings_action)
        self.toolbar.addSeparator()

        # Add a spacer widget to push the exit button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        # Exit action (right-aligned)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._on_click_exit)
        self.toolbar.addAction(exit_action)

    def _create_control_panel(self) -> QWidget:
        """
        Create the control panel with record button and instruction set selection.

        Returns
        -------
        QWidget
            The control panel widget
        """
        control_panel = QWidget()
        control_layout = QGridLayout(control_panel)

        # Record button
        self._record_button = QPushButton("Start Recording")
        self._record_button.setMinimumHeight(50)
        self._record_button.clicked.connect(self._on_click_record)

        # Instruction set selection
        instruction_set_form = self._create_instruction_set_form()

        # Add to layout
        control_layout.addWidget(self._record_button, 0, 0, 2, 1)
        control_layout.addWidget(instruction_set_form, 0, 1, 2, 5)
        control_layout.setColumnStretch(0, 1)
        control_layout.setColumnStretch(1, 3)

        return control_panel

    def _create_instruction_set_form(self) -> QWidget:
        """
        Create the instruction set selection form.

        Returns
        -------
        QWidget
            The instruction set form widget
        """
        instruction_set_form = QWidget()
        form_layout = QFormLayout(instruction_set_form)

        instruction_set_label = QLabel("Instruction Set:")
        self._instruction_set_combo = QComboBox()
        self._instruction_set_combo.setMinimumWidth(200)
        form_layout.addRow(instruction_set_label, self._instruction_set_combo)

        return instruction_set_form

    def _create_output_tabs(self) -> QWidget:
        """
        Create the tab widget for STT and LLM outputs.

        Returns
        -------
        QTabWidget
            The tab widget containing output tabs
        """
        self._tab_widget = QTabWidget()

        # Create STT output tab
        stt_tab = self._create_stt_output_tab()
        self._tab_widget.addTab(stt_tab, "STT Output")

        # Create LLM output tab
        llm_tab = self._create_llm_output_tab()
        self._tab_widget.addTab(llm_tab, "LLM Output")

        return self._tab_widget

    def _create_stt_output_tab(self) -> QWidget:
        """
        Create the STT output tab.

        Returns
        -------
        QWidget
            The STT output tab widget
        """
        stt_tab = QWidget()
        stt_layout = QVBoxLayout(stt_tab)

        # Create header with label and copy button
        stt_header_layout = self._create_output_header(
            label_text="STT Output:",
            copy_button_slot=self._on_click_copy_stt,
        )
        stt_layout.addLayout(stt_header_layout)

        # Use MarkdownTextBrowser for STT output
        self._stt_text = MarkdownTextBrowser(main_window=self)
        self._stt_text.setPlaceholderText("STT output will appear here...")
        stt_layout.addWidget(self._stt_text)

        return stt_tab

    def _create_llm_output_tab(self) -> QWidget:
        """
        Create the LLM output tab.

        Returns
        -------
        QWidget
            The LLM output tab widget
        """
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)

        # Create header with label and copy button
        llm_header_layout = self._create_output_header(
            label_text="LLM Output:",
            copy_button_slot=self._on_click_copy_llm,
        )
        llm_layout.addLayout(llm_header_layout)

        # Use MarkdownTextBrowser for LLM output
        self._llm_text = MarkdownTextBrowser(main_window=self)
        self._llm_text.setPlaceholderText("LLM output will appear here...")
        llm_layout.addWidget(self._llm_text)

        return llm_tab

    def _create_output_header(self, label_text: str, copy_button_slot) -> QGridLayout:
        """
        Create a header layout with label and copy button for output tabs.

        Parameters
        ----------
        label_text : str
            Text for the header label
        copy_button_slot : callable
            Slot to connect to the copy button

        Returns
        -------
        QGridLayout
            The header layout with label and copy button
        """
        header_layout = QGridLayout()

        # Create label
        label = QLabel(label_text)
        header_layout.addWidget(label, 0, 0)

        # Create copy button
        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(copy_button_slot)
        header_layout.addWidget(copy_button, 0, 1, Qt.AlignmentFlag.AlignRight)

        # Store copy button reference for later use
        if "STT" in label_text:
            self._stt_copy_button = copy_button
        else:
            self._llm_copy_button = copy_button

        return header_layout

    def _create_status_bar(self) -> None:
        """
        Create the status bar with status indicator.
        """
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        # Status indicator
        self._status_indicator = QLabel("Ready")
        self._status_bar.addPermanentWidget(self._status_indicator)

    def _setup_system_tray(self) -> None:
        """
        Set up the system tray icon.
        """
        # Create system tray with the icon
        self._system_tray = SystemTray(main_window=self)

        # Connect system tray signals
        self._system_tray.show_window_signal.connect(self._on_click_show_window)
        self._system_tray.hide_window_signal.connect(self._on_click_hide_window)
        self._system_tray.quit_application_signal.connect(self._on_click_exit)
        self._system_tray.toggle_recording_signal.connect(self._on_click_record)

        # Show system tray icon
        self._system_tray.show()

    def _create_toolbar(self) -> None:
        """
        Create the application toolbar.
        """
        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)

        # Toolbar actions start with instruction sets
        # API key action
        api_action = QAction("API Key", self)
        api_action.triggered.connect(self._on_click_api_key)
        self.toolbar.addAction(api_action)
        self.toolbar.addSeparator()

        # Instruction sets action
        instruction_sets_action = QAction("Instruction Sets", self)
        instruction_sets_action.triggered.connect(self._on_click_instruction_sets)
        self.toolbar.addAction(instruction_sets_action)
        self.toolbar.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._on_click_settings)
        self.toolbar.addAction(settings_action)
        self.toolbar.addSeparator()

        # Add a spacer widget to push the exit button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        # Exit action (right-aligned)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._on_click_exit)
        self.toolbar.addAction(exit_action)

    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller to the view slots.
        """
        # Recording signals
        self._controller.recording_started.connect(self._handle_recording_started)

        # Processing signals
        self._controller.processing_started.connect(self._handle_processing_started)
        self._controller.processing_complete.connect(self._handle_processing_complete)
        self._controller.processing_cancelled.connect(self._handle_processing_cancelled)

        # Status update signal
        self._controller.status_update.connect(self._handle_update_status)

        # Instruction set activation signal
        self._controller.instruction_set_activated.connect(self._handle_instruction_set_activated)

        # Hotkey triggered signal
        self._controller.hotkey_triggered.connect(self._handle_hotkey_triggered)

        # LLM streaming signal
        self._controller.llm_stream_update.connect(self._handle_llm_stream_update)

    def _populate_instruction_set_combo(self) -> None:
        """
        Populate the instruction set combo box with available instruction sets.
        """
        self._instruction_set_combo.blockSignals(True)
        self._instruction_set_combo.clear()

        # Add all instruction sets
        for instruction_set in self._controller.get_instruction_sets():
            self._instruction_set_combo.addItem(instruction_set.name)

            # Add tooltip with hotkey if available
            if instruction_set.hotkey:
                self._instruction_set_combo.setItemData(
                    self._instruction_set_combo.count() - 1,
                    f"Hotkey: {instruction_set.hotkey}",
                    Qt.ItemDataRole.ToolTipRole,
                )

        # Select the currently selected instruction set
        selected_set = self._controller.get_selected_instruction_set()
        if selected_set:
            index = self._instruction_set_combo.findText(selected_set.name)
            if index >= 0:
                self._instruction_set_combo.setCurrentIndex(index)

        self._instruction_set_combo.blockSignals(False)

    def _register_hotkeys(self) -> None:
        """
        Register hotkeys for all instruction sets.
        """
        for instruction_set in self._controller.get_instruction_sets():
            if instruction_set.hotkey:
                self._controller.register_hotkey(hotkey=instruction_set.hotkey)

    @pyqtSlot()
    def _handle_recording_started(self) -> None:
        """
        Handle the recording started event.
        """
        # Update button and indicator text
        self._record_button.setText("Stop Recording")
        self._status_indicator.setText("Recording...")

        # Update system tray recording status
        self._system_tray.update_recording_status("stop_recording")

        # Disable instruction set selection during processing
        self._instruction_set_combo.setEnabled(False)

        # Play recording start sound
        self._audio_manager.play_start_recording()

    @pyqtSlot()
    def _handle_processing_started(self) -> None:
        """
        Handle the processing started event.
        """
        # Update button and indicator text
        self._record_button.setText("Cancel Processing")
        self._status_indicator.setText("Processing...")

        # Update system tray recording status
        self._system_tray.update_recording_status("cancel_processing")

        # Clear the LLM text to prepare for streaming updates
        self._stt_text.clear()
        self._llm_text.clear()

        # Play recording stop sound
        self._audio_manager.play_stop_recording()

    @pyqtSlot()
    def _handle_processing_cancelled(self) -> None:
        """
        Handle processing cancelled event.
        """
        # Update button and indicator text
        self._record_button.setText("Start Recording")
        self._status_indicator.setText("Cancelled")

        # Re-enable instruction set selection
        self._instruction_set_combo.setEnabled(True)

        # Update system tray recording status
        self._system_tray.update_recording_status("start_recording")

        # Play cancel processing sound
        self._audio_manager.play_cancel_processing()

    @pyqtSlot(PipelineResult)
    def _handle_processing_complete(self, result: PipelineResult) -> None:
        """
        Handle the processing complete event.

        Parameters
        ----------
        result : PipelineResult
            The result of the processing
        """
        # Update the STT output text
        self._stt_text.set_markdown_text(markdown_text=result.stt_output)

        if result.is_llm_processed and result.llm_output:
            # Set the LLM output text
            self._llm_text.set_markdown_text(markdown_text=result.llm_output)

            # Stay on or switch to LLM tab
            self._tab_widget.setCurrentIndex(1)
        else:
            # No LLM processing, switch to STT output tab
            self._tab_widget.setCurrentIndex(0)

        # Reset button state and status indicator
        self._record_button.setText("Start Recording")
        self._status_indicator.setText("Ready")

        # Re-enable instruction set selection
        self._instruction_set_combo.setEnabled(True)

        # Update system tray recording status
        self._system_tray.update_recording_status("start_recording")

        # Update status bar to show completion
        self._status_bar.showMessage("Processing complete", 3000)

        # Play completion sound
        self._audio_manager.play_complete_processing()

    @pyqtSlot(str, int)
    def _handle_update_status(self, message: str, timeout: int = 0) -> None:
        """
        Update the status bar message.

        Parameters
        ----------
        message : str
            The message to display
        timeout : int, optional
            Timeout in milliseconds, 0 means no timeout, by default 0
        """
        self._status_bar.showMessage(message, timeout)

    @pyqtSlot(str)
    def _handle_instruction_set_activated(self, set_name: str) -> None:
        """
        Handle instruction set activation.

        Parameters
        ----------
        set_name : str
            The name of the activated instruction set
        """
        # Update the combo box
        self._instruction_set_combo.blockSignals(True)
        index = self._instruction_set_combo.findText(set_name)
        if index >= 0:
            self._instruction_set_combo.setCurrentIndex(index)
        self._instruction_set_combo.blockSignals(False)

    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle hotkey trigger event.

        Parameters
        ----------
        hotkey : str
            The hotkey that was triggered
        """
        # The controller will handle the actual logic, this is for UI feedback
        self._status_bar.showMessage(f"Hotkey triggered: {hotkey}", 2000)

    @pyqtSlot(str)
    def _handle_llm_stream_update(self, chunk: str) -> None:
        """
        Handle streaming updates from the LLM processor.

        Parameters
        ----------
        chunk : str
            The text chunk from the LLM stream
        """
        # Switch to the LLM tab if not already active
        if self._tab_widget.currentIndex() != 1:
            self._tab_widget.setCurrentIndex(1)

        # Append the new chunk to the LLM text
        self._llm_text.append_markdown(text=chunk)

    @pyqtSlot()
    def _on_click_api_key(self) -> None:
        """
        Show dialog for API key entry.
        """
        # Use the controller's API key settings method
        if self._controller.show_api_key_dialog(main_window=self):
            self._status_bar.showMessage("API key updated", 2000)
        else:
            self._status_bar.showMessage("Failed to update API key", 2000)

    @pyqtSlot()
    def _on_click_instruction_sets(self) -> None:
        """
        Show the instruction sets management dialog.
        """
        # Use controller to handle instruction dialog
        if self._controller.show_instruction_dialog(main_window=self):
            # Dialog was accepted, refresh instruction sets combo
            self._populate_instruction_set_combo()
            self._status_bar.showMessage("Instruction sets updated", 2000)

    @pyqtSlot()
    def _on_click_settings(self) -> None:
        """
        Show the settings dialog.
        """
        # Use controller to handle settings dialog
        if self._controller.show_settings_dialog(main_window=self):
            # Settings were updated
            self._status_bar.showMessage("Settings updated", 2000)

    @pyqtSlot()
    def _on_click_record(self) -> None:
        """
        Handle the record button click event.
        """
        # If processing is active, cancel it
        if self._controller.is_processing:
            self._controller.cancel_processing()
            return

        # If recording is active, stop it
        if self._controller.is_recording:
            self._controller.stop_recording()
            return

        # Otherwise start recording
        index = self._instruction_set_combo.currentIndex()
        if index < 0:
            return
        name = self._instruction_set_combo.itemText(index)
        instruction_set = self._controller.get_instruction_set_by_name(name=name)
        if instruction_set is None:
            return
        self._controller.start_recording(set_name=name, hotkey=instruction_set.hotkey)

    @pyqtSlot()
    def _on_click_copy_stt(self) -> None:
        """
        Copy the STT output text to the clipboard.
        """
        ClipboardUtils.set_text(text=self._stt_text.markdown_text())
        self._status_bar.showMessage("STT output copied to clipboard", 2000)

    @pyqtSlot()
    def _on_click_copy_llm(self) -> None:
        """
        Copy the LLM output text to the clipboard.
        """
        ClipboardUtils.set_text(text=self._llm_text.markdown_text())
        self._status_bar.showMessage("LLM output copied to clipboard", 2000)

    @pyqtSlot()
    def _on_click_show_window(self) -> None:
        """
        Show and activate the application window.
        """
        self.showNormal()
        self.activateWindow()

    @pyqtSlot()
    def _on_click_hide_window(self) -> None:
        """
        Hide the application window.
        """
        self.hide()

    @pyqtSlot()
    def _on_click_exit(self) -> None:
        """
        Completely exit the application.
        """
        reply = QMessageBox.question(
            self,
            "Quit Application",
            "Are you sure you want to quit the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Set closing flag
            self._is_closing = True

            # Hide the system tray icon
            if hasattr(self, "system_tray"):
                self._system_tray.hide()

            # Shut down the controller cleanly
            self._controller.shutdown()

            # Exit application
            sys.exit(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Parameters
        ----------
        event : QCloseEvent
            The close event
        """
        # If not actually closing (just minimizing to tray)
        if not self._is_closing:
            event.ignore()
            self._on_click_hide_window()

            # Show a notification message
            self._system_tray.showMessage(
                "Open Super Whisper App",
                "The application is still running in the background. Click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )
        else:
            # Actually closing
            event.accept()

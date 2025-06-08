"""
Main Window View

This module provides the main application window for the Open Super Whisper application,
implementing the view component of the MVC architecture.
"""

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
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QAction, QCloseEvent

from core.pipelines.pipeline_result import PipelineResult

from ..utils.clipboard_utils import ClipboardUtils
from ..managers.icon_manager import IconManager
from ..managers.settings_manager import SettingsManager
from ..managers.audio_manager import AudioManager
from ..controllers.main_controller import MainController
from .tray.system_tray import SystemTray
from .widgets.markdown_text_browser import MarkdownTextBrowser


class LabelManager:
    """
    Manages application labels for internationalization support in Main Window.
    """

    ALL_LABELS = {
        "English": {
            # Window/UI Labels
            "window_title": "Open Super Whisper",
            "main_toolbar": "Main Toolbar",
            "instruction_set_label": "Instruction Set:",
            "stt_output_tab": "STT Output",
            "llm_output_tab": "LLM Output",
            "stt_output_header": "STT Output:",
            "llm_output_header": "LLM Output:",
            "copy_button": "Copy",
            "hotkey_tooltip": "Hotkey: {hotkey}",
            # Button Labels
            "start_recording": "Start Recording",
            "stop_recording": "Stop Recording",
            "cancel_processing": "Cancel Processing",
            # Menu/Action Labels
            "api_key_action": "API Key",
            "instruction_sets_action": "Instruction Sets",
            "settings_action": "Settings",
            "quit_application_action": "Quit Application",
            # Status Messages
            "status_ready": "Ready",
            "status_recording": "Recording...",
            "status_processing": "Processing...",
            "status_cancelled": "Cancelled",
            "status_processing_completed": "Processing completed",
            # Placeholder Text
            "stt_placeholder": "STT output will appear here...",
            "llm_placeholder": "LLM output will appear here...",
            # Status Bar Messages
            "api_key_updated": "API key updated",
            "api_key_update_failed": "Failed to update API key",
            "instruction_sets_updated": "Instruction sets updated",
            "settings_updated": "Settings updated",
            "stt_copied": "STT output copied to clipboard",
            "llm_copied": "LLM output copied to clipboard",
            # Dialog Messages
            "quit_dialog_title": "Quit Application",
            "quit_dialog_message": "Are you sure you want to quit the application?",
            "settings_restart_dialog_title": "Settings Updated",
            "settings_restart_dialog_message": "Settings have been updated successfully.\n\nThe application will shut down in {seconds} seconds to apply the new settings.",
            "tray_message_title": "Open Super Whisper",
            "tray_message_text": "The application is still running in the background. Click the tray icon to restore.",
        },
        "Japanese": {
            # Window/UI Labels
            "window_title": "Open Super Whisper",
            "main_toolbar": "メインツールバー",
            "instruction_set_label": "インストラクションセット:",
            "stt_output_tab": "STT出力",
            "llm_output_tab": "LLM出力",
            "stt_output_header": "STT出力:",
            "llm_output_header": "LLM出力:",
            "copy_button": "コピー",
            "hotkey_tooltip": "ホットキー: {hotkey}",
            # Button Labels
            "start_recording": "録音開始",
            "stop_recording": "録音停止",
            "cancel_processing": "処理キャンセル",
            # Menu/Action Labels
            "api_key_action": "APIキー",
            "instruction_sets_action": "インストラクションセット",
            "settings_action": "設定",
            "quit_application_action": "アプリ終了",
            # Status Messages
            "status_ready": "待機中",
            "status_recording": "録音中...",
            "status_processing": "処理中...",
            "status_cancelled": "キャンセルされました",
            "status_processing_completed": "処理が完了しました",
            # Placeholder Text
            "stt_placeholder": "ここにSTT出力が表示されます...",
            "llm_placeholder": "ここにLLM出力が表示されます...",
            # Status Bar Messages
            "api_key_updated": "APIキーを更新しました",
            "api_key_update_failed": "APIキーの更新に失敗しました",
            "instruction_sets_updated": "インストラクションセットを更新しました",
            "settings_updated": "設定を更新しました",
            "stt_copied": "STT出力をクリップボードにコピーしました",
            "llm_copied": "LLM出力をクリップボードにコピーしました",
            # Dialog Messages
            "quit_dialog_title": "アプリ終了",
            "quit_dialog_message": "アプリケーションを終了してもよろしいですか？",
            "settings_restart_dialog_title": "設定が更新されました",
            "settings_restart_dialog_message": "設定が正常に更新されました。\n\n新しい設定を適用するため、{seconds}秒後にアプリケーションを終了します。",
            "tray_message_title": "Open Super Whisper",
            "tray_message_text": "アプリケーションはバックグラウンドで動作中です。トレイアイコンをクリックして復元できます。",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # Load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # Set labels based on language
        self._labels = self.ALL_LABELS[language]

    # Window/UI Labels
    @property
    def window_title(self) -> str:
        return self._labels["window_title"]

    @property
    def main_toolbar(self) -> str:
        return self._labels["main_toolbar"]

    @property
    def instruction_set_label(self) -> str:
        return self._labels["instruction_set_label"]

    @property
    def stt_output_tab(self) -> str:
        return self._labels["stt_output_tab"]

    @property
    def llm_output_tab(self) -> str:
        return self._labels["llm_output_tab"]

    @property
    def stt_output_header(self) -> str:
        return self._labels["stt_output_header"]

    @property
    def llm_output_header(self) -> str:
        return self._labels["llm_output_header"]

    @property
    def copy_button(self) -> str:
        return self._labels["copy_button"]

    @property
    def hotkey_tooltip(self) -> str:
        return self._labels["hotkey_tooltip"]

    # Button Labels
    @property
    def start_recording(self) -> str:
        return self._labels["start_recording"]

    @property
    def stop_recording(self) -> str:
        return self._labels["stop_recording"]

    @property
    def cancel_processing(self) -> str:
        return self._labels["cancel_processing"]

    # Menu/Action Labels
    @property
    def api_key_action(self) -> str:
        return self._labels["api_key_action"]

    @property
    def instruction_sets_action(self) -> str:
        return self._labels["instruction_sets_action"]

    @property
    def settings_action(self) -> str:
        return self._labels["settings_action"]

    @property
    def quit_application_action(self) -> str:
        return self._labels["quit_application_action"]

    # Status Messages
    @property
    def status_ready(self) -> str:
        return self._labels["status_ready"]

    @property
    def status_recording(self) -> str:
        return self._labels["status_recording"]

    @property
    def status_processing(self) -> str:
        return self._labels["status_processing"]

    @property
    def status_cancelled(self) -> str:
        return self._labels["status_cancelled"]

    @property
    def status_processing_completed(self) -> str:
        return self._labels["status_processing_completed"]

    # Placeholder Text
    @property
    def stt_placeholder(self) -> str:
        return self._labels["stt_placeholder"]

    @property
    def llm_placeholder(self) -> str:
        return self._labels["llm_placeholder"]

    # Status Bar Messages
    @property
    def api_key_updated(self) -> str:
        return self._labels["api_key_updated"]

    @property
    def api_key_update_failed(self) -> str:
        return self._labels["api_key_update_failed"]

    @property
    def instruction_sets_updated(self) -> str:
        return self._labels["instruction_sets_updated"]

    @property
    def settings_updated(self) -> str:
        return self._labels["settings_updated"]

    @property
    def stt_copied(self) -> str:
        return self._labels["stt_copied"]

    @property
    def llm_copied(self) -> str:
        return self._labels["llm_copied"]

    # Dialog Messages
    @property
    def quit_dialog_title(self) -> str:
        return self._labels["quit_dialog_title"]

    @property
    def quit_dialog_message(self) -> str:
        return self._labels["quit_dialog_message"]

    @property
    def settings_restart_dialog_title(self) -> str:
        return self._labels["settings_restart_dialog_title"]

    @property
    def settings_restart_dialog_message(self) -> str:
        return self._labels["settings_restart_dialog_message"]

    @property
    def tray_message_title(self) -> str:
        return self._labels["tray_message_title"]

    @property
    def tray_message_text(self) -> str:
        return self._labels["tray_message_text"]


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

        # Initialize label manager
        self._label_manager = LabelManager()

        # Initialize managers
        self._icon_manager = IconManager.instance()
        self._audio_manager = AudioManager.instance()

        # Create controller
        self._controller = MainController(main_window=self)

        # Flag to track if the application is actually closing
        self._is_closing = False

        # Flag to restart the application
        self._is_restart_required = False

        # Set up UI
        self._setup_ui()

        # Set up system tray
        self._setup_system_tray()

        # Register instruction set hotkeys
        self._register_hotkeys()

        # Connect signals from controller
        self._connect_controller_signals()

    #
    # UI Setup
    #
    def _setup_ui(self) -> None:
        """
        Set up the user interface.
        """
        # Set window properties
        self.setWindowTitle(self._label_manager.window_title)
        self.setMinimumSize(700, 500)

        # Set window icon
        icon = self._icon_manager.get_app_icon()
        self.setWindowIcon(icon)

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
        self.toolbar = self.addToolBar(self._label_manager.main_toolbar)
        self.toolbar.setMovable(False)

        # API key action
        api_action = QAction(self._label_manager.api_key_action, self)
        api_action.triggered.connect(self._on_click_api_key)
        self.toolbar.addAction(api_action)
        self.toolbar.addSeparator()

        # Instruction sets action
        instruction_sets_action = QAction(self._label_manager.instruction_sets_action, self)
        instruction_sets_action.triggered.connect(self._on_click_instruction_sets)
        self.toolbar.addAction(instruction_sets_action)
        self.toolbar.addSeparator()

        # Settings action
        settings_action = QAction(self._label_manager.settings_action, self)
        settings_action.triggered.connect(self._on_click_settings)
        self.toolbar.addAction(settings_action)
        self.toolbar.addSeparator()

        # Add a spacer widget to push the exit button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        # Exit action (right-aligned)
        quit_action = QAction(self._label_manager.quit_application_action, self)
        quit_action.triggered.connect(self._on_click_quit_application)
        self.toolbar.addAction(quit_action)

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
        self._record_button = QPushButton(self._label_manager.start_recording)
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

        instruction_set_label = QLabel(self._label_manager.instruction_set_label)
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
        self._tab_widget.addTab(stt_tab, self._label_manager.stt_output_tab)

        # Create LLM output tab
        llm_tab = self._create_llm_output_tab()
        self._tab_widget.addTab(llm_tab, self._label_manager.llm_output_tab)

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
            label_text=self._label_manager.stt_output_header,
            copy_button_slot=self._on_click_copy_stt,
        )
        stt_layout.addLayout(stt_header_layout)

        # Use MarkdownTextBrowser for STT output
        self._stt_text = MarkdownTextBrowser(main_window=self)
        self._stt_text.setPlaceholderText(self._label_manager.stt_placeholder)
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
            label_text=self._label_manager.llm_output_header,
            copy_button_slot=self._on_click_copy_llm,
        )
        llm_layout.addLayout(llm_header_layout)

        # Use MarkdownTextBrowser for LLM output
        self._llm_text = MarkdownTextBrowser(main_window=self)
        self._llm_text.setPlaceholderText(self._label_manager.llm_placeholder)
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
        copy_button = QPushButton(self._label_manager.copy_button)
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
        self._status_indicator = QLabel(self._label_manager.status_ready)
        self._status_bar.addPermanentWidget(self._status_indicator)

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
                    self._label_manager.hotkey_tooltip.format(hotkey=instruction_set.hotkey),
                    Qt.ItemDataRole.ToolTipRole,
                )

        # Select the currently selected instruction set
        selected_set = self._controller.get_selected_instruction_set()
        if selected_set:
            index = self._instruction_set_combo.findText(selected_set.name)
            if index >= 0:
                self._instruction_set_combo.setCurrentIndex(index)

        self._instruction_set_combo.blockSignals(False)

    #
    # Tray Setup
    #
    def _setup_system_tray(self) -> None:
        """
        Set up the system tray icon.
        """
        # Create system tray with the icon
        self._system_tray = SystemTray(main_window=self)

        # Connect system tray signals
        self._system_tray.show_window_signal.connect(self._on_click_show_window)
        self._system_tray.hide_window_signal.connect(self._on_click_hide_window)
        self._system_tray.quit_application_signal.connect(self._on_click_quit_application)
        self._system_tray.toggle_recording_signal.connect(self._on_click_record)

        # Show system tray icon
        self._system_tray.show()

    #
    # Hotkeys
    #
    def _register_hotkeys(self) -> None:
        """
        Register hotkeys for all instruction sets.
        """
        for instruction_set in self._controller.get_instruction_sets():
            if instruction_set.hotkey:
                self._controller.register_hotkey(hotkey=instruction_set.hotkey)

    #
    # Controller Signals
    #
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller to the view slots.
        """
        self._controller.recording_started.connect(self._handle_recording_started)
        self._controller.processing_started.connect(self._handle_processing_started)
        self._controller.processing_completed.connect(self._handle_processing_completed)
        self._controller.processing_cancelled.connect(self._handle_processing_cancelled)
        self._controller.streaming_llm_chunk.connect(self._handle_streaming_llm_chunk)

        self._controller.instruction_set_activated.connect(self._handle_instruction_set_activated)

        self._controller.showing_message.connect(self._handle_showing_message)

    #
    # Controller Events
    #
    @pyqtSlot()
    def _handle_recording_started(self) -> None:
        """
        Handle the recording started event.
        """
        # Update button and indicator text
        self._record_button.setText(self._label_manager.stop_recording)
        self._status_indicator.setText(self._label_manager.status_recording)

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
        self._record_button.setText(self._label_manager.cancel_processing)
        self._status_indicator.setText(self._label_manager.status_processing)

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
        self._record_button.setText(self._label_manager.start_recording)
        self._status_indicator.setText(self._label_manager.status_cancelled)

        # Re-enable instruction set selection
        self._instruction_set_combo.setEnabled(True)

        # Update system tray recording status
        self._system_tray.update_recording_status("start_recording")

        # Play cancel processing sound
        self._audio_manager.play_cancel_processing()

    @pyqtSlot(PipelineResult)
    def _handle_processing_completed(self, result: PipelineResult) -> None:
        """
        Handle the processing completed event.

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
        self._record_button.setText(self._label_manager.start_recording)
        self._status_indicator.setText(self._label_manager.status_ready)

        # Re-enable instruction set selection
        self._instruction_set_combo.setEnabled(True)

        # Update system tray recording status
        self._system_tray.update_recording_status("start_recording")

        # Update status bar to show completion
        self._status_bar.showMessage(self._label_manager.status_processing_completed, 2000)

        # Play completion sound
        self._audio_manager.play_complete_processing()

    @pyqtSlot(str)
    def _handle_streaming_llm_chunk(self, chunk: str) -> None:
        """
        Handle streaming LLM chunks.

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

    @pyqtSlot(str)
    def _handle_instruction_set_activated(self, set_name: str) -> None:
        """
        Handle instruction set activation.

        Parameters
        ----------
        set_name : str
            The name of the activated instruction set
        """
        self._instruction_set_combo.blockSignals(True)

        # Update the combo box
        index = self._instruction_set_combo.findText(set_name)
        if index >= 0:
            self._instruction_set_combo.setCurrentIndex(index)

        self._instruction_set_combo.blockSignals(False)

    @pyqtSlot(str, int)
    def _handle_showing_message(self, message: str, timeout: int = 0) -> None:
        """
        Show a message in the status bar.

        Parameters
        ----------
        message : str
            The message to display
        timeout : int, optional
            Timeout in milliseconds, 0 means no timeout, by default 0
        """
        self._status_bar.showMessage(message, timeout)

    #
    # UI Events
    #

    def _update_settings_dialog_message(self) -> None:
        """
        Update the settings dialog message with current countdown.
        """
        message = self._label_manager.settings_restart_dialog_message.format(seconds=self._countdown_seconds)
        self._settings_dialog.setText(message)

    @pyqtSlot()
    def _on_settings_timer_timeout(self) -> None:
        """
        Handle settings dialog timer timeout.
        """
        self._countdown_seconds -= 1

        if self._countdown_seconds > 0:
            # Update message with new countdown
            self._update_settings_dialog_message()
        else:
            # Timer reached zero, close dialog and exit
            self._settings_timer.stop()
            self._settings_dialog.accept()  # Close dialog automatically

    def _show_settings_restart_dialog(self) -> None:
        """
        Show settings restart dialog with countdown timer.
        """
        # Create message box
        self._settings_dialog = QMessageBox(self)
        self._settings_dialog.setWindowTitle(self._label_manager.settings_restart_dialog_title)
        self._settings_dialog.setIcon(QMessageBox.Icon.Information)
        self._settings_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Initialize countdown variables
        self._countdown_seconds = 5

        # Set initial message with countdown
        self._update_settings_dialog_message()

        # Create and start timer
        self._settings_timer = QTimer(self)
        self._settings_timer.timeout.connect(self._on_settings_timer_timeout)
        self._settings_timer.start(1000)  # Update every second

        # Show dialog (non-blocking)
        self._settings_dialog.exec()

    @pyqtSlot()
    def _on_click_api_key(self) -> None:
        """
        Show dialog for API key entry.
        """
        # Use the controller's API key settings method
        if self._controller.show_api_key_dialog(main_window=self):
            self._status_bar.showMessage(self._label_manager.api_key_updated, 2000)
        else:
            self._status_bar.showMessage(self._label_manager.api_key_update_failed, 2000)

    @pyqtSlot()
    def _on_click_instruction_sets(self) -> None:
        """
        Show the instruction sets management dialog.
        """
        # Use controller to handle instruction dialog
        if self._controller.show_instruction_dialog(main_window=self):
            # Dialog was accepted, refresh instruction sets combo
            self._populate_instruction_set_combo()
            self._status_bar.showMessage(self._label_manager.instruction_sets_updated, 2000)

    @pyqtSlot()
    def _on_click_settings(self) -> None:
        """
        Show the settings dialog.
        """
        # Use controller to handle settings dialog
        if self._controller.show_settings_dialog(main_window=self):
            # Settings were updated
            self._status_bar.showMessage(self._label_manager.settings_updated, 2000)

            # Show countdown dialog with auto-close timer
            self._show_settings_restart_dialog()

            # Exit application
            self._exit_application(restart=True)

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
        self._status_bar.showMessage(self._label_manager.stt_copied, 2000)

    @pyqtSlot()
    def _on_click_copy_llm(self) -> None:
        """
        Copy the LLM output text to the clipboard.
        """
        ClipboardUtils.set_text(text=self._llm_text.markdown_text())
        self._status_bar.showMessage(self._label_manager.llm_copied, 2000)

    #
    # Open/Close Events
    #
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
    def _on_click_quit_application(self) -> None:
        """
        Completely exit the application.
        """
        self.showNormal()
        self.activateWindow()

        reply = QMessageBox.question(
            self,
            self._label_manager.quit_dialog_title,
            self._label_manager.quit_dialog_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._exit_application()
        else:
            self.hide()

    def _exit_application(self, restart: bool = False) -> None:
        """
        Exit the application with proper cleanup.
        """
        # Set closing flag
        self._is_closing = True

        # Hide the system tray icon
        if hasattr(self, "_system_tray"):
            self._system_tray.hide()

        # Shut down the controller cleanly
        self._controller.shutdown()

        # Set restart flag
        self._is_restart_required = restart

        self.close()

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
                self._label_manager.tray_message_title,
                self._label_manager.tray_message_text,
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        else:
            # Actually closing
            event.accept()

    @property
    def is_restart_required(self) -> bool:
        """
        Get the restart required flag.
        """
        return self._is_restart_required

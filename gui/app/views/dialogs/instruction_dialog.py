"""
Instruction Dialog View

This module provides the view component for the instruction dialog in the Open Super Whisper application.
It provides the UI for managing instruction sets.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QDialogButtonBox,
    QListWidget,
    QSplitter,
    QLineEdit,
    QInputDialog,
    QTabWidget,
    QWidget,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent, QShowEvent

from core.pipelines.instruction_set import InstructionSet

from ...managers.settings_manager import SettingsManager
from ...controllers.dialogs.instruction_dialog_controller import InstructionDialogController


class LabelManager:
    """
    Manages application labels for internationalization support in Instruction Dialog.
    """

    ALL_LABELS = {
        "English": {
            # Window/Dialog titles
            "window_title": "Instruction Sets",
            "new_instruction_set_title": "New Instruction Set",
            "rename_instruction_set_title": "Rename Instruction Set",
            "confirm_deletion_title": "Confirm Deletion",
            "success_title": "Success",
            "error_title": "Error",
            "unsaved_changes_title": "Unsaved Changes",
            "changes_discarded_title": "Changes Discarded",
            # UI Labels
            "instruction_sets_label": "Instruction Sets",
            "custom_vocabulary_label": "Custom Vocabulary",
            "stt_instructions_label": "STT Instructions",
            "llm_instructions_label": "LLM Instructions",
            "stt_language_label": "STT Language",
            "stt_model_label": "STT Model",
            "hotkey_label": "Hotkey",
            "enable_llm_processing_label": "Enable LLM Processing",
            "llm_model_label": "LLM Model",
            "context_label": "Context",
            # Button Labels
            "add_button": "Add",
            "rename_button": "Rename",
            "delete_button": "Delete",
            "save_changes_button": "Save Changes",
            "discard_changes_button": "Discard Changes",
            "set_hotkey_button": "Set Hotkey",
            "close_button": "Close",
            # Tab Labels
            "vocabulary_tab": "Vocabulary",
            "stt_instructions_tab": "STT Instructions",
            "llm_instructions_tab": "LLM Instructions",
            "settings_tab": "Settings",
            # Checkbox Labels
            "include_clipboard_text": "Include Clipboard Text",
            "include_clipboard_image": "Include Clipboard Image",
            # Help/Description Text
            "vocabulary_help": "Add custom technical terms, acronyms, or specialized vocabulary to improve transcription accuracy.",
            "stt_instructions_help": "Provide system instructions to guide the transcription process (formatting, focus areas, etc.)",
            "llm_instructions_help": "Provide system instructions for the LLM to guide its processing of transcription results.",
            "settings_help": "Configure language, model, and other settings for this instruction set.",
            "clipboard_text_tooltip": "Include text from clipboard when processing with LLM",
            "clipboard_image_tooltip": "Include image from clipboard when processing with LLM (if supported by model)",
            # Placeholder Text
            "no_hotkey_placeholder": "No hotkey set",
            # Message Text
            "enter_instruction_set_name": "Enter a name for the new instruction set:",
            "enter_new_name": "Enter a new name for the instruction set:",
            "confirm_delete_message": "Are you sure you want to delete the instruction set '{name}'?",
            "unsaved_changes_message": "You have unsaved changes. Do you want to save them?",
            "changes_discarded_message": "Changes have been discarded.",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # Load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # Set labels based on language
        self._labels = self.ALL_LABELS[language]

    # Window/Dialog titles
    @property
    def window_title(self) -> str:
        return self._labels["window_title"]

    @property
    def new_instruction_set_title(self) -> str:
        return self._labels["new_instruction_set_title"]

    @property
    def rename_instruction_set_title(self) -> str:
        return self._labels["rename_instruction_set_title"]

    @property
    def confirm_deletion_title(self) -> str:
        return self._labels["confirm_deletion_title"]

    @property
    def success_title(self) -> str:
        return self._labels["success_title"]

    @property
    def error_title(self) -> str:
        return self._labels["error_title"]

    @property
    def unsaved_changes_title(self) -> str:
        return self._labels["unsaved_changes_title"]

    @property
    def changes_discarded_title(self) -> str:
        return self._labels["changes_discarded_title"]

    # UI Labels
    @property
    def instruction_sets_label(self) -> str:
        return self._labels["instruction_sets_label"]

    @property
    def custom_vocabulary_label(self) -> str:
        return self._labels["custom_vocabulary_label"]

    @property
    def stt_instructions_label(self) -> str:
        return self._labels["stt_instructions_label"]

    @property
    def llm_instructions_label(self) -> str:
        return self._labels["llm_instructions_label"]

    @property
    def stt_language_label(self) -> str:
        return self._labels["stt_language_label"]

    @property
    def stt_model_label(self) -> str:
        return self._labels["stt_model_label"]

    @property
    def hotkey_label(self) -> str:
        return self._labels["hotkey_label"]

    @property
    def enable_llm_processing_label(self) -> str:
        return self._labels["enable_llm_processing_label"]

    @property
    def llm_model_label(self) -> str:
        return self._labels["llm_model_label"]

    @property
    def context_label(self) -> str:
        return self._labels["context_label"]

    # Button Labels
    @property
    def add_button(self) -> str:
        return self._labels["add_button"]

    @property
    def rename_button(self) -> str:
        return self._labels["rename_button"]

    @property
    def delete_button(self) -> str:
        return self._labels["delete_button"]

    @property
    def save_changes_button(self) -> str:
        return self._labels["save_changes_button"]

    @property
    def discard_changes_button(self) -> str:
        return self._labels["discard_changes_button"]

    @property
    def set_hotkey_button(self) -> str:
        return self._labels["set_hotkey_button"]

    @property
    def close_button(self) -> str:
        return self._labels["close_button"]

    # Tab Labels
    @property
    def vocabulary_tab(self) -> str:
        return self._labels["vocabulary_tab"]

    @property
    def stt_instructions_tab(self) -> str:
        return self._labels["stt_instructions_tab"]

    @property
    def llm_instructions_tab(self) -> str:
        return self._labels["llm_instructions_tab"]

    @property
    def settings_tab(self) -> str:
        return self._labels["settings_tab"]

    # Checkbox Labels
    @property
    def include_clipboard_text(self) -> str:
        return self._labels["include_clipboard_text"]

    @property
    def include_clipboard_image(self) -> str:
        return self._labels["include_clipboard_image"]

    # Help/Description Text
    @property
    def vocabulary_help(self) -> str:
        return self._labels["vocabulary_help"]

    @property
    def stt_instructions_help(self) -> str:
        return self._labels["stt_instructions_help"]

    @property
    def llm_instructions_help(self) -> str:
        return self._labels["llm_instructions_help"]

    @property
    def settings_help(self) -> str:
        return self._labels["settings_help"]

    @property
    def clipboard_text_tooltip(self) -> str:
        return self._labels["clipboard_text_tooltip"]

    @property
    def clipboard_image_tooltip(self) -> str:
        return self._labels["clipboard_image_tooltip"]

    # Placeholder Text
    @property
    def no_hotkey_placeholder(self) -> str:
        return self._labels["no_hotkey_placeholder"]

    # Message Text
    @property
    def enter_instruction_set_name(self) -> str:
        return self._labels["enter_instruction_set_name"]

    @property
    def enter_new_name(self) -> str:
        return self._labels["enter_new_name"]

    @property
    def confirm_delete_message(self) -> str:
        return self._labels["confirm_delete_message"]

    @property
    def unsaved_changes_message(self) -> str:
        return self._labels["unsaved_changes_message"]

    @property
    def changes_discarded_message(self) -> str:
        return self._labels["changes_discarded_message"]


class InstructionDialog(QDialog):
    """
    Dialog for managing instruction sets.

    This dialog allows users to create, edit, delete, and select
    instruction sets with custom vocabulary, system instructions,
    language/model selection, and LLM settings.
    """

    def __init__(self, main_window: QWidget | None = None) -> None:
        """
        Initialize the InstructionDialog.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget, by default None
        """
        super().__init__(parent=main_window)

        # Initialize label manager
        self._label_manager = LabelManager()

        # Create controller
        self._controller = InstructionDialogController(instruction_dialog=self)

        # Track changes and hotkey state
        self._is_editing_mode = False
        self._hotkeys_disabled = False

        # Set up UI
        self._init_ui()

        # Load sets and options
        self._load_sets_and_options()

        # Connect controller signals
        self._connect_controller_signals()

    #
    # UI Setup
    #
    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Set dialog properties
        self.setWindowTitle(self._label_manager.window_title)
        self.setMinimumSize(700, 500)

        # Create main layout
        layout = QVBoxLayout(self)

        # Create splitter for list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - List of instruction sets
        left_widget = self._create_list_widget()

        # Right side - Editor
        right_widget = self._create_editor_widget()

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Set initial sizes
        splitter.setSizes([200, 500])

        # Add splitter to layout
        layout.addWidget(splitter)

        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self._on_click_close)

        layout.addWidget(button_box)

        # Set initial state
        self._set_editing_mode(is_editing_mode=False)

    def _create_list_widget(self) -> QWidget:
        """
        Create the left-side list widget for instruction sets.

        Returns
        -------
        QWidget
            The list widget containing instruction sets
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # List selection label
        list_label = QLabel(self._label_manager.instruction_sets_label)
        left_layout.addWidget(list_label)

        # Instruction sets list
        self._sets_list = QListWidget()
        self._sets_list.currentRowChanged.connect(self._on_set_selected)
        left_layout.addWidget(self._sets_list)

        # Buttons for managing sets
        buttons_layout = QHBoxLayout()

        self._add_button = QPushButton(self._label_manager.add_button)
        self._add_button.clicked.connect(self._on_click_add)

        self._rename_button = QPushButton(self._label_manager.rename_button)
        self._rename_button.clicked.connect(self._on_click_rename)

        self._delete_button = QPushButton(self._label_manager.delete_button)
        self._delete_button.clicked.connect(self._on_click_delete)

        buttons_layout.addWidget(self._add_button)
        buttons_layout.addWidget(self._rename_button)
        buttons_layout.addWidget(self._delete_button)
        left_layout.addLayout(buttons_layout)

        return left_widget

    def _create_editor_widget(self) -> QWidget:
        """
        Create the right-side editor widget for instruction set properties.

        Returns
        -------
        QWidget
            The editor widget for instruction set properties
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Tab widget for different properties
        self._tab_widget = QTabWidget()

        # Create tabs
        stt_vocabulary_tab = self._create_vocabulary_tab()
        stt_instructions_tab = self._create_stt_instructions_tab()
        llm_instructions_tab = self._create_llm_instructions_tab()
        settings_tab = self._create_settings_tab()

        # Add tabs to widget
        self._tab_widget.addTab(stt_vocabulary_tab, self._label_manager.vocabulary_tab)
        self._tab_widget.addTab(stt_instructions_tab, self._label_manager.stt_instructions_tab)
        self._tab_widget.addTab(llm_instructions_tab, self._label_manager.llm_instructions_tab)
        self._tab_widget.addTab(settings_tab, self._label_manager.settings_tab)

        right_layout.addWidget(self._tab_widget)

        # Save and Discard buttons
        save_buttons_layout = QHBoxLayout()

        self._save_button = QPushButton(self._label_manager.save_changes_button)
        self._save_button.clicked.connect(self._on_click_save)
        save_buttons_layout.addWidget(self._save_button)

        self._discard_button = QPushButton(self._label_manager.discard_changes_button)
        self._discard_button.clicked.connect(self._on_click_discard)
        save_buttons_layout.addWidget(self._discard_button)

        right_layout.addLayout(save_buttons_layout)

        return right_widget

    def _create_vocabulary_tab(self) -> QWidget:
        """
        Create the vocabulary tab.

        Returns
        -------
        QWidget
            The vocabulary tab widget
        """
        stt_vocabulary_tab = QWidget()
        stt_vocabulary_layout = QVBoxLayout(stt_vocabulary_tab)

        stt_vocabulary_label = QLabel(self._label_manager.custom_vocabulary_label)
        stt_vocabulary_layout.addWidget(stt_vocabulary_label)

        stt_vocabulary_help = QLabel(self._label_manager.vocabulary_help)
        stt_vocabulary_help.setWordWrap(True)
        stt_vocabulary_layout.addWidget(stt_vocabulary_help)

        self._stt_vocabulary_edit = QTextEdit()
        self._stt_vocabulary_edit.textChanged.connect(self._on_form_changed)
        stt_vocabulary_layout.addWidget(self._stt_vocabulary_edit)

        return stt_vocabulary_tab

    def _create_stt_instructions_tab(self) -> QWidget:
        """
        Create the STT instructions tab.

        Returns
        -------
        QWidget
            The STT instructions tab widget
        """
        stt_instructions_tab = QWidget()
        stt_instructions_layout = QVBoxLayout(stt_instructions_tab)

        stt_instructions_label = QLabel(self._label_manager.stt_instructions_label)
        stt_instructions_layout.addWidget(stt_instructions_label)

        stt_instructions_help = QLabel(self._label_manager.stt_instructions_help)
        stt_instructions_help.setWordWrap(True)
        stt_instructions_layout.addWidget(stt_instructions_help)

        self._stt_instructions_edit = QTextEdit()
        self._stt_instructions_edit.textChanged.connect(self._on_form_changed)
        stt_instructions_layout.addWidget(self._stt_instructions_edit)

        return stt_instructions_tab

    def _create_llm_instructions_tab(self) -> QWidget:
        """
        Create the LLM instructions tab.

        Returns
        -------
        QWidget
            The LLM instructions tab widget
        """
        llm_instructions_tab = QWidget()
        llm_instructions_layout = QVBoxLayout(llm_instructions_tab)

        llm_instructions_label = QLabel(self._label_manager.llm_instructions_label)
        llm_instructions_layout.addWidget(llm_instructions_label)

        llm_instructions_help = QLabel(self._label_manager.llm_instructions_help)
        llm_instructions_help.setWordWrap(True)
        llm_instructions_layout.addWidget(llm_instructions_help)

        self._llm_instructions_edit = QTextEdit()
        self._llm_instructions_edit.textChanged.connect(self._on_form_changed)
        llm_instructions_layout.addWidget(self._llm_instructions_edit)

        return llm_instructions_tab

    def _create_settings_tab(self) -> QWidget:
        """
        Create the settings tab.

        Returns
        -------
        QWidget
            The settings tab widget
        """
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        settings_help = QLabel(self._label_manager.settings_help)
        settings_help.setWordWrap(True)
        settings_layout.addWidget(settings_help)

        # Main form
        main_form = QWidget()
        main_layout = QFormLayout(main_form)

        # STT Language selection
        stt_language_label = QLabel(self._label_manager.stt_language_label)
        self._stt_language_combo = QComboBox()
        self._stt_language_combo.currentIndexChanged.connect(self._on_form_changed)
        main_layout.addRow(stt_language_label, self._stt_language_combo)

        # STT Model selection
        stt_model_label = QLabel(self._label_manager.stt_model_label)
        self._stt_model_combo = QComboBox()
        self._stt_model_combo.currentIndexChanged.connect(self._on_form_changed)
        main_layout.addRow(stt_model_label, self._stt_model_combo)

        # Hotkey selection
        hotkey_label = QLabel(self._label_manager.hotkey_label)
        self._hotkey_input = QLineEdit()
        self._hotkey_input.setReadOnly(True)
        self._hotkey_input.setPlaceholderText(self._label_manager.no_hotkey_placeholder)

        hotkey_button = QPushButton(self._label_manager.set_hotkey_button)
        hotkey_button.clicked.connect(self._on_click_hotkey)

        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self._hotkey_input)
        hotkey_layout.addWidget(hotkey_button)
        main_layout.addRow(hotkey_label, hotkey_layout)

        # LLM settings
        llm_enabled_label = QLabel(self._label_manager.enable_llm_processing_label)
        self._llm_enabled_checkbox = QCheckBox()
        self._llm_enabled_checkbox.stateChanged.connect(self._on_llm_enabled_changed)
        main_layout.addRow(llm_enabled_label, self._llm_enabled_checkbox)

        llm_model_label = QLabel(self._label_manager.llm_model_label)
        self._llm_model_combo = QComboBox()
        self._llm_model_combo.currentIndexChanged.connect(self._on_llm_model_changed)
        main_layout.addRow(llm_model_label, self._llm_model_combo)

        # LLM context options
        self._llm_clipboard_text_checkbox = QCheckBox(self._label_manager.include_clipboard_text)
        self._llm_clipboard_text_checkbox.setToolTip(self._label_manager.clipboard_text_tooltip)
        self._llm_clipboard_text_checkbox.stateChanged.connect(self._on_form_changed)
        main_layout.addRow(self._label_manager.context_label, self._llm_clipboard_text_checkbox)

        self._llm_clipboard_image_checkbox = QCheckBox(self._label_manager.include_clipboard_image)
        self._llm_clipboard_image_checkbox.setToolTip(self._label_manager.clipboard_image_tooltip)
        self._llm_clipboard_image_checkbox.stateChanged.connect(self._on_form_changed)
        main_layout.addRow("", self._llm_clipboard_image_checkbox)

        settings_layout.addWidget(main_form)
        settings_layout.addStretch(1)

        return settings_tab

    def _load_sets_and_options(self) -> None:
        """
        Load sets and options into the UI.
        """
        # Clear list
        self._sets_list.clear()

        # Add sets
        for instruction_set in self._controller.get_all_sets():
            self._sets_list.addItem(instruction_set.name)

        # Load available options
        self._load_stt_languages()
        self._load_stt_models()
        self._load_llm_models()

        # Select first item if available
        if self._sets_list.count() > 0:
            self._sets_list.setCurrentRow(0)

    def _load_stt_languages(self) -> None:
        """
        Load available STT languages into the combo box.
        """
        self._stt_language_combo.clear()

        stt_languages = self._controller.get_available_stt_languages()
        for lang in stt_languages:
            if lang.code:
                self._stt_language_combo.addItem(
                    f"{lang.name} ({lang.code})",
                    lang.code,
                )
            else:
                self._stt_language_combo.addItem(
                    lang.name,
                    lang.code,
                )

    def _load_stt_models(self) -> None:
        """
        Load available STT models into the combo box.
        """
        self._stt_model_combo.clear()

        stt_models = self._controller.get_available_stt_models()
        for stt_model in stt_models:
            self._stt_model_combo.addItem(
                stt_model.name,
                stt_model.id,
            )
            self._stt_model_combo.setItemData(
                self._stt_model_combo.count() - 1,
                stt_model.description,
                Qt.ItemDataRole.ToolTipRole,
            )

    def _load_llm_models(self) -> None:
        """
        Load available LLM models into the combo box.
        """
        self._llm_model_combo.clear()

        llm_models = self._controller.get_available_llm_models()
        for llm_model in llm_models:
            self._llm_model_combo.addItem(
                llm_model.name,
                llm_model.id,
            )
            self._llm_model_combo.setItemData(
                self._llm_model_combo.count() - 1,
                llm_model.description,
                Qt.ItemDataRole.ToolTipRole,
            )

    #
    # Controller Signals
    #
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        self._controller.instruction_set_added.connect(self._handle_instruction_set_added)
        self._controller.instruction_set_deleted.connect(self._handle_instruction_set_deleted)
        self._controller.instruction_set_renamed.connect(self._handle_instruction_set_renamed)
        self._controller.operation_result.connect(self._handle_operation_result)

    #
    # Controller Events
    #
    @pyqtSlot(str)
    def _handle_instruction_set_added(self, name: str) -> None:
        """
        Handle instruction set added event.

        Parameters
        ----------
        name : str
            The name of the added instruction set
        """
        # Add to list
        self._sets_list.addItem(name)

        # Select new item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == name:
                self._sets_list.setCurrentRow(i)
                break

    @pyqtSlot(str, str)
    def _handle_instruction_set_renamed(self, old_name: str, new_name: str) -> None:
        """
        Handle instruction set renamed event.

        Parameters
        ----------
        old_name : str
            The old name of the instruction set
        new_name : str
            The new name of the instruction set
        """
        # Find and update item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == old_name:
                self._sets_list.item(i).setText(new_name)
                break

    @pyqtSlot(str)
    def _handle_instruction_set_deleted(self, name: str) -> None:
        """
        Handle instruction set deleted event.

        Parameters
        ----------
        name : str
            The name of the instruction set that was deleted
        """
        # Find and remove item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == name:
                self._sets_list.takeItem(i)
                break

        # Select next item if available
        self._sets_list.setCurrentRow(0)

    @pyqtSlot(bool, str)
    def _handle_operation_result(self, success: bool, message: str) -> None:
        """
        Handle operation result event.

        Parameters
        ----------
        success : bool
            True if the operation was successful, False otherwise
        """
        if success:
            QMessageBox.information(
                self,
                self._label_manager.success_title,
                message,
                QMessageBox.StandardButton.Ok,
            )
        else:
            QMessageBox.warning(
                self,
                self._label_manager.error_title,
                message,
                QMessageBox.StandardButton.Ok,
            )

    #
    # UI Events
    #
    def _set_combo_value(self, combo: QComboBox, value: str) -> None:
        """
        Set combo box value by item data.

        Parameters
        ----------
        combo : QComboBox
            The combo box to set the value for
        value : str
            The value to set in the combo box
        """
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(0)  # Default to first item

    def _block_signals_from_editor_widget(self, is_signal_blocked: bool) -> None:
        """
        Block or unblock signals from editor widgets.

        Parameters
        ----------
        is_signal_blocked : bool
            True to block signals, False to unblock
        """
        editor_widget: list[QWidget] = [
            self._stt_vocabulary_edit,
            self._stt_instructions_edit,
            self._llm_instructions_edit,
            self._stt_language_combo,
            self._stt_model_combo,
            self._llm_enabled_checkbox,
            self._llm_model_combo,
            self._llm_clipboard_text_checkbox,
            self._llm_clipboard_image_checkbox,
        ]

        for widget in editor_widget:
            widget.blockSignals(is_signal_blocked)

    def _set_editing_mode(self, is_editing_mode: bool = False) -> None:
        """
        Set the editing mode of the dialog.

        Parameters
        ----------
        is_editing_mode : bool
            True if the dialog is in editing mode, False otherwise
        """
        # Enable/disable operation buttons based on changes
        self._is_editing_mode = is_editing_mode

        is_ui_enabled = not is_editing_mode

        self._add_button.setEnabled(is_ui_enabled)
        self._rename_button.setEnabled(is_ui_enabled)
        self._delete_button.setEnabled(is_ui_enabled)
        self._sets_list.setEnabled(is_ui_enabled)

        # Enable/disable save/discard buttons
        self._save_button.setEnabled(not is_ui_enabled)
        self._discard_button.setEnabled(not is_ui_enabled)

        # Update LLM UI state
        is_llm_enabled = self._llm_enabled_checkbox.isChecked()
        selected_model_id = self._llm_model_combo.currentData()
        is_image_supported = False

        if selected_model_id:
            is_image_supported = self._controller.check_image_input_supported(model_id=selected_model_id)

        self._llm_model_combo.setEnabled(is_llm_enabled)
        self._llm_clipboard_text_checkbox.setEnabled(is_llm_enabled)
        self._llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and is_image_supported)
        self._llm_instructions_edit.setEnabled(is_llm_enabled)

    def _apply_set_to_editor_widget(self, instruction_set: InstructionSet) -> None:
        """
        Apply the selected instruction set to the editor widget.

        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set that was selected
        """
        # Block signals to prevent triggering change events
        self._block_signals_from_editor_widget(is_signal_blocked=True)

        # Update UI with instruction set data
        self._stt_vocabulary_edit.setPlainText(instruction_set.stt_vocabulary)
        self._stt_instructions_edit.setPlainText(instruction_set.stt_instructions)
        self._llm_instructions_edit.setPlainText(instruction_set.llm_instructions)

        # Update language selection
        self._set_combo_value(self._stt_language_combo, instruction_set.stt_language)

        # Update STT model selection
        self._set_combo_value(self._stt_model_combo, instruction_set.stt_model)

        # Update LLM settings
        self._llm_enabled_checkbox.setChecked(instruction_set.llm_enabled)
        self._set_combo_value(self._llm_model_combo, instruction_set.llm_model)
        self._llm_clipboard_text_checkbox.setChecked(instruction_set.llm_clipboard_text_enabled)
        self._llm_clipboard_image_checkbox.setChecked(instruction_set.llm_clipboard_image_enabled)

        # Update hotkey
        self._hotkey_input.setText(instruction_set.hotkey)

        # Unblock signals
        self._block_signals_from_editor_widget(is_signal_blocked=False)

        # Set editing mode to False
        self._set_editing_mode(is_editing_mode=False)

    @pyqtSlot()
    def _on_click_add(self) -> None:
        """
        Handle adding a new instruction set.
        """
        name, ok = QInputDialog.getText(
            self,
            self._label_manager.new_instruction_set_title,
            self._label_manager.enter_instruction_set_name,
        )

        if ok and name:
            self._controller.add_set(name=name)

    @pyqtSlot()
    def _on_click_rename(self) -> None:
        """
        Handle renaming an instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        old_name = self._sets_list.item(row).text()

        new_name, ok = QInputDialog.getText(
            self,
            self._label_manager.rename_instruction_set_title,
            self._label_manager.enter_new_name,
            QLineEdit.EchoMode.Normal,
            old_name,
        )

        if ok and new_name and new_name != old_name:
            self._controller.rename_set(old_name=old_name, new_name=new_name)

    @pyqtSlot()
    def _on_click_delete(self) -> None:
        """
        Handle deleting an instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        name = self._sets_list.item(row).text()

        result = QMessageBox.question(
            self,
            self._label_manager.confirm_deletion_title,
            self._label_manager.confirm_delete_message.format(name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            self._controller.delete_set(name=name)

    @pyqtSlot(int)
    def _on_set_selected(self, row: int) -> None:
        """
        Handle selection of an instruction set.

        Parameters
        ----------
        row : int
            The row index of the selected instruction set
        """
        if row < 0:
            return

        # Get selected set name and notify controller
        set_name = self._sets_list.item(row).text()
        selected_set = self._controller.select_set(name=set_name)
        if selected_set:
            self._apply_set_to_editor_widget(instruction_set=selected_set)

    @pyqtSlot()
    def _on_form_changed(self) -> None:
        """
        Handle form value changes.
        """
        # Set editing mode to True
        self._set_editing_mode(is_editing_mode=True)

    @pyqtSlot(int)
    def _on_llm_enabled_changed(self, state: int) -> None:
        """
        Handle changes to the LLM enabled checkbox.

        Parameters
        ----------
        state : int
            The state of the LLM enabled checkbox
        """
        self._on_form_changed()

    @pyqtSlot(int)
    def _on_llm_model_changed(self, index: int) -> None:
        """
        Handle changes to the LLM model selection.

        Parameters
        ----------
        index : int
            The index of the selected LLM model
        """
        self._on_form_changed()

    @pyqtSlot()
    def _on_click_hotkey(self) -> None:
        """
        Handle setting a hotkey for the selected instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        set_name = self._sets_list.item(row).text()
        current_hotkey = self._hotkey_input.text()

        new_hotkey = self._controller.show_hotkey_dialog(
            current_hotkey=current_hotkey,
            set_name=set_name,
            instruction_dialog=self,
        )

        if new_hotkey is not None:
            self._hotkey_input.setText(new_hotkey)
            self._on_form_changed()

    @pyqtSlot()
    def _on_click_save(self) -> None:
        """
        Handle saving changes to the current instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        set_name = self._sets_list.item(row).text()

        # Collect values from UI
        kwargs = {
            "stt_vocabulary": self._stt_vocabulary_edit.toPlainText(),
            "stt_instructions": self._stt_instructions_edit.toPlainText(),
            "stt_language": self._stt_language_combo.currentData(),
            "stt_model": self._stt_model_combo.currentData(),
            "llm_enabled": self._llm_enabled_checkbox.isChecked(),
            "llm_model": self._llm_model_combo.currentData(),
            "llm_instructions": self._llm_instructions_edit.toPlainText(),
            "llm_clipboard_text_enabled": self._llm_clipboard_text_checkbox.isChecked(),
            "llm_clipboard_image_enabled": self._llm_clipboard_image_checkbox.isChecked(),
            "hotkey": self._hotkey_input.text(),
        }

        # Update set through controller
        self._controller.update_set(
            name=set_name,
            **kwargs,
        )

        # Set editing mode to False
        self._set_editing_mode(is_editing_mode=False)

    @pyqtSlot()
    def _on_click_discard(self) -> None:
        """
        Handle discarding changes to the current instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        # Get current instruction set and refresh UI
        set_name = self._sets_list.item(row).text()
        instruction_set = self._controller.get_set_by_name(name=set_name)
        if instruction_set:
            self._apply_set_to_editor_widget(instruction_set=instruction_set)

        QMessageBox.information(
            self,
            self._label_manager.changes_discarded_title,
            self._label_manager.changes_discarded_message,
            QMessageBox.StandardButton.Ok,
        )

    #
    # Open/Close Events
    #
    def _restore_hotkeys(self) -> None:
        """
        Restore hotkeys that were disabled.
        """
        if self._hotkeys_disabled:
            self._controller.start_listening()
            self._hotkeys_disabled = False

    def _show_unsaved_changes_dialog(self) -> QMessageBox.StandardButton:
        """
        Show dialog asking if unsaved changes should be saved.

        Returns
        -------
        QMessageBox.StandardButton
            The button that was clicked
        """
        return QMessageBox.question(
            self,
            self._label_manager.unsaved_changes_title,
            self._label_manager.unsaved_changes_message,
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

    def accept(self) -> None:
        """
        Handle dialog acceptance.
        """
        self._restore_hotkeys()
        super().accept()

    def reject(self) -> None:
        """
        Handle dialog rejection.
        """
        self._restore_hotkeys()
        super().reject()

    @pyqtSlot()
    def _on_click_close(self) -> None:
        """
        Handle dialog close event.
        """
        if self._is_editing_mode:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                return
            elif result == QMessageBox.StandardButton.Save:
                self._on_click_save()

        self._restore_hotkeys()
        self.accept()

    def showEvent(self, event: QShowEvent) -> None:
        """
        Handle dialog show event.

        Parameters
        ----------
        event : QShowEvent
            The show event
        """
        super().showEvent(event)

        # Disable hotkeys while dialog is open
        self._controller.stop_listening()
        self._hotkeys_disabled = True

        # Ensure UI reflects current selection
        row = self._sets_list.currentRow()
        if row >= 0:
            set_name = self._sets_list.item(row).text()
            instruction_set = self._controller.get_set_by_name(name=set_name)
            if instruction_set:
                self._apply_set_to_editor_widget(instruction_set=instruction_set)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Parameters
        ----------
        event : QCloseEvent
            The close event
        """
        if self._is_editing_mode:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif result == QMessageBox.StandardButton.Save:
                self._on_click_save()

        self._restore_hotkeys()
        event.accept()

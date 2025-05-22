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

from ...controllers.dialogs.instruction_dialog_controller import InstructionDialogController
from ..factories.hotkey_dialog_factory import HotkeyDialogFactory


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

        # Create controller
        self._controller = InstructionDialogController()

        # Track changes and hotkey state
        self._changes_made = False
        self._hotkeys_disabled = False

        # Set up UI
        self._init_ui()

        # Connect controller signals
        self._connect_controller_signals()

        # Load instruction sets
        self._load_instruction_sets()

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Set dialog properties
        self.setWindowTitle("Instruction Sets")
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
        button_box.rejected.connect(self.on_close)

        layout.addWidget(button_box)

        # Set initial state
        self._update_ui_state()

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
        list_label = QLabel("Instruction Sets")
        left_layout.addWidget(list_label)

        # Instruction sets list
        self._sets_list = QListWidget()
        self._sets_list.currentRowChanged.connect(self._on_set_selected)
        left_layout.addWidget(self._sets_list)

        # Buttons for managing sets
        buttons_layout = QHBoxLayout()

        self._add_button = QPushButton("Add")
        self._add_button.clicked.connect(self._on_add_set)

        self._rename_button = QPushButton("Rename")
        self._rename_button.clicked.connect(self._on_rename_set)

        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self._on_delete_set)

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
        vocab_tab = self._create_vocabulary_tab()
        stt_tab = self._create_stt_instructions_tab()
        llm_tab = self._create_llm_instructions_tab()
        settings_tab = self._create_settings_tab()

        # Add tabs to widget
        self._tab_widget.addTab(vocab_tab, "Vocabulary")
        self._tab_widget.addTab(stt_tab, "STT Instructions")
        self._tab_widget.addTab(llm_tab, "LLM Instructions")
        self._tab_widget.addTab(settings_tab, "Settings")

        right_layout.addWidget(self._tab_widget)

        # Save and Discard buttons
        save_buttons_layout = QHBoxLayout()

        self._save_button = QPushButton("Save Changes")
        self._save_button.clicked.connect(self._on_click_save)
        save_buttons_layout.addWidget(self._save_button)

        self._discard_button = QPushButton("Discard Changes")
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
        vocab_tab = QWidget()
        vocab_layout = QVBoxLayout(vocab_tab)

        vocab_label = QLabel("Custom Vocabulary")
        vocab_layout.addWidget(vocab_label)

        vocab_help = QLabel("Add custom technical terms, acronyms, or specialized vocabulary to improve transcription accuracy.")
        vocab_help.setWordWrap(True)
        vocab_layout.addWidget(vocab_help)

        self._vocabulary_edit = QTextEdit()
        self._vocabulary_edit.textChanged.connect(self._on_form_changed)
        vocab_layout.addWidget(self._vocabulary_edit)

        return vocab_tab

    def _create_stt_instructions_tab(self) -> QWidget:
        """
        Create the STT instructions tab.

        Returns
        -------
        QWidget
            The STT instructions tab widget
        """
        stt_tab = QWidget()
        stt_layout = QVBoxLayout(stt_tab)

        stt_label = QLabel("STT Instructions")
        stt_layout.addWidget(stt_label)

        stt_help = QLabel("Provide system instructions to guide the transcription process (formatting, focus areas, etc.)")
        stt_help.setWordWrap(True)
        stt_layout.addWidget(stt_help)

        self._stt_instructions_edit = QTextEdit()
        self._stt_instructions_edit.textChanged.connect(self._on_form_changed)
        stt_layout.addWidget(self._stt_instructions_edit)

        return stt_tab

    def _create_llm_instructions_tab(self) -> QWidget:
        """
        Create the LLM instructions tab.

        Returns
        -------
        QWidget
            The LLM instructions tab widget
        """
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)

        llm_label = QLabel("LLM Instructions")
        llm_layout.addWidget(llm_label)

        llm_help = QLabel("Provide system instructions for the LLM to guide its processing of transcription results.")
        llm_help.setWordWrap(True)
        llm_layout.addWidget(llm_help)

        self._llm_instructions_edit = QTextEdit()
        self._llm_instructions_edit.textChanged.connect(self._on_form_changed)
        llm_layout.addWidget(self._llm_instructions_edit)

        return llm_tab

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

        settings_help = QLabel("Configure language, model, and other settings for this instruction set.")
        settings_help.setWordWrap(True)
        settings_layout.addWidget(settings_help)

        # Main form
        main_form = QWidget()
        main_layout = QFormLayout(main_form)

        # STT Language selection
        stt_language_label = QLabel("STT Language")
        self._stt_language_combo = QComboBox()
        self._stt_language_combo.currentIndexChanged.connect(self._on_form_changed)
        main_layout.addRow(stt_language_label, self._stt_language_combo)

        # STT Model selection
        stt_model_label = QLabel("STT Model")
        self._stt_model_combo = QComboBox()
        self._stt_model_combo.currentIndexChanged.connect(self._on_form_changed)
        main_layout.addRow(stt_model_label, self._stt_model_combo)

        # Hotkey selection
        hotkey_label = QLabel("Hotkey")
        self._hotkey_input = QLineEdit()
        self._hotkey_input.setReadOnly(True)
        self._hotkey_input.setPlaceholderText("No hotkey set")

        hotkey_button = QPushButton("Set Hotkey")
        hotkey_button.clicked.connect(self._on_click_hotkey)

        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self._hotkey_input)
        hotkey_layout.addWidget(hotkey_button)
        main_layout.addRow(hotkey_label, hotkey_layout)

        # LLM settings
        llm_enabled_label = QLabel("Enable LLM Processing")
        self._llm_enabled_checkbox = QCheckBox()
        self._llm_enabled_checkbox.stateChanged.connect(self._on_llm_enabled_changed)
        main_layout.addRow(llm_enabled_label, self._llm_enabled_checkbox)

        llm_model_label = QLabel("LLM Model")
        self._llm_model_combo = QComboBox()
        self._llm_model_combo.currentIndexChanged.connect(self._on_llm_model_changed)
        main_layout.addRow(llm_model_label, self._llm_model_combo)

        # LLM context options
        self._llm_clipboard_text_checkbox = QCheckBox("Include Clipboard Text")
        self._llm_clipboard_text_checkbox.setToolTip("Include text from clipboard when processing with LLM")
        self._llm_clipboard_text_checkbox.stateChanged.connect(self._on_form_changed)
        main_layout.addRow("Context", self._llm_clipboard_text_checkbox)

        self._llm_clipboard_image_checkbox = QCheckBox("Include Clipboard Image")
        self._llm_clipboard_image_checkbox.setToolTip("Include image from clipboard when processing with LLM (if supported by model)")
        self._llm_clipboard_image_checkbox.stateChanged.connect(self._on_form_changed)
        main_layout.addRow("", self._llm_clipboard_image_checkbox)

        settings_layout.addWidget(main_form)
        settings_layout.addStretch(1)

        return settings_tab

    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        self._controller.instruction_set_added.connect(self._handle_instruction_set_added)
        self._controller.instruction_set_updated.connect(self._handle_instruction_set_updated)
        self._controller.instruction_set_deleted.connect(self._handle_instruction_set_deleted)
        self._controller.instruction_set_renamed.connect(self._handle_instruction_set_renamed)
        self._controller.instruction_set_selected.connect(self._handle_instruction_set_selected)
        self._controller.operation_result.connect(self._handle_operation_result)

    def _load_instruction_sets(self) -> None:
        """
        Load instruction sets into the UI.
        """
        # Clear list
        self._sets_list.clear()

        # Add sets
        for instruction_set in self._controller.get_all_sets():
            self._sets_list.addItem(instruction_set.name)

        # Load available options
        self._load_languages()
        self._load_stt_models()
        self._load_llm_models()

        # Select first item if available
        if self._sets_list.count() > 0:
            self._sets_list.setCurrentRow(0)

    def _load_languages(self) -> None:
        """
        Load available languages into the combo box.
        """
        self._stt_language_combo.clear()

        languages = self._controller.get_available_languages()
        for lang in languages:
            if lang.code:
                self._stt_language_combo.addItem(f"{lang.name} ({lang.code})", lang.code)
            else:
                self._stt_language_combo.addItem(lang.name, lang.code)

    def _load_stt_models(self) -> None:
        """
        Load available STT models into the combo box.
        """
        self._stt_model_combo.clear()

        models = self._controller.get_available_stt_models()
        for model in models:
            self._stt_model_combo.addItem(model.name, model.id)
            self._stt_model_combo.setItemData(self._stt_model_combo.count() - 1, model.description, Qt.ItemDataRole.ToolTipRole)

    def _load_llm_models(self) -> None:
        """
        Load available LLM models into the combo box.
        """
        self._llm_model_combo.clear()

        models = self._controller.get_available_llm_models()
        for model in models:
            self._llm_model_combo.addItem(model.name, model.id)
            self._llm_model_combo.setItemData(self._llm_model_combo.count() - 1, model.description, Qt.ItemDataRole.ToolTipRole)

    def _update_ui_state(self) -> None:
        """
        Update the UI state based on current settings.
        """
        # Enable/disable operation buttons based on changes
        operations_enabled = not self._changes_made

        self._add_button.setEnabled(operations_enabled)
        self._rename_button.setEnabled(operations_enabled)
        self._delete_button.setEnabled(operations_enabled)
        self._sets_list.setEnabled(operations_enabled)

        # Enable/disable save/discard buttons
        self._save_button.setEnabled(self._changes_made)
        self._discard_button.setEnabled(self._changes_made)

        # Update LLM UI state
        is_llm_enabled = self._llm_enabled_checkbox.isChecked()
        selected_model_id = self._llm_model_combo.currentData()
        supports_image = False

        if selected_model_id:
            supports_image = self._controller.check_image_input_supported(selected_model_id)

        self._llm_model_combo.setEnabled(is_llm_enabled)
        self._llm_clipboard_text_checkbox.setEnabled(is_llm_enabled)
        self._llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
        self._llm_instructions_edit.setEnabled(is_llm_enabled)

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

        # Check for unsaved changes
        if self._changes_made:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                # Revert selection - this is handled by the controller
                return
            elif result == QMessageBox.StandardButton.Save:
                self._on_click_save()

        # Get selected set name and notify controller
        set_name = self._sets_list.item(row).text()
        self._controller.select_set(set_name)

    @pyqtSlot(InstructionSet)
    def _handle_instruction_set_selected(self, instruction_set: InstructionSet) -> None:
        """
        Handle instruction set selected event.

        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set that was selected
        """
        # Block signals to prevent triggering change events
        self._block_signals(True)

        # Update UI with instruction set data
        self._vocabulary_edit.setPlainText(instruction_set.stt_vocabulary)
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
        self._block_signals(False)

        # Reset changes flag
        self._changes_made = False

        # Update UI state
        self._update_ui_state()

    def _block_signals(self, block: bool) -> None:
        """
        Block or unblock signals from form elements.

        Parameters
        ----------
        block : bool
            True to block signals, False to unblock
        """
        widgets = [
            self._vocabulary_edit,
            self._stt_instructions_edit,
            self._llm_instructions_edit,
            self._stt_language_combo,
            self._stt_model_combo,
            self._llm_enabled_checkbox,
            self._llm_model_combo,
            self._llm_clipboard_text_checkbox,
            self._llm_clipboard_image_checkbox,
        ]

        for widget in widgets:
            widget.blockSignals(block)

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

    def _on_form_changed(self) -> None:
        """
        Handle form value changes.
        """
        if self.isVisible():  # Only mark changes if dialog is visible
            self._changes_made = True
            self._update_ui_state()

    @pyqtSlot()
    def _on_add_set(self) -> None:
        """
        Handle adding a new instruction set.
        """
        name, ok = QInputDialog.getText(
            self,
            "New Instruction Set",
            "Enter a name for the new instruction set:",
        )

        if ok and name:
            self._controller.add_set(name)

    @pyqtSlot(InstructionSet)
    def _handle_instruction_set_added(self, instruction_set: InstructionSet) -> None:
        """
        Handle instruction set added event.

        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set that was added
        """
        # Add to list
        self._sets_list.addItem(instruction_set.name)

        # Select new item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == instruction_set.name:
                self._sets_list.setCurrentRow(i)
                break

    @pyqtSlot()
    def _on_rename_set(self) -> None:
        """
        Handle renaming an instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        old_name = self._sets_list.item(row).text()

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Instruction Set",
            "Enter a new name for the instruction set:",
            QLineEdit.EchoMode.Normal,
            old_name,
        )

        if ok and new_name and new_name != old_name:
            self._controller.rename_set(old_name, new_name)

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

    @pyqtSlot()
    def _on_delete_set(self) -> None:
        """
        Handle deleting an instruction set.
        """
        row = self._sets_list.currentRow()
        if row < 0:
            return

        name = self._sets_list.item(row).text()

        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the instruction set '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            self._controller.delete_set(name)

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
        if self._sets_list.count() > 0:
            self._sets_list.setCurrentRow(min(i, self._sets_list.count() - 1))

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

        dialog = HotkeyDialogFactory.create_dialog(
            current_hotkey=current_hotkey,
            instruction_dialog=self,
        )
        result = dialog.exec()

        if result:
            new_hotkey = dialog.get_hotkey()
            if new_hotkey != current_hotkey:
                self._controller.update_hotkey(set_name=set_name, hotkey=new_hotkey)
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
            "stt_vocabulary": self._vocabulary_edit.toPlainText(),
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
        self._controller.update_set(set_name, **kwargs)

        # Reset changes flag
        self._changes_made = False
        self._update_ui_state()

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
        instruction_set = self._controller.get_set_by_name(set_name)
        if instruction_set:
            self._handle_instruction_set_selected(instruction_set)

        QMessageBox.information(
            self,
            "Changes Discarded",
            "Changes have been discarded.",
            QMessageBox.StandardButton.Ok,
        )

    @pyqtSlot(InstructionSet)
    def _handle_instruction_set_updated(self, instruction_set: InstructionSet) -> None:
        """
        Handle instruction set updated event.

        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set that was updated
        """
        # No action needed here as the UI is already updated
        pass

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
                "Success",
                message,
                QMessageBox.StandardButton.Ok,
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                message,
                QMessageBox.StandardButton.Ok,
            )

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
        self._update_ui_state()

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
        self._update_ui_state()

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
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

    def on_close(self) -> None:
        """
        Handle dialog close event.
        """
        if self._changes_made:
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
            instruction_set = self._controller.get_set_by_name(set_name)
            if instruction_set:
                self._handle_instruction_set_selected(instruction_set)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Parameters
        ----------
        event : QCloseEvent
            The close event
        """
        if self._changes_made:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif result == QMessageBox.StandardButton.Save:
                self._on_click_save()

        self._restore_hotkeys()
        event.accept()

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

    def _restore_hotkeys(self) -> None:
        """
        Restore hotkeys that were disabled.
        """
        if self._hotkeys_disabled:
            self._controller.start_listening()
            self._hotkeys_disabled = False

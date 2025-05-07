"""
Instruction Dialog View

This module provides the view component for the instruction dialog in the Super Whisper application.
It provides the UI for managing instruction sets.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QDialogButtonBox, QListWidget, QSplitter,
    QLineEdit, QInputDialog, QTabWidget, QWidget,
    QFormLayout, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent, QShowEvent

from ...controllers.dialogs.instruction_dialog_controller import InstructionDialogController
from core.pipelines.instruction_set import InstructionSet
from gui.dialogs.hotkey_dialog import HotkeyDialog


class InstructionDialog(QDialog):
    """
    Dialog for managing instruction sets.
    
    This dialog allows users to create, edit, delete, and select
    instruction sets with custom vocabulary, system instructions,
    language/model selection, and LLM (Large Language Model) settings.
    
    Attributes
    ----------
    _controller : InstructionDialogController
        The controller for this dialog
    _sets_list : QListWidget
        Widget displaying the list of instruction sets
    _tab_widget : QTabWidget
        Widget containing tabs for different instruction set properties
    _vocabulary_edit : QTextEdit
        Widget for editing custom vocabulary
    _instructions_edit : QTextEdit
        Widget for editing STT system instructions
    _llm_instructions_edit : QTextEdit
        Widget for editing LLM system instructions
    _stt_language_combo : QComboBox
        Widget for selecting STT language
    _stt_model_combo : QComboBox
        Widget for selecting STT model
    _llm_enabled_checkbox : QCheckBox
        Widget for enabling LLM processing
    _llm_model_combo : QComboBox
        Widget for selecting LLM model
    _llm_clipboard_text_checkbox : QCheckBox
        Widget for enabling clipboard text in LLM input
    _llm_clipboard_image_checkbox : QCheckBox
        Widget for enabling clipboard image in LLM input
    _hotkey_input : QLineEdit
        Widget for displaying and setting hotkeys
    """
    
    def __init__(self, controller: InstructionDialogController, parent=None):
        """
        Initialize the InstructionDialog.
        
        Parameters
        ----------
        controller : InstructionDialogController
            The controller for this dialog
        parent : QWidget, optional
            Parent widget, by default None
        """
        super().__init__(parent)
        
        # Store controller
        self._controller = controller
        
        # Flag to track if changes were made - initialize before UI setup
        self._changes_made = False
        
        # Flag to track if hotkeys were disabled
        self._hotkeys_disabled = False
        
        # Set up UI
        self._init_ui()
        
        # Connect controller signals
        self._connect_controller_signals()
        
        # Load instruction sets
        self._load_instruction_sets()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Instruction Sets")
        self.setMinimumSize(700, 500)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create splitter for list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - List of instruction sets
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
        
        # Initially disable operation buttons until saved
        self._update_operation_buttons()
        
        # Right side - Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tab widget for vocabulary, instructions, and settings
        self._tab_widget = QTabWidget()
        
        # Vocabulary tab
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
        
        # Instructions tab
        instr_tab = QWidget()
        instr_layout = QVBoxLayout(instr_tab)
        
        instr_label = QLabel("System Instructions")
        instr_layout.addWidget(instr_label)
        
        instr_help = QLabel("Provide system instructions to guide the transcription process (formatting, focus areas, etc.)")
        instr_help.setWordWrap(True)
        instr_layout.addWidget(instr_help)
        
        self._instructions_edit = QTextEdit()
        self._instructions_edit.textChanged.connect(self._on_form_changed)
        instr_layout.addWidget(self._instructions_edit)
        
        # Settings tab for language and model
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_help = QLabel("Configure language, model, and other settings for this instruction set.")
        settings_help.setWordWrap(True)
        settings_layout.addWidget(settings_help)
        
        # Language selection
        main_form = QWidget()
        main_layout = QFormLayout(main_form)
        
        stt_language_label = QLabel("Language")
        self._stt_language_combo = QComboBox()
        self._stt_language_combo.currentIndexChanged.connect(self._on_form_changed)
        
        # Model selection
        stt_model_label = QLabel("STT Model")
        self._stt_model_combo = QComboBox()
        self._stt_model_combo.currentIndexChanged.connect(self._on_form_changed)
        
        main_layout.addRow(stt_language_label, self._stt_language_combo)
        main_layout.addRow(stt_model_label, self._stt_model_combo)
        
        # Add hotkey selection
        hotkey_label = QLabel("Hotkey")
        self._hotkey_input = QLineEdit()
        self._hotkey_input.setReadOnly(True)
        self._hotkey_input.setPlaceholderText("No hotkey set")

        hotkey_button = QPushButton("Set Hotkey")
        hotkey_button.clicked.connect(self._on_set_hotkey)
        
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self._hotkey_input)
        hotkey_layout.addWidget(hotkey_button)
        
        main_layout.addRow(hotkey_label, hotkey_layout)

        # LLM enable/disable
        llm_enabled_label = QLabel("Enable LLM Processing")
        self._llm_enabled_checkbox = QCheckBox()
        self._llm_enabled_checkbox.stateChanged.connect(self._on_llm_enabled_changed)
        main_layout.addRow(llm_enabled_label, self._llm_enabled_checkbox)
        
        # LLM model selection
        llm_model_label = QLabel("LLM Model")
        self._llm_model_combo = QComboBox()
        self._llm_model_combo.currentIndexChanged.connect(self._on_llm_model_changed)
        main_layout.addRow(llm_model_label, self._llm_model_combo)
        
        # Add checkbox for clipboard text
        self._llm_clipboard_text_checkbox = QCheckBox("Include Clipboard Text")
        self._llm_clipboard_text_checkbox.setToolTip("Include text from clipboard when processing with LLM")
        self._llm_clipboard_text_checkbox.stateChanged.connect(self._on_form_changed)
        main_layout.addRow("Context", self._llm_clipboard_text_checkbox)
        
        # Add checkbox for clipboard image
        self._llm_clipboard_image_checkbox = QCheckBox("Include Clipboard Image")
        self._llm_clipboard_image_checkbox.setToolTip("Include image from clipboard when processing with LLM (if supported by model)")
        self._llm_clipboard_image_checkbox.stateChanged.connect(self._on_form_changed)
        main_layout.addRow("", self._llm_clipboard_image_checkbox)

        settings_layout.addWidget(main_form)
        
        # Add spacer
        settings_layout.addStretch(1)
        
        # LLM Instructions tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        llm_label = QLabel("LLM Instructions")
        llm_layout.addWidget(llm_label)
        
        llm_help = QLabel("Provide system instructions for the LLM to guide its processing of transcription results.")
        llm_help.setWordWrap(True)
        llm_layout.addWidget(llm_help)
        
        # LLM instructions        
        self._llm_instructions_edit = QTextEdit()
        self._llm_instructions_edit.setEnabled(False)  # Disabled by default
        self._llm_instructions_edit.textChanged.connect(self._on_form_changed)
        llm_layout.addWidget(self._llm_instructions_edit)
        
        # Add tabs to the tab widget in specified order
        self._tab_widget.addTab(vocab_tab, "Vocabulary")
        self._tab_widget.addTab(instr_tab, "Instructions")
        self._tab_widget.addTab(llm_tab, "LLM Instructions")
        self._tab_widget.addTab(settings_tab, "Settings")
        
        right_layout.addWidget(self._tab_widget)
        
        # Save and Discard buttons layout
        save_buttons_layout = QHBoxLayout()
        
        # Save changes button
        self._save_button = QPushButton("Save Changes")
        self._save_button.clicked.connect(self._on_save_changes)
        self._save_button.setEnabled(False)  # Initially disabled until changes are made
        save_buttons_layout.addWidget(self._save_button)
        
        # Discard changes button
        self._discard_button = QPushButton("Discard Changes")
        self._discard_button.clicked.connect(self._on_discard_changes)
        self._discard_button.setEnabled(False)  # Initially disabled until changes are made
        save_buttons_layout.addWidget(self._discard_button)
        
        # Add buttons layout to main layout
        right_layout.addLayout(save_buttons_layout)

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
        
        # Set initial state of LLM-related UI components
        # By default, these should be disabled unless LLM is enabled
        self._llm_model_combo.setEnabled(False)
        self._llm_clipboard_text_checkbox.setEnabled(False)
        self._llm_clipboard_image_checkbox.setEnabled(False)
        # LLM tab's contents will be enabled/disabled when a set is selected
    
    def _connect_controller_signals(self):
        """Connect signals from the controller."""
        # Connect controller signals to local methods
        self._controller.instruction_set_added.connect(self._on_instruction_set_added)
        self._controller.instruction_set_updated.connect(self._on_instruction_set_updated)
        self._controller.instruction_set_deleted.connect(self._on_instruction_set_deleted)
        self._controller.instruction_set_renamed.connect(self._on_instruction_set_renamed)
        self._controller.instruction_set_selected.connect(self._on_instruction_set_selected)
        self._controller.hotkey_conflict.connect(self._on_hotkey_conflict)
        self._controller.operation_result.connect(self._on_operation_result)
        
    def _load_instruction_sets(self):
        """Load instruction sets into the UI."""
        # Clear list
        self._sets_list.clear()
        
        # Add sets
        for instruction_set in self._controller.get_all_sets():
            self._sets_list.addItem(instruction_set.name)
        
        # Select first item if available
        if self._sets_list.count() > 0:
            self._sets_list.setCurrentRow(0)
            
        # Load available languages
        self._load_languages()
        
        # Load available STT models
        self._load_stt_models()
        
        # Load available LLM models
        self._load_llm_models()
    
    def _load_languages(self):
        """Load available languages into the language combo box."""
        # Clear combo box
        self._stt_language_combo.clear()
        
        # Add auto-detect option
        self._stt_language_combo.addItem("Auto-detect", None)
        
        # Add languages
        languages = self._controller.get_available_languages()
        for lang in languages:
            self._stt_language_combo.addItem(f"{lang.name} ({lang.code})", lang.code)
    
    def _load_stt_models(self):
        """Load available STT models into the model combo box."""
        # Clear combo box
        self._stt_model_combo.clear()
        
        # Add models
        models = self._controller.get_available_stt_models()
        for model in models:
            self._stt_model_combo.addItem(model.name, model.id)
            self._stt_model_combo.setItemData(
                self._stt_model_combo.count() - 1,
                model.description,
                Qt.ItemDataRole.ToolTipRole
            )
    
    def _load_llm_models(self):
        """Load available LLM models into the model combo box."""
        # Clear combo box
        self._llm_model_combo.clear()
        
        # Add models
        models = self._controller.get_available_llm_models()
        for model in models:
            self._llm_model_combo.addItem(model.name, model.id)
            self._llm_model_combo.setItemData(
                self._llm_model_combo.count() - 1,
                model.description,
                Qt.ItemDataRole.ToolTipRole
            )
    
    @pyqtSlot(int)
    def _on_set_selected(self, row):
        """
        Handle selection of an instruction set.
        
        Parameters
        ----------
        row : int
            Selected row index.
        """
        if row < 0:
            # Clear editors
            self._vocabulary_edit.clear()
            self._instructions_edit.clear()
            self._llm_instructions_edit.clear()
            self._llm_enabled_checkbox.setChecked(False)
            self._hotkey_input.clear()
            return
        
        # Get selected set name
        set_name = self._sets_list.item(row).text()
        
        # Select the set in the controller
        self._controller.select_set(set_name)
    
    @pyqtSlot(InstructionSet)
    def _on_instruction_set_selected(self, instruction_set: InstructionSet):
        """
        Handle the instruction set selected event from the controller.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The selected instruction set
        """
        # Check if we need to prompt for unsaved changes
        if self._changes_made:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                # Revert selection
                for i in range(self._sets_list.count()):
                    if self._sets_list.item(i).text() == instruction_set.name:
                        self._sets_list.setCurrentRow(i)
                        break
                return
            elif result == QMessageBox.StandardButton.Save:
                # Save changes before switching
                self._on_save_changes()
        
        # Block signals before setting values to prevent _on_form_changed from being triggered
        self._vocabulary_edit.blockSignals(True)
        self._instructions_edit.blockSignals(True)
        self._llm_instructions_edit.blockSignals(True)
        self._stt_language_combo.blockSignals(True)
        self._stt_model_combo.blockSignals(True)
        self._llm_enabled_checkbox.blockSignals(True)
        self._llm_model_combo.blockSignals(True)
        self._llm_clipboard_text_checkbox.blockSignals(True)
        self._llm_clipboard_image_checkbox.blockSignals(True)
        
        # Reset changes flag
        self._changes_made = False
        self._save_button.setEnabled(False)
        self._discard_button.setEnabled(False)
        
        # Update operation buttons based on save state
        self._update_operation_buttons()
        
        # Update vocabulary and instructions
        self._vocabulary_edit.setPlainText(instruction_set.stt_vocabulary)
        self._instructions_edit.setPlainText(instruction_set.stt_instructions)
        
        # Update language selection
        language_index = 0  # Default to auto-detect
        if instruction_set.stt_language:
            for i in range(self._stt_language_combo.count()):
                if self._stt_language_combo.itemData(i) == instruction_set.stt_language:
                    language_index = i
                    break
        self._stt_language_combo.setCurrentIndex(language_index)
        
        # Update STT model selection
        model_index = 0  # Default to first model
        for i in range(self._stt_model_combo.count()):
            if self._stt_model_combo.itemData(i) == instruction_set.stt_model:
                model_index = i
                break
        self._stt_model_combo.setCurrentIndex(model_index)
        
        # Update LLM settings
        is_llm_enabled = instruction_set.llm_enabled
        self._llm_enabled_checkbox.setChecked(is_llm_enabled)
        
        # Update LLM model selection
        llm_model_index = 0  # Default to first model
        for i in range(self._llm_model_combo.count()):
            if self._llm_model_combo.itemData(i) == instruction_set.llm_model:
                llm_model_index = i
                break
        self._llm_model_combo.setCurrentIndex(llm_model_index)
        
        # Update LLM clipboard options
        self._llm_clipboard_text_checkbox.setChecked(instruction_set.llm_clipboard_text_enabled)
        self._llm_clipboard_image_checkbox.setChecked(instruction_set.llm_clipboard_image_enabled)
        
        # Update LLM instructions
        self._llm_instructions_edit.setPlainText(instruction_set.llm_instructions)
        
        # Update hotkey field
        self._hotkey_input.setText(instruction_set.hotkey)
        
        # Check if model supports image input
        supports_image = False
        if instruction_set.llm_model:
            supports_image = self._controller.supports_image_input(instruction_set.llm_model)
        
        # Set enabled state for LLM-related UI components
        self._llm_model_combo.setEnabled(is_llm_enabled)
        self._llm_clipboard_text_checkbox.setEnabled(is_llm_enabled)
        self._llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
        self._llm_instructions_edit.setEnabled(is_llm_enabled)
        
        # Unblock signals
        self._vocabulary_edit.blockSignals(False)
        self._instructions_edit.blockSignals(False)
        self._llm_instructions_edit.blockSignals(False)
        self._stt_language_combo.blockSignals(False)
        self._stt_model_combo.blockSignals(False)
        self._llm_enabled_checkbox.blockSignals(False)
        self._llm_model_combo.blockSignals(False)
        self._llm_clipboard_text_checkbox.blockSignals(False)
        self._llm_clipboard_image_checkbox.blockSignals(False)
    
    def _update_operation_buttons(self):
        """
        Update the enabled state of operation buttons based on save state.
        
        This method controls whether buttons like Add, Rename, Delete, and
        the instruction set list should be enabled based on whether the
        current changes have been saved.
        """
        # If there are unsaved changes, disable operations
        operations_enabled = not self._changes_made
        
        # Update button states
        self._add_button.setEnabled(operations_enabled)
        self._rename_button.setEnabled(operations_enabled)
        self._delete_button.setEnabled(operations_enabled)
        
        # Control the list selection ability
        # Note: We don't completely disable the list widget as it's needed to show selection
        # Instead, we'll handle selection change attempts in the _on_set_selected method
        self._sets_list.setEnabled(operations_enabled)
    
    def _on_form_changed(self):
        """
        Handle form value changes.
        
        This method is called when any form element changes its value.
        It marks the form as having unsaved changes and updates the UI accordingly.
        """
        # During initialization, the dialog might still be in setup phase
        # Only mark changes if the window is fully visible
        if self.isVisible():
            # Set changes flag
            self._changes_made = True
            
            # Enable save and discard buttons
            self._save_button.setEnabled(True)
            self._discard_button.setEnabled(True)
            
            # Update operation buttons
            self._update_operation_buttons()
    
    def _on_add_set(self):
        """Handle adding a new instruction set."""
        # Show input dialog
        name, ok = QInputDialog.getText(
            self,
            "New Instruction Set",
            "Enter a name for the new instruction set:"
        )
        
        if ok and name:
            # Add new set
            self._controller.add_set(name)
    
    @pyqtSlot(InstructionSet)
    def _on_instruction_set_added(self, instruction_set: InstructionSet):
        """
        Handle instruction set added event from the controller.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The added instruction set
        """
        # Add to list
        self._sets_list.addItem(instruction_set.name)
        
        # Select new item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == instruction_set.name:
                self._sets_list.setCurrentRow(i)
                break
    
    def _on_rename_set(self):
        """Handle renaming an instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        old_name = self._sets_list.item(row).text()
        
        # Show input dialog
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Instruction Set",
            "Enter a new name for the instruction set:",
            QLineEdit.EchoMode.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Rename set
            self._controller.rename_set(old_name, new_name)
    
    @pyqtSlot(str, str)
    def _on_instruction_set_renamed(self, old_name: str, new_name: str):
        """
        Handle instruction set renamed event from the controller.
        
        Parameters
        ----------
        old_name : str
            Old name of the set
        new_name : str
            New name of the set
        """
        # Find and update item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == old_name:
                self._sets_list.item(i).setText(new_name)
                break
    
    def _on_delete_set(self):
        """Handle deleting an instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        name = self._sets_list.item(row).text()
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the instruction set '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Delete set
            self._controller.delete_set(name)
    
    @pyqtSlot(str)
    def _on_instruction_set_deleted(self, name: str):
        """
        Handle instruction set deleted event from the controller.
        
        Parameters
        ----------
        name : str
            Name of the deleted set
        """
        # Find and remove item
        for i in range(self._sets_list.count()):
            if self._sets_list.item(i).text() == name:
                self._sets_list.takeItem(i)
                break
        
        # Select next item if available
        if self._sets_list.count() > 0:
            self._sets_list.setCurrentRow(min(i, self._sets_list.count() - 1))
    
    def _on_set_hotkey(self):
        """Handle setting a hotkey for the selected instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        set_name = self._sets_list.item(row).text()
        
        # Show hotkey dialog
        
        # Get current hotkey
        current_hotkey = self._hotkey_input.text()
        
        dialog = HotkeyDialog(self, current_hotkey)
        result = dialog.exec()
        
        if result:
            new_hotkey = dialog.get_hotkey()
            if new_hotkey != current_hotkey:
                # Update hotkey
                self._controller.update_hotkey(set_name, new_hotkey)
                # Update UI
                self._hotkey_input.setText(new_hotkey)
                # Mark form as changed
                self._on_form_changed()
    
    @pyqtSlot(str, str)
    def _on_hotkey_conflict(self, hotkey: str, conflict_set_name: str):
        """
        Handle hotkey conflict event from the controller.
        
        Parameters
        ----------
        hotkey : str
            The conflicting hotkey
        conflict_set_name : str
            Name of the set that already uses the hotkey
        """
        if conflict_set_name:
            QMessageBox.warning(
                self,
                "Hotkey Conflict",
                f"The hotkey '{hotkey}' is already used by instruction set '{conflict_set_name}'.",
                QMessageBox.StandardButton.Ok
            )
        else:
            QMessageBox.warning(
                self,
                "Hotkey Registration Failed",
                f"Failed to register hotkey '{hotkey}'. It may be in use by another application.",
                QMessageBox.StandardButton.Ok
            )
    
    def _on_save_changes(self):
        """Handle saving changes to the current instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        # Get selected set name
        set_name = self._sets_list.item(row).text()
        
        # Get values from UI
        stt_vocabulary = self._vocabulary_edit.toPlainText()
        stt_instructions = self._instructions_edit.toPlainText()
        stt_language = self._stt_language_combo.currentData()
        stt_model = self._stt_model_combo.currentData()
        llm_enabled = self._llm_enabled_checkbox.isChecked()
        llm_model = self._llm_model_combo.currentData()
        llm_instructions = self._llm_instructions_edit.toPlainText()
        llm_clipboard_text_enabled = self._llm_clipboard_text_checkbox.isChecked()
        llm_clipboard_image_enabled = self._llm_clipboard_image_checkbox.isChecked()
        hotkey = self._hotkey_input.text()
        
        # Update set
        self._controller.update_set(
            set_name,
            stt_vocabulary=stt_vocabulary,
            stt_instructions=stt_instructions,
            stt_language=stt_language,
            stt_model=stt_model,
            llm_enabled=llm_enabled,
            llm_model=llm_model,
            llm_instructions=llm_instructions,
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
            hotkey=hotkey
        )
        
        # Reset changes flag
        self._changes_made = False
        self._save_button.setEnabled(False)
        self._discard_button.setEnabled(False)
        
        # Update operation buttons - enable after save
        self._update_operation_buttons()
    
    def _on_discard_changes(self):
        """Handle discarding changes to the current instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        # Get selected set name
        set_name = self._sets_list.item(row).text()
        
        # Get the instruction set from the controller
        instruction_set = self._controller.get_set_by_name(set_name)
        if not instruction_set:
            return
        
        # Block signals to prevent _on_form_changed from being triggered
        self._vocabulary_edit.blockSignals(True)
        self._instructions_edit.blockSignals(True)
        self._llm_instructions_edit.blockSignals(True)
        self._stt_language_combo.blockSignals(True)
        self._stt_model_combo.blockSignals(True)
        self._llm_enabled_checkbox.blockSignals(True)
        self._llm_model_combo.blockSignals(True)
        self._llm_clipboard_text_checkbox.blockSignals(True)
        self._llm_clipboard_image_checkbox.blockSignals(True)
        
        # Reset values to the current instruction set values
        self._vocabulary_edit.setPlainText(instruction_set.stt_vocabulary)
        self._instructions_edit.setPlainText(instruction_set.stt_instructions)
        
        # Update language selection
        language_index = 0  # Default to auto-detect
        if instruction_set.stt_language:
            for i in range(self._stt_language_combo.count()):
                if self._stt_language_combo.itemData(i) == instruction_set.stt_language:
                    language_index = i
                    break
        self._stt_language_combo.setCurrentIndex(language_index)
        
        # Update STT model selection
        model_index = 0  # Default to first model
        for i in range(self._stt_model_combo.count()):
            if self._stt_model_combo.itemData(i) == instruction_set.stt_model:
                model_index = i
                break
        self._stt_model_combo.setCurrentIndex(model_index)
        
        # Update LLM settings
        is_llm_enabled = instruction_set.llm_enabled
        self._llm_enabled_checkbox.setChecked(is_llm_enabled)
        
        # Update LLM model selection
        llm_model_index = 0  # Default to first model
        for i in range(self._llm_model_combo.count()):
            if self._llm_model_combo.itemData(i) == instruction_set.llm_model:
                llm_model_index = i
                break
        self._llm_model_combo.setCurrentIndex(llm_model_index)
        
        # Update LLM clipboard options
        self._llm_clipboard_text_checkbox.setChecked(instruction_set.llm_clipboard_text_enabled)
        self._llm_clipboard_image_checkbox.setChecked(instruction_set.llm_clipboard_image_enabled)
        
        # Update LLM instructions
        self._llm_instructions_edit.setPlainText(instruction_set.llm_instructions)
        
        # Update hotkey field
        self._hotkey_input.setText(instruction_set.hotkey)
        
        # Check if model supports image input
        supports_image = False
        if instruction_set.llm_model:
            supports_image = self._controller.supports_image_input(instruction_set.llm_model)
        
        # Set enabled state for LLM-related UI components
        self._llm_model_combo.setEnabled(is_llm_enabled)
        self._llm_clipboard_text_checkbox.setEnabled(is_llm_enabled)
        self._llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
        self._llm_instructions_edit.setEnabled(is_llm_enabled)
        
        # Unblock signals
        self._vocabulary_edit.blockSignals(False)
        self._instructions_edit.blockSignals(False)
        self._llm_instructions_edit.blockSignals(False)
        self._stt_language_combo.blockSignals(False)
        self._stt_model_combo.blockSignals(False)
        self._llm_enabled_checkbox.blockSignals(False)
        self._llm_model_combo.blockSignals(False)
        self._llm_clipboard_text_checkbox.blockSignals(False)
        self._llm_clipboard_image_checkbox.blockSignals(False)
        
        # Reset changes flag
        self._changes_made = False
        self._save_button.setEnabled(False)
        self._discard_button.setEnabled(False)
        
        # Update operation buttons
        self._update_operation_buttons()
        
        # Show a message to inform the user
        QMessageBox.information(
            self,
            "Changes Discarded",
            "Changes have been discarded.",
            QMessageBox.StandardButton.Ok
        )
    
    @pyqtSlot(InstructionSet)
    def _on_instruction_set_updated(self, instruction_set: InstructionSet):
        """
        Handle instruction set updated event from the controller.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The updated instruction set
        """
        # No action needed here as the UI is already updated
        # The event is primarily for other components to respond to changes
        pass
    
    @pyqtSlot(bool, str)
    def _on_operation_result(self, success: bool, message: str):
        """
        Handle operation result event from the controller.
        
        Parameters
        ----------
        success : bool
            Whether the operation was successful
        message : str
            Message to display
        """
        if success:
            QMessageBox.information(
                self,
                "Success",
                message,
                QMessageBox.StandardButton.Ok
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                message,
                QMessageBox.StandardButton.Ok
            )
    
    @pyqtSlot(int)
    def _on_llm_enabled_changed(self, state: int):
        """
        Handle changes to the LLM enabled checkbox.
        
        Parameters
        ----------
        state : int
            Checkbox state (Qt.Checked or Qt.Unchecked)
        """
        # Mark form as changed
        self._on_form_changed()
        
        # Define if LLM is enabled
        is_enabled = state == Qt.CheckState.Checked.value
        
        # Get current selected LLM model
        selected_model_id = self._llm_model_combo.currentData()
        
        # Check if model supports image input
        supports_image = False
        if selected_model_id:
            supports_image = self._controller.supports_image_input(selected_model_id)
        
        # Enable/disable LLM model selector
        self._llm_model_combo.setEnabled(is_enabled)
        
        # Enable/disable LLM context checkboxes
        self._llm_clipboard_text_checkbox.setEnabled(is_enabled)
        
        # Image checkbox is enabled only if LLM is enabled AND model supports images
        self._llm_clipboard_image_checkbox.setEnabled(is_enabled and supports_image)
        
        # Enable/disable LLM instructions
        self._llm_instructions_edit.setEnabled(is_enabled)
    
    @pyqtSlot(int)
    def _on_llm_model_changed(self, index: int):
        """
        Handle changes to the LLM model selection.
        
        Parameters
        ----------
        index : int
            Index of the selected model
        """
        # Mark form as changed
        self._on_form_changed()
        
        # Get the selected model ID
        selected_model_id = self._llm_model_combo.itemData(index)
        
        # Check if LLM is enabled
        is_llm_enabled = self._llm_enabled_checkbox.isChecked()
        
        # Check if model supports image input
        supports_image = False
        if selected_model_id:
            supports_image = self._controller.supports_image_input(selected_model_id)
        
        # Update UI components
        # Image checkbox is enabled only if LLM is enabled AND model supports images
        self._llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
        
        # If model doesn't support images, uncheck the checkbox
        if not supports_image:
            self._llm_clipboard_image_checkbox.setChecked(False)
    
    def _show_unsaved_changes_dialog(self):
        """
        Show a dialog asking if unsaved changes should be saved.
        
        Returns
        -------
        QMessageBox.StandardButton
            The user's choice (Save, Discard, or Cancel)
        """
        return QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
    
    def on_close(self):
        """Handle dialog close event."""
        # Check if there are unsaved changes
        if self._changes_made:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                return
            elif result == QMessageBox.StandardButton.Save:
                self._on_save_changes()
        
        # Re-enable hotkeys if they were disabled
        self._restore_hotkeys()
        
        # Close the dialog
        self.accept()
    
    def showEvent(self, event: QShowEvent):
        """
        Handle dialog show event.
        
        This method is called when the dialog is shown. It disables all hotkeys
        to prevent them from being triggered while the dialog is open.
        It also ensures the initial state is "saved" to enable operation buttons.
        
        Parameters
        ----------
        event : QShowEvent
            Show event
        """
        # Call parent class method first
        super().showEvent(event)
        
        # Disable hotkeys
        if self._controller._hotkey_model:
            self._controller._hotkey_model.stop_listening()
            self._hotkeys_disabled = True
            
        # Ensure initial state is "saved" to enable operation buttons
        self._changes_made = False
        self._save_button.setEnabled(False)
        self._discard_button.setEnabled(False)
        self._update_operation_buttons()
    
    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.
        
        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Check if there are unsaved changes
        if self._changes_made:
            result = self._show_unsaved_changes_dialog()
            if result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif result == QMessageBox.StandardButton.Save:
                self._on_save_changes()
        
        # Re-enable hotkeys if they were disabled
        self._restore_hotkeys()
        
        # Accept the event to close the dialog
        event.accept()
    
    def accept(self):
        """
        Handle dialog acceptance.
        
        This method is called when the dialog is accepted (e.g., by clicking Close).
        It re-enables hotkeys that were disabled when the dialog was shown.
        """
        # Re-enable hotkeys if they were disabled
        self._restore_hotkeys()
        
        # Call parent class method
        super().accept()
    
    def reject(self):
        """
        Handle dialog rejection.
        
        This method is called when the dialog is rejected (e.g., by pressing Escape).
        It re-enables hotkeys that were disabled when the dialog was shown.
        """
        # Re-enable hotkeys if they were disabled
        self._restore_hotkeys()
        
        # Call parent class method
        super().reject()
    
    def _restore_hotkeys(self):
        """
        Restore hotkeys that were disabled.
        
        This method re-enables all hotkeys that were disabled when the dialog was shown.
        """
        if self._hotkeys_disabled and self._controller._hotkey_model:
            self._controller._hotkey_model.start_listening()
            self._hotkeys_disabled = False

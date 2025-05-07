"""
Instruction Sets Dialog

This module provides a dialog for managing instruction sets, including creating,
editing, and deleting sets. It is based on the GUI reference implementation
but simplified for the Super Whisper App.
"""

from typing import Optional, List

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QDialogButtonBox, QListWidget, QSplitter,
    QLineEdit, QInputDialog, QTabWidget, QWidget,
    QFormLayout, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings

from core.pipelines.instruction_set import InstructionSet
from super_whisper_app.app.controllers.app_controller import AppController


class InstructionSetsDialog(QDialog):
    """
    Dialog for managing instruction sets.
    
    This dialog allows users to create, edit, delete, and select
    instruction sets with custom vocabulary, system instructions,
    language settings, and LLM configurations.
    """
    
    def __init__(self, parent=None, controller=None):
        """
        Initialize the InstructionSetsDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        controller : AppController, optional
            Application controller with instruction set management functionality
        """
        super().__init__(parent)
        
        # Store controller
        self._controller = controller
        
        # Set up UI
        self._init_ui()
        
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
        
        vocab_help = QLabel(
            "Enter custom vocabulary, technical terms, names, or other specific words "
            "that should be recognized during transcription. Each entry on a new line."
        )
        vocab_help.setWordWrap(True)
        vocab_layout.addWidget(vocab_help)
        
        self._vocabulary_edit = QTextEdit()
        vocab_layout.addWidget(self._vocabulary_edit)
        
        # Instructions tab
        instr_tab = QWidget()
        instr_layout = QVBoxLayout(instr_tab)
        
        instr_label = QLabel("System Instructions")
        instr_layout.addWidget(instr_label)
        
        instr_help = QLabel(
            "Enter system instructions to guide the transcription process, "
            "such as formatting preferences or domain-specific handling."
        )
        instr_help.setWordWrap(True)
        instr_layout.addWidget(instr_help)
        
        self._instructions_edit = QTextEdit()
        instr_layout.addWidget(self._instructions_edit)
        
        # Settings tab for language and model
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_help = QLabel(
            "Configure language, model, and hotkey settings for this instruction set."
        )
        settings_help.setWordWrap(True)
        settings_layout.addWidget(settings_help)
        
        # Form layout for settings
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Language selection
        self._language_label = QLabel("Language:")
        self._language_combo = QComboBox()
        
        # Add language options (simplified for this implementation)
        self._language_combo.addItem("Auto-detect", None)
        self._language_combo.addItem("English", "en")
        self._language_combo.addItem("Japanese", "ja")
        self._language_combo.addItem("French", "fr")
        self._language_combo.addItem("German", "de")
        self._language_combo.addItem("Spanish", "es")
        self._language_combo.addItem("Chinese", "zh")
        
        form_layout.addRow(self._language_label, self._language_combo)
        
        # Model selection
        self._model_label = QLabel("Model:")
        self._model_combo = QComboBox()
        
        # Add model options (simplified)
        self._model_combo.addItem("GPT-4o Transcribe", "gpt-4o-transcribe")
        self._model_combo.addItem("Whisper", "whisper")
        
        form_layout.addRow(self._model_label, self._model_combo)
        
        # Add hotkey selection
        self._hotkey_label = QLabel("Hotkey:")
        self._hotkey_input = QLineEdit()
        self._hotkey_input.setReadOnly(True)
        self._hotkey_input.setPlaceholderText("No hotkey assigned")
        
        self._hotkey_button = QPushButton("Set Hotkey")
        self._hotkey_button.clicked.connect(self._show_hotkey_dialog)
        
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self._hotkey_input)
        hotkey_layout.addWidget(self._hotkey_button)
        
        form_layout.addRow(self._hotkey_label, hotkey_layout)
        
        # LLM enable/disable
        self._llm_enabled_label = QLabel("Enable LLM Processing:")
        self._llm_enabled_checkbox = QCheckBox()
        self._llm_enabled_checkbox.stateChanged.connect(self._on_llm_enabled_changed)
        form_layout.addRow(self._llm_enabled_label, self._llm_enabled_checkbox)
        
        # LLM model selection
        self._llm_model_label = QLabel("LLM Model:")
        self._llm_model_combo = QComboBox()
        
        # Add model options
        self._llm_model_combo.addItem("GPT-4o", "gpt-4o")
        self._llm_model_combo.addItem("GPT-3.5 Turbo", "gpt-3.5-turbo")
        
        form_layout.addRow(self._llm_model_label, self._llm_model_combo)
        
        # LLM context options
        self._llm_clipboard_text_checkbox = QCheckBox("Include clipboard text")
        self._llm_clipboard_text_checkbox.setToolTip(
            "Include text from clipboard as context for LLM analysis"
        )
        form_layout.addRow("LLM Context:", self._llm_clipboard_text_checkbox)
        
        self._llm_clipboard_image_checkbox = QCheckBox("Include clipboard images")
        self._llm_clipboard_image_checkbox.setToolTip(
            "Include images from clipboard as context for LLM analysis (for supported models)"
        )
        form_layout.addRow("", self._llm_clipboard_image_checkbox)
        
        # Add form to settings tab
        settings_layout.addWidget(form_widget)
        settings_layout.addStretch(1)
        
        # LLM Instructions tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        llm_label = QLabel("LLM Instructions")
        llm_layout.addWidget(llm_label)
        
        llm_help = QLabel(
            "Enter system instructions for the Large Language Model analysis. "
            "These instructions will guide how the LLM processes the transcription."
        )
        llm_help.setWordWrap(True)
        llm_layout.addWidget(llm_help)
        
        self._llm_instructions_edit = QTextEdit()
        llm_layout.addWidget(self._llm_instructions_edit)
        
        # Add tabs to the tab widget
        self._tab_widget.addTab(vocab_tab, "Vocabulary")
        self._tab_widget.addTab(instr_tab, "Instructions")
        self._tab_widget.addTab(llm_tab, "LLM")
        self._tab_widget.addTab(settings_tab, "Settings")
        
        right_layout.addWidget(self._tab_widget)
        
        # Save changes button
        self._save_button = QPushButton("Save Changes")
        self._save_button.clicked.connect(self._on_save_changes)
        right_layout.addWidget(self._save_button)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes
        splitter.setSizes([200, 500])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Add standard button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)  # Close button
        
        layout.addWidget(button_box)
        
        # Disable LLM components by default
        self._set_llm_components_enabled(False)
    
    def _load_instruction_sets(self):
        """Load instruction sets into the UI."""
        if not self._controller:
            return
        
        # Clear list
        self._sets_list.clear()
        
        # Add sets
        for instruction_set in self._controller.get_instruction_sets():
            self._sets_list.addItem(instruction_set.name)
        
        # Select the current set
        selected_set = self._controller.get_selected_instruction_set()
        if selected_set:
            for i in range(self._sets_list.count()):
                if self._sets_list.item(i).text() == selected_set.name:
                    self._sets_list.setCurrentRow(i)
                    break
    
    def _on_set_selected(self, row):
        """
        Handle selection of an instruction set.
        
        Parameters
        ----------
        row : int
            Selected row index.
        """
        if row < 0 or not self._controller:
            # Clear editors
            self._vocabulary_edit.clear()
            self._instructions_edit.clear()
            self._llm_instructions_edit.clear()
            self._llm_enabled_checkbox.setChecked(False)
            self._hotkey_input.clear()
            return
        
        # Get selected set name
        set_name = self._sets_list.item(row).text()
        
        # Find instruction set
        instruction_set = None
        for set_item in self._controller.get_instruction_sets():
            if set_item.name == set_name:
                instruction_set = set_item
                break
        
        if not instruction_set:
            return
        
        # Update UI with set data
        self._vocabulary_edit.setPlainText(instruction_set.stt_vocabulary)
        self._instructions_edit.setPlainText(instruction_set.stt_instructions)
        self._llm_instructions_edit.setPlainText(instruction_set.llm_instructions)
        
        # Set language
        language_index = 0  # Default to auto-detect
        if instruction_set.stt_language:
            for i in range(self._language_combo.count()):
                if self._language_combo.itemData(i) == instruction_set.stt_language:
                    language_index = i
                    break
        self._language_combo.setCurrentIndex(language_index)
        
        # Set model
        model_index = 0  # Default to first model
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == instruction_set.stt_model:
                model_index = i
                break
        self._model_combo.setCurrentIndex(model_index)
        
        # Set LLM options
        is_llm_enabled = instruction_set.llm_enabled
        self._llm_enabled_checkbox.setChecked(is_llm_enabled)
        
        # Set LLM model
        llm_model_index = 0  # Default to first model
        for i in range(self._llm_model_combo.count()):
            if self._llm_model_combo.itemData(i) == instruction_set.llm_model:
                llm_model_index = i
                break
        self._llm_model_combo.setCurrentIndex(llm_model_index)
        
        # Set LLM context options
        self._llm_clipboard_text_checkbox.setChecked(instruction_set.llm_clipboard_text_enabled)
        self._llm_clipboard_image_checkbox.setChecked(instruction_set.llm_clipboard_image_enabled)
        
        # Set hotkey
        self._hotkey_input.setText(instruction_set.hotkey)
        
        # Update LLM components enabled state
        self._set_llm_components_enabled(is_llm_enabled)
    
    def _on_add_set(self):
        """Handle adding a new instruction set."""
        name, ok = QInputDialog.getText(
            self,
            "New Instruction Set",
            "Enter name for new instruction set:"
        )
        
        if ok and name:
            # Check if name already exists
            for i in range(self._sets_list.count()):
                if self._sets_list.item(i).text() == name:
                    QMessageBox.warning(
                        self,
                        "Name Exists",
                        f"An instruction set named '{name}' already exists."
                    )
                    return
            
            # Create new set
            if self._controller.create_instruction_set(name):
                # Refresh the list to include the new set
                self._load_instruction_sets()
                
                # Select the new set
                for i in range(self._sets_list.count()):
                    if self._sets_list.item(i).text() == name:
                        self._sets_list.setCurrentRow(i)
                        break
    
    def _on_rename_set(self):
        """Handle renaming an instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        old_name = self._sets_list.item(row).text()
        
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Instruction Set",
            "Enter new name:",
            QLineEdit.EchoMode.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Check if name already exists
            for i in range(self._sets_list.count()):
                if i != row and self._sets_list.item(i).text() == new_name:
                    QMessageBox.warning(
                        self,
                        "Name Exists",
                        f"An instruction set named '{new_name}' already exists."
                    )
                    return
            
            # Rename set
            if self._controller.rename_instruction_set(old_name, new_name):
                # Update list item
                self._sets_list.item(row).setText(new_name)
    
    def _on_delete_set(self):
        """Handle deleting an instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        # Check if this is the last set - can't delete the last set
        if self._sets_list.count() <= 1:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete the last instruction set."
            )
            return
        
        name = self._sets_list.item(row).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the instruction set '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete set
            if self._controller.delete_instruction_set(name):
                # Refresh the list
                self._load_instruction_sets()
            else:
                QMessageBox.warning(
                    self,
                    "Deletion Failed",
                    f"Failed to delete instruction set '{name}'."
                )
    
    def _show_hotkey_dialog(self):
        """Show dialog to set a hotkey."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        # For this simplified implementation, just use a text input dialog
        current_hotkey = self._hotkey_input.text()
        
        new_hotkey, ok = QInputDialog.getText(
            self,
            "Set Hotkey",
            "Enter hotkey (e.g., 'ctrl+shift+1'):",
            QLineEdit.EchoMode.Normal,
            current_hotkey
        )
        
        if ok:
            # Update the hotkey field
            self._hotkey_input.setText(new_hotkey)
    
    def _on_save_changes(self):
        """Handle saving changes to the current instruction set."""
        row = self._sets_list.currentRow()
        if row < 0:
            return
        
        name = self._sets_list.item(row).text()
        
        # Get edited values
        vocabulary = self._vocabulary_edit.toPlainText()
        instructions = self._instructions_edit.toPlainText()
        
        # Get language and model settings
        language = self._language_combo.currentData()
        model = self._model_combo.currentData()
        
        # Get LLM settings
        llm_enabled = self._llm_enabled_checkbox.isChecked()
        llm_model = self._llm_model_combo.currentData()
        llm_instructions = self._llm_instructions_edit.toPlainText()
        
        # Get LLM context settings
        llm_clipboard_text_enabled = self._llm_clipboard_text_checkbox.isChecked()
        llm_clipboard_image_enabled = self._llm_clipboard_image_checkbox.isChecked()
        
        # Get hotkey
        hotkey = self._hotkey_input.text()
        
        # Update set
        success = self._controller.update_instruction_set(
            name,
            vocabulary=vocabulary,
            instructions=instructions,
            stt_language=language,
            stt_model=model,
            llm_enabled=llm_enabled,
            llm_model=llm_model,
            llm_instructions=llm_instructions,
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
            hotkey=hotkey
        )
        
        if success:
            QMessageBox.information(
                self,
                "Changes Saved",
                f"Changes to instruction set '{name}' have been saved."
            )
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Failed to save changes to instruction set '{name}'."
            )
    
    def _on_llm_enabled_changed(self, state):
        """
        Handle changes to the LLM enabled checkbox.
        
        Parameters
        ----------
        state : int
            Checkbox state.
        """
        is_enabled = state == Qt.CheckState.Checked.value
        self._set_llm_components_enabled(is_enabled)
    
    def _set_llm_components_enabled(self, enabled):
        """
        Set enabled state for LLM-related UI components.
        
        Parameters
        ----------
        enabled : bool
            Whether the components should be enabled.
        """
        self._llm_model_combo.setEnabled(enabled)
        self._llm_clipboard_text_checkbox.setEnabled(enabled)
        self._llm_clipboard_image_checkbox.setEnabled(enabled)
        self._llm_instructions_edit.setEnabled(enabled)

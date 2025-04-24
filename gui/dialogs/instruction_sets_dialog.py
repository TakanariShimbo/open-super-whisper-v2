"""
Instruction Sets Dialog

This module provides a dialog for managing instruction sets and custom vocabulary.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QDialogButtonBox, QListWidget, QSplitter,
    QLineEdit, QInputDialog, QMessageBox, QTabWidget, QWidget,
    QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

from gui.resources.labels import AppLabels
from gui.dialogs.simple_message_dialog import SimpleMessageDialog

# Import core instruction sets
from core.instructions import InstructionSetManager, InstructionSet

# Import language and model data
from core.models.language import LanguageManager
from core.models.whisper import WhisperModelManager


class GUIInstructionSetManager:
    """
    GUI wrapper for the core InstructionSetManager.
    
    This class wraps the core InstructionSetManager to provide GUI-specific
    functionality, such as QSettings integration.
    """
    
    def __init__(self, settings: QSettings):
        """
        Initialize the GUI instruction set manager.
        
        Parameters
        ----------
        settings : QSettings
            Settings object to store/retrieve data.
        """
        self.settings = settings
        self.core_manager = InstructionSetManager()
        self.load_from_settings()
    
    @property
    def active_set(self):
        """Get the active instruction set."""
        return self.core_manager.active_set
    
    def get_all_sets(self):
        """Get all instruction sets."""
        return self.core_manager.get_all_sets()
    
    def create_set(self, name, vocabulary=None, instructions=None, language=None, model=None):
        """Create a new instruction set."""
        result = self.core_manager.create_set(name, vocabulary, instructions, language, model)
        self.save_to_settings()
        return result
    
    def update_set(self, name, vocabulary=None, instructions=None, language=None, model=None):
        """Update an existing instruction set."""
        result = self.core_manager.update_set(name, vocabulary, instructions, language, model)
        self.save_to_settings()
        return result
    
    def delete_set(self, name):
        """Delete an instruction set."""
        result = self.core_manager.delete_set(name)
        self.save_to_settings()
        return result
    
    def set_active(self, name):
        """Set the active instruction set."""
        result = self.core_manager.set_active(name)
        self.save_to_settings()
        return result
    
    def rename_set(self, old_name, new_name):
        """Rename an instruction set."""
        result = self.core_manager.rename_set(old_name, new_name)
        self.save_to_settings()
        return result
    
    def get_active_vocabulary(self):
        """Get vocabulary from the active set."""
        return self.core_manager.get_active_vocabulary()
    
    def get_active_instructions(self):
        """Get instructions from the active set."""
        return self.core_manager.get_active_instructions()
    
    def get_active_language(self):
        """Get language setting from the active set."""
        return self.core_manager.get_active_language()
    
    def get_active_model(self):
        """Get model setting from the active set."""
        return self.core_manager.get_active_model()
    
    def save_to_settings(self):
        """Save all instruction sets to settings."""
        data = self.core_manager.to_dict()
        
        # Save to QSettings
        prefix = "InstructionSets"
        self.settings.beginGroup(prefix)
        
        # Remove any existing sets first
        self.settings.remove("")
        
        # Save active set
        self.settings.setValue("ActiveSet", data["active_set"])
        
        # Save sets
        self.settings.setValue("Sets", data["sets"])
        
        self.settings.endGroup()
        self.settings.sync()
    
    def load_from_settings(self):
        """Load instruction sets from settings."""
        # Get from QSettings
        prefix = "InstructionSets"
        self.settings.beginGroup(prefix)
        
        # Load active set
        active_set = self.settings.value("ActiveSet", "")
        
        # Load sets
        sets = self.settings.value("Sets", [])
        
        self.settings.endGroup()
        
        # Convert to dict for core manager
        data = {
            "active_set": active_set,
            "sets": sets
        }
        
        # Load into core manager
        self.core_manager.load_from_dict(data)


class InstructionSetsDialog(QDialog):
    """
    Dialog for managing instruction sets.
    
    This dialog allows users to create, edit, delete, and select
    instruction sets with custom vocabulary and system instructions.
    """
    
    def __init__(self, parent=None, manager=None):
        """
        Initialize the InstructionSetsDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        manager : GUIInstructionSetManager, optional
            Instruction set manager, by default None
        """
        super().__init__(parent)
        
        self.manager = manager
        
        # Set up UI
        self.init_ui()
        
        # Load instruction sets
        self.load_instruction_sets()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle(AppLabels.INSTRUCTION_SETS_TITLE)
        self.setMinimumSize(700, 500)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create splitter for list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - List of instruction sets
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # List selection label
        list_label = QLabel(AppLabels.INSTRUCTION_SETS_LIST_LABEL)
        left_layout.addWidget(list_label)
        
        # Instruction sets list
        self.sets_list = QListWidget()
        self.sets_list.currentRowChanged.connect(self.on_set_selected)
        left_layout.addWidget(self.sets_list)
        
        # Buttons for managing sets
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton(AppLabels.INSTRUCTION_SETS_ADD_BUTTON)
        self.add_button.clicked.connect(self.on_add_set)
        
        self.rename_button = QPushButton(AppLabels.INSTRUCTION_SETS_RENAME_BUTTON)
        self.rename_button.clicked.connect(self.on_rename_set)
        
        self.delete_button = QPushButton(AppLabels.INSTRUCTION_SETS_DELETE_BUTTON)
        self.delete_button.clicked.connect(self.on_delete_set)
        
        self.activate_button = QPushButton(AppLabels.INSTRUCTION_SETS_ACTIVATE_BUTTON)
        self.activate_button.clicked.connect(self.on_activate_set)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.rename_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.activate_button)
        left_layout.addLayout(buttons_layout)
        
        # Right side - Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tab widget for vocabulary, instructions, and settings
        self.tab_widget = QTabWidget()
        
        # Vocabulary tab
        vocab_tab = QWidget()
        vocab_layout = QVBoxLayout(vocab_tab)
        
        vocab_label = QLabel(AppLabels.INSTRUCTION_SETS_VOCABULARY_LABEL)
        vocab_layout.addWidget(vocab_label)
        
        vocab_help = QLabel(AppLabels.INSTRUCTION_SETS_VOCABULARY_HELP)
        vocab_help.setWordWrap(True)
        vocab_layout.addWidget(vocab_help)
        
        self.vocabulary_edit = QTextEdit()
        vocab_layout.addWidget(self.vocabulary_edit)
        
        # Instructions tab
        instr_tab = QWidget()
        instr_layout = QVBoxLayout(instr_tab)
        
        instr_label = QLabel(AppLabels.INSTRUCTION_SETS_INSTRUCTIONS_LABEL)
        instr_layout.addWidget(instr_label)
        
        instr_help = QLabel(AppLabels.INSTRUCTION_SETS_INSTRUCTIONS_HELP)
        instr_help.setWordWrap(True)
        instr_layout.addWidget(instr_help)
        
        self.instructions_edit = QTextEdit()
        instr_layout.addWidget(self.instructions_edit)
        
        # Settings tab for language and model
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_help = QLabel(AppLabels.INSTRUCTION_SETS_SETTINGS_HELP)
        settings_help.setWordWrap(True)
        settings_layout.addWidget(settings_help)
        
        # Language selection
        language_form = QWidget()
        language_layout = QFormLayout(language_form)
        
        language_label = QLabel(AppLabels.INSTRUCTION_SETS_LANGUAGE_LABEL)
        self.language_combo = QComboBox()
        
        # Add language options from LanguageManager
        languages = LanguageManager.get_languages()
        for language in languages:
            self.language_combo.addItem(language.name, language.code)
            # Add tooltip with native name if available
            if language.native_name and language.native_name != language.name:
                self.language_combo.setItemData(
                    self.language_combo.count() - 1,
                    f"{language.name} ({language.native_name})",
                    Qt.ItemDataRole.ToolTipRole
                )
        
        language_layout.addRow(language_label, self.language_combo)
        
        # Model selection
        model_label = QLabel(AppLabels.INSTRUCTION_SETS_MODEL_LABEL)
        self.model_combo = QComboBox()
        
        # Add model options from WhisperModelManager
        models = WhisperModelManager.get_models()
        for model in models:
            self.model_combo.addItem(model.name, model.id)
            # Add tooltip
            self.model_combo.setItemData(
                self.model_combo.count() - 1,
                model.description,
                Qt.ItemDataRole.ToolTipRole
            )
        
        language_layout.addRow(model_label, self.model_combo)
        settings_layout.addWidget(language_form)
        
        # Add spacer
        settings_layout.addStretch(1)
        
        # Add tabs
        self.tab_widget.addTab(vocab_tab, AppLabels.INSTRUCTION_SETS_VOCABULARY_TAB_NAME)
        self.tab_widget.addTab(instr_tab, AppLabels.INSTRUCTION_SETS_INSTRUCTIONS_TAB_NAME)
        self.tab_widget.addTab(settings_tab, AppLabels.INSTRUCTION_SETS_LANGUAGE_AND_MODEL_TAB_NAME)
        
        right_layout.addWidget(self.tab_widget)
        
        
        # Save changes button - style consistent with other buttons
        self.save_button = QPushButton(AppLabels.INSTRUCTION_SETS_SAVE_BUTTON)
        self.save_button.clicked.connect(self.on_save_changes)
        right_layout.addWidget(self.save_button)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes
        splitter.setSizes([200, 500])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)  # Close button
        
        layout.addWidget(button_box)
    
    def load_instruction_sets(self):
        """Load instruction sets into the UI."""
        if not self.manager:
            return
        
        # Clear list
        self.sets_list.clear()
        
        # Add sets
        for instruction_set in self.manager.get_all_sets():
            self.sets_list.addItem(instruction_set.name)
        
        # Select active set
        active_set = self.manager.active_set
        if active_set:
            for i in range(self.sets_list.count()):
                if self.sets_list.item(i).text() == active_set.name:
                    self.sets_list.setCurrentRow(i)
                    break
    
    def on_set_selected(self, row):
        """
        Handle selection of an instruction set.
        
        Parameters
        ----------
        row : int
            Selected row index.
        """
        if row < 0 or not self.manager:
            # Clear editors
            self.vocabulary_edit.clear()
            self.instructions_edit.clear()
            return
        
        # Get selected set
        set_name = self.sets_list.item(row).text()
        
        # Find corresponding set
        for instruction_set in self.manager.get_all_sets():
            if instruction_set.name == set_name:
                # Update editors
                self.vocabulary_edit.setPlainText("\n".join(instruction_set.vocabulary))
                self.instructions_edit.setPlainText("\n".join(instruction_set.instructions))
                
                # Update language selection
                language_index = 0  # Default to auto-detect
                if instruction_set.language:
                    for i in range(self.language_combo.count()):
                        if self.language_combo.itemData(i) == instruction_set.language:
                            language_index = i
                            break
                self.language_combo.setCurrentIndex(language_index)
                
                # Update model selection
                model_index = 0  # Default to first model
                for i in range(self.model_combo.count()):
                    if self.model_combo.itemData(i) == instruction_set.model:
                        model_index = i
                        break
                self.model_combo.setCurrentIndex(model_index)
                break
    
    def on_add_set(self):
        """Handle adding a new instruction set."""
        name, ok = QInputDialog.getText(
            self,
            AppLabels.INSTRUCTION_SETS_NEW_INSTRUCTION_SET_TITLE,
            AppLabels.INSTRUCTION_SETS_NEW_INSTRUCTION_SET_PROMPT
        )
        
        if ok and name:
            # Check if name already exists
            for i in range(self.sets_list.count()):
                if self.sets_list.item(i).text() == name:
                    SimpleMessageDialog.show_message(
                        self,
                        AppLabels.INSTRUCTION_SETS_NAME_EXISTS_TITLE,
                        AppLabels.INSTRUCTION_SETS_NAME_EXISTS_MESSAGE.format(name),
                        SimpleMessageDialog.WARNING
                    )
                    return
            
            # Create new set
            if self.manager.create_set(name):
                # Add to list
                self.sets_list.addItem(name)
                
                # Select new item
                for i in range(self.sets_list.count()):
                    if self.sets_list.item(i).text() == name:
                        self.sets_list.setCurrentRow(i)
                        break
    
    def on_rename_set(self):
        """Handle renaming an instruction set."""
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        old_name = self.sets_list.item(row).text()
        
        new_name, ok = QInputDialog.getText(
            self,
            AppLabels.INSTRUCTION_SETS_RENAME_INSTRUCTION_SET_TITLE,
            AppLabels.INSTRUCTION_SETS_RENAME_INSTRUCTION_SET_PROMPT,
            QLineEdit.EchoMode.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Check if name already exists
            for i in range(self.sets_list.count()):
                if i != row and self.sets_list.item(i).text() == new_name:
                    SimpleMessageDialog.show_message(
                        self,
                        AppLabels.INSTRUCTION_SETS_NAME_EXISTS_TITLE,
                        AppLabels.INSTRUCTION_SETS_NAME_EXISTS_MESSAGE.format(new_name),
                        SimpleMessageDialog.WARNING
                    )
                    return
            
            # Rename set
            if self.manager.rename_set(old_name, new_name):
                # Update list item
                self.sets_list.item(row).setText(new_name)
    
    def on_delete_set(self):
        """Handle deleting an instruction set."""
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        name = self.sets_list.item(row).text()
        
        # Confirm deletion
        confirm = SimpleMessageDialog.show_confirmation(
            self,
            AppLabels.INSTRUCTION_SETS_CONFIRM_DELETION_TITLE,
            AppLabels.INSTRUCTION_SETS_CONFIRM_DELETION_MESSAGE.format(name),
            False
        )
        
        if confirm:
            # Delete set
            if self.manager.delete_set(name):
                # Remove from list
                self.sets_list.takeItem(row)
                
                # Select next item
                if self.sets_list.count() > 0:
                    next_row = min(row, self.sets_list.count() - 1)
                    self.sets_list.setCurrentRow(next_row)
    
    def on_save_changes(self):
        """Handle saving changes to the current instruction set."""
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        name = self.sets_list.item(row).text()
        
        # Get edited values
        vocabulary = self.vocabulary_edit.toPlainText().strip().split("\n")
        instructions = self.instructions_edit.toPlainText().strip().split("\n")
        
        # Filter empty lines
        vocabulary = [v for v in vocabulary if v]
        instructions = [i for i in instructions if i]
        
        # Get language and model settings
        language = self.language_combo.currentData()
        model = self.model_combo.currentData()
        
        # Update set
        self.manager.update_set(name, vocabulary, instructions, language, model)
        
        # Show confirmation
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_CHANGES_SAVED_TITLE,
            AppLabels.INSTRUCTION_SETS_CHANGES_SAVED_MESSAGE.format(name),
            SimpleMessageDialog.INFO
        )
    
    def on_activate_set(self):
        """Handle activating the selected instruction set."""
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        name = self.sets_list.item(row).text()
        
        # Activate set
        self.manager.set_active(name)
        
        # Show confirmation
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_SET_ACTIVATED_TITLE,
            AppLabels.INSTRUCTION_SETS_SET_ACTIVATED_MESSAGE.format(name),
            SimpleMessageDialog.INFO
        )
    
    def get_manager(self):
        """
        Get the instruction set manager.
        
        Returns
        -------
        GUIInstructionSetManager
            The instruction set manager.
        """
        return self.manager

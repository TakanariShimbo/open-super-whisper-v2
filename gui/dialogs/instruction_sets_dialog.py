"""
Instruction Sets Dialog

This module provides a dialog for managing instruction sets and custom vocabulary.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QDialogButtonBox, QListWidget, QSplitter,
    QLineEdit, QInputDialog, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

from gui.resources.labels import AppLabels
from gui.dialogs.simple_message_dialog import SimpleMessageDialog

# Import core instruction sets
from core.instructions import InstructionSetManager, InstructionSet


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
    
    def create_set(self, name, vocabulary=None, instructions=None):
        """Create a new instruction set."""
        result = self.core_manager.create_set(name, vocabulary, instructions)
        self.save_to_settings()
        return result
    
    def update_set(self, name, vocabulary=None, instructions=None):
        """Update an existing instruction set."""
        result = self.core_manager.update_set(name, vocabulary, instructions)
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
        self.setWindowTitle(AppLabels.DIALOG_INSTRUCTION_SETS_TITLE)
        self.setMinimumSize(700, 500)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create splitter for list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - List of instruction sets
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # List selection label
        list_label = QLabel("Instruction Sets:")
        left_layout.addWidget(list_label)
        
        # Instruction sets list
        self.sets_list = QListWidget()
        self.sets_list.currentRowChanged.connect(self.on_set_selected)
        left_layout.addWidget(self.sets_list)
        
        # Buttons for managing sets
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("New")
        self.add_button.clicked.connect(self.on_add_set)
        
        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.on_rename_set)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete_set)
        
        self.activate_button = QPushButton("Activate")
        self.activate_button.clicked.connect(self.on_activate_set)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.rename_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.activate_button)
        left_layout.addLayout(buttons_layout)
        
        # Right side - Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tab widget for vocabulary and instructions
        self.tab_widget = QTabWidget()
        
        # Vocabulary tab
        vocab_tab = QWidget()
        vocab_layout = QVBoxLayout(vocab_tab)
        
        vocab_label = QLabel("Custom Vocabulary:")
        vocab_layout.addWidget(vocab_label)
        
        vocab_help = QLabel(
            "Enter words or phrases to improve transcription accuracy. "
            "One item per line."
        )
        vocab_help.setWordWrap(True)
        vocab_layout.addWidget(vocab_help)
        
        self.vocabulary_edit = QTextEdit()
        vocab_layout.addWidget(self.vocabulary_edit)
        
        # Instructions tab
        instr_tab = QWidget()
        instr_layout = QVBoxLayout(instr_tab)
        
        instr_label = QLabel("System Instructions:")
        instr_layout.addWidget(instr_label)
        
        instr_help = QLabel(
            "Enter system instructions to control transcription behavior. "
            "One instruction per line."
        )
        instr_help.setWordWrap(True)
        instr_layout.addWidget(instr_help)
        
        self.instructions_edit = QTextEdit()
        instr_layout.addWidget(self.instructions_edit)
        
        # Add tabs
        self.tab_widget.addTab(vocab_tab, "Vocabulary")
        self.tab_widget.addTab(instr_tab, "Instructions")
        
        right_layout.addWidget(self.tab_widget)
        
        
        # Save changes button - style consistent with other buttons
        self.save_button = QPushButton("Save")
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
                break
    
    def on_add_set(self):
        """Handle adding a new instruction set."""
        name, ok = QInputDialog.getText(
            self,
            "New Instruction Set",
            "Enter a name for the new instruction set:"
        )
        
        if ok and name:
            # Check if name already exists
            for i in range(self.sets_list.count()):
                if self.sets_list.item(i).text() == name:
                    SimpleMessageDialog.show_message(
                        self,
                        "Name Exists",
                        f"An instruction set with the name '{name}' already exists.",
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
            "Rename Instruction Set",
            "Enter a new name for the instruction set:",
            QLineEdit.EchoMode.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Check if name already exists
            for i in range(self.sets_list.count()):
                if i != row and self.sets_list.item(i).text() == new_name:
                    SimpleMessageDialog.show_message(
                        self,
                        "Name Exists",
                        f"An instruction set with the name '{new_name}' already exists.",
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
            "Confirm Deletion",
            f"Are you sure you want to delete the instruction set '{name}'?",
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
        
        # Update set
        self.manager.update_set(name, vocabulary, instructions)
        
        # Show confirmation
        SimpleMessageDialog.show_message(
            self,
            "Changes Saved",
            f"Changes to instruction set '{name}' have been saved.",
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
            "Set Activated",
            f"Instruction set '{name}' has been activated.",
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

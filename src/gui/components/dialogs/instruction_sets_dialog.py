"""
Instruction Sets Dialog Module

This module provides a dialog for managing instruction sets for transcription,
including vocabulary and system instructions.
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout, QTabWidget,
    QPushButton, QLineEdit, QLabel, QListWidget, QTextEdit, QMessageBox,
    QInputDialog, QApplication, QFrame, QSplitter, QWidget, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from src.gui.resources.labels import AppLabels
from src.core.instruction_sets import InstructionSetManager, InstructionSet
from src.gui.components.dialogs.simple_message_dialog import SimpleMessageDialog


class InstructionSetsDialog(QDialog):
    """
    Dialog for managing instruction sets for transcription.
    
    This dialog allows users to create, edit, rename, and delete instruction
    sets containing custom vocabulary and system instructions.
    """
    
    # Signals
    instruction_sets_updated = pyqtSignal(InstructionSetManager)
    
    def __init__(self, parent=None, manager=None):
        """
        Initialize the InstructionSetsDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget, by default None.
        manager : InstructionSetManager, optional
            The instruction set manager to use, by default None.
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.INSTRUCTION_SETS_DIALOG_TITLE)
        self.setMinimumSize(700, 500)
        
        # Store the manager
        if manager:
            # Create a copy to avoid modifying the original until accepted
            self.manager = InstructionSetManager(manager.settings)
            for instruction_set in manager.get_all_sets():
                self.manager.create_set(
                    instruction_set.name,
                    instruction_set.vocabulary,
                    instruction_set.instructions
                )
            self.manager.active_set_name = manager.active_set_name
        else:
            # Create a new manager if none was provided
            self.manager = InstructionSetManager(parent.settings)
            self.manager.load_from_settings()
        
        # Current selection
        self.current_set_name = self.manager.active_set_name
        
        # Set up UI
        self.init_ui()
        
        # Update UI with current data
        self.update_sets_list()
        self.update_edit_panel()
    
    def init_ui(self):
        """
        Initialize the user interface.
        
        This method sets up the dialog layout and widgets.
        """
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create dialog frame
        dialog_frame = QFrame(self)
        layout = QVBoxLayout(dialog_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Dialog title
        title_label = QLabel(AppLabels.INSTRUCTION_SETS_DIALOG_TITLE)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Create splitter for list and edit panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - sets list
        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(5)
        
        # Sets list label
        list_label = QLabel(AppLabels.INSTRUCTION_SETS_LIST_LABEL)
        list_layout.addWidget(list_label)
        
        # Sets list
        self.sets_list = QListWidget()
        self.sets_list.setMinimumWidth(150)
        self.sets_list.currentTextChanged.connect(self.on_set_selected)
        list_layout.addWidget(self.sets_list)
        
        # Sets list buttons
        list_buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton(AppLabels.INSTRUCTION_SETS_ADD_BUTTON)
        self.add_button.clicked.connect(self.on_add_set)
        
        self.rename_button = QPushButton(AppLabels.INSTRUCTION_SETS_RENAME_BUTTON)
        self.rename_button.clicked.connect(self.on_rename_set)
        
        self.remove_button = QPushButton(AppLabels.INSTRUCTION_SETS_REMOVE_BUTTON)
        self.remove_button.clicked.connect(self.on_remove_set)
        
        list_buttons_layout.addWidget(self.add_button)
        list_buttons_layout.addWidget(self.rename_button)
        list_buttons_layout.addWidget(self.remove_button)
        
        list_layout.addLayout(list_buttons_layout)
        
        # Activate button
        self.activate_button = QPushButton(AppLabels.INSTRUCTION_SETS_ACTIVATE_BUTTON)
        self.activate_button.clicked.connect(self.on_activate_set)
        list_layout.addWidget(self.activate_button)
        
        # Right panel - edit panel
        self.edit_panel = QWidget()
        edit_layout = QVBoxLayout(self.edit_panel)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(10)
        
        # Edit panel label
        edit_label = QLabel(AppLabels.INSTRUCTION_SETS_EDIT_SECTION_TITLE)
        edit_layout.addWidget(edit_label)
        
        # Tab widget for vocabulary and instructions
        self.tab_widget = QTabWidget()
        
        # Vocabulary tab
        vocabulary_tab = QWidget()
        vocabulary_layout = QVBoxLayout(vocabulary_tab)
        
        vocabulary_info = QLabel(AppLabels.VOCABULARY_SECTION_TITLE)
        vocabulary_layout.addWidget(vocabulary_info)
        
        self.vocabulary_text = QTextEdit()
        self.vocabulary_text.setPlaceholderText(AppLabels.VOCABULARY_PLACEHOLDER)
        vocabulary_layout.addWidget(self.vocabulary_text)
        
        # Instructions tab
        instructions_tab = QWidget()
        instructions_layout = QVBoxLayout(instructions_tab)
        
        instructions_info = QLabel(AppLabels.INSTRUCTIONS_INFO)
        instructions_info.setWordWrap(True)
        instructions_layout.addWidget(instructions_info)
        
        self.instructions_text = QTextEdit()
        self.instructions_text.setPlaceholderText(AppLabels.SYSTEM_INSTRUCTIONS_DIALOG_PLACEHOLDER)
        instructions_layout.addWidget(self.instructions_text)
        
        # Add tabs
        self.tab_widget.addTab(vocabulary_tab, "Vocabulary")
        self.tab_widget.addTab(instructions_tab, "Instructions")
        
        edit_layout.addWidget(self.tab_widget)
        
        # Add panels to splitter
        splitter.addWidget(list_panel)
        splitter.addWidget(self.edit_panel)
        splitter.setSizes([200, 500])  # Initial sizes
        
        layout.addWidget(splitter)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton(AppLabels.APPLY_BUTTON)
        self.apply_button.clicked.connect(self.on_apply)
        
        self.save_button = QPushButton(AppLabels.SAVE_BUTTON)
        self.save_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(dialog_frame)
    
    def update_sets_list(self):
        """
        Update the instruction sets list.
        
        This method refreshes the list of instruction sets with the
        current data from the manager.
        """
        self.sets_list.clear()
        
        # Add all sets
        for instruction_set in self.manager.get_all_sets():
            display_name = instruction_set.name
            
            # Mark active set
            if instruction_set.name == self.manager.active_set_name:
                display_name = f"{display_name} {AppLabels.INSTRUCTION_SETS_ACTIVE_MARK}"
            
            self.sets_list.addItem(display_name)
            
            # Select the current set
            if instruction_set.name == self.current_set_name:
                self.sets_list.setCurrentRow(self.sets_list.count() - 1)
    
    def update_edit_panel(self):
        """
        Update the edit panel with the selected set's data.
        
        This method populates the vocabulary and instructions text
        fields with the data from the currently selected set.
        """
        if not self.current_set_name or self.current_set_name not in self.manager.sets:
            # Clear panels if no set is selected
            self.vocabulary_text.clear()
            self.instructions_text.clear()
            self.edit_panel.setEnabled(False)
            self.activate_button.setEnabled(False)
            return
        
        # Enable panels
        self.edit_panel.setEnabled(True)
        
        # Enable/disable activate button based on current selection
        self.activate_button.setEnabled(self.current_set_name != self.manager.active_set_name)
        
        # Get selected set
        instruction_set = self.manager.sets[self.current_set_name]
        
        # Update vocabulary text
        self.vocabulary_text.clear()
        self.vocabulary_text.setPlainText("\n".join(instruction_set.vocabulary))
        
        # Update instructions text
        self.instructions_text.clear()
        self.instructions_text.setPlainText("\n".join(instruction_set.instructions))
    
    def on_set_selected(self, text):
        """
        Handle set selection changed.
        
        Parameters
        ----------
        text : str
            The text of the selected item.
        """
        # Save current edits
        self.save_current_edits()
        
        # Extract the real name (remove active mark if present)
        if text:
            self.current_set_name = text.replace(f" {AppLabels.INSTRUCTION_SETS_ACTIVE_MARK}", "")
        else:
            self.current_set_name = None
        
        # Update edit panel
        self.update_edit_panel()
    
    def save_current_edits(self):
        """
        Save the current edits to the selected set.
        
        This method saves any changes made in the vocabulary and
        instructions text fields to the currently selected set.
        """
        if not self.current_set_name or self.current_set_name not in self.manager.sets:
            return
        
        # Get vocabulary lines and filter out empty ones
        vocabulary = self.vocabulary_text.toPlainText().splitlines()
        vocabulary = [line.strip() for line in vocabulary if line.strip()]
        
        # Get instructions lines and filter out empty ones
        instructions = self.instructions_text.toPlainText().splitlines()
        instructions = [line.strip() for line in instructions if line.strip()]
        
        # Update the set
        self.manager.update_set(self.current_set_name, vocabulary, instructions)
    
    def on_add_set(self):
        """
        Handle add set button click.
        
        This method displays a dialog to create a new instruction set.
        """
        # Save current edits
        self.save_current_edits()
        
        # Get new set name
        name, ok = QInputDialog.getText(
            self,
            AppLabels.INSTRUCTION_SETS_NEW_TITLE,
            AppLabels.INSTRUCTION_SETS_NEW_PROMPT
        )
        
        if ok and name:
            # Check if name already exists
            if name in self.manager.sets:
                SimpleMessageDialog.show_message(
                    self,
                    AppLabels.WARNING_TITLE,
                    f"A set named '{name}' already exists.",
                    SimpleMessageDialog.WARNING
                )
                return
            
            # Create new set
            self.manager.create_set(name)
            
            # Update UI
            self.current_set_name = name
            self.update_sets_list()
            self.update_edit_panel()
    
    def on_rename_set(self):
        """
        Handle rename set button click.
        
        This method displays a dialog to rename the selected instruction set.
        """
        if not self.current_set_name:
            return
        
        # Save current edits
        self.save_current_edits()
        
        # Get new name
        new_name, ok = QInputDialog.getText(
            self,
            AppLabels.INSTRUCTION_SETS_RENAME_TITLE,
            AppLabels.INSTRUCTION_SETS_RENAME_PROMPT,
            text=self.current_set_name
        )
        
        if ok and new_name and new_name != self.current_set_name:
            # Check if name already exists
            if new_name in self.manager.sets:
                SimpleMessageDialog.show_message(
                    self,
                    AppLabels.WARNING_TITLE,
                    f"A set named '{new_name}' already exists.",
                    SimpleMessageDialog.WARNING
                )
                return
            
            # Rename set
            self.manager.rename_set(self.current_set_name, new_name)
            
            # Update current selection
            self.current_set_name = new_name
            
            # Update UI
            self.update_sets_list()
            self.update_edit_panel()
    
    def on_remove_set(self):
        """
        Handle remove set button click.
        
        This method displays a confirmation dialog to delete the
        selected instruction set.
        """
        if not self.current_set_name:
            return
        
        # Don't allow deleting the last set
        if len(self.manager.sets) <= 1:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.WARNING_TITLE,
                AppLabels.INSTRUCTION_SETS_LAST_SET_ERROR,
                SimpleMessageDialog.WARNING
            )
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            AppLabels.INSTRUCTION_SETS_REMOVE_TITLE,
            AppLabels.INSTRUCTION_SETS_REMOVE_CONFIRM.format(self.current_set_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Delete set
            old_name = self.current_set_name
            self.manager.delete_set(old_name)
            
            # Update current selection
            self.current_set_name = self.manager.active_set_name
            
            # Update UI
            self.update_sets_list()
            self.update_edit_panel()
    
    def on_activate_set(self):
        """
        Handle activate set button click.
        
        This method activates the selected instruction set.
        """
        if not self.current_set_name:
            return
        
        # Save current edits
        self.save_current_edits()
        
        # Activate set
        self.manager.set_active(self.current_set_name)
        
        # Update UI
        self.update_sets_list()
        self.update_edit_panel()
    
    def on_apply(self):
        """
        Handle apply button click.
        
        This method saves the current edits and emits the
        instruction_sets_updated signal.
        """
        # Save current edits
        self.save_current_edits()
        
        # Save to settings
        self.manager.save_to_settings()
        
        # Emit signal
        self.instruction_sets_updated.emit(self.manager)
        
        # Show success message
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_UPDATED_TITLE,
            AppLabels.INSTRUCTION_SETS_UPDATED_SUCCESS,
            SimpleMessageDialog.INFO
        )
    
    def accept(self):
        """
        Handle dialog acceptance.
        
        This method is called when the Save button is clicked.
        It saves the current edits, saves to settings, emits the
        instruction_sets_updated signal, and closes the dialog.
        """
        # Save current edits
        self.save_current_edits()
        
        # Save to settings
        self.manager.save_to_settings()
        
        # Emit signal
        self.instruction_sets_updated.emit(self.manager)
        
        # Close dialog
        super().accept()
    
    def get_manager(self):
        """
        Get the instruction set manager.
        
        Returns
        -------
        InstructionSetManager
            The instruction set manager.
        """
        return self.manager


# For standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    from PyQt6.QtCore import QSettings
    settings = QSettings("TestApp", "TestApp")
    
    # Create manager and add some test sets
    manager = InstructionSetManager(settings)
    manager.create_set("Default", ["word1", "word2"], ["Ignore filler words"])
    manager.create_set("Technical", ["API", "SDK", "REST"], ["Format as paragraphs"])
    manager.set_active("Default")
    
    # Create and show the dialog
    dialog = InstructionSetsDialog(None, manager)
    dialog.instruction_sets_updated.connect(lambda m: print(f"Sets updated: {m.get_all_sets()}"))
    result = dialog.exec()
    
    # Show the result
    if result == QDialog.DialogCode.Accepted:
        print("Dialog accepted")
        print(f"Active set: {dialog.get_manager().active_set_name}")
    else:
        print("Dialog rejected")
    
    sys.exit()

"""
Instruction Sets Dialog

This module provides a dialog for managing instruction sets, custom vocabulary, system instructions,
and LLM settings with thread-safe implementation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QDialogButtonBox, QListWidget, QSplitter,
    QLineEdit, QInputDialog, QTabWidget, QWidget,
    QFormLayout, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSlot

from gui.resources.labels import AppLabels
from gui.dialogs.simple_message_dialog import SimpleMessageDialog
from gui.dialogs.hotkey_dialog import HotkeyDialog
from gui.thread_management.hotkey_bridge import HotkeyBridge

from core.utils.instruction_set import InstructionSet
from core.utils.instruction_manager import InstructionManager

from core.stt.stt_lang_model_manager import STTLangModelManager
from core.stt.stt_model_manager import STTModelManager
from core.llm.llm_model_manager import LLMModelManager


class GUIInstructionSetManager:
    """
    GUI wrapper for the core InstructionSetManager.
    
    This class wraps the core InstructionSetManager to provide GUI-specific
    functionality, such as QSettings integration.
    
    Thread Safety:
    --------------
    Uses thread_manager when provided to ensure thread-safe operations for
    heavy I/O operations like saving to QSettings.
    """
    
    def __init__(self, settings: QSettings, thread_manager=None):
        """
        Initialize the GUI instruction set manager.
        
        Parameters
        ----------
        settings : QSettings
            Settings object to store/retrieve data.
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operations
        """
        self.settings = settings
        self.core_manager = InstructionManager()
        self.thread_manager = thread_manager
        self._selected_set_name = ""  # Tracks currently selected set name for dropdown
        self.load_from_settings()
    
    def get_all_sets(self):
        """Get all instruction sets."""
        return self.core_manager.get_all_sets()
    
    def create_set(self, name, vocabulary=None, instructions=None, stt_language=None, stt_model=None,
                  llm_enabled=False, llm_model=None, llm_instructions=None, 
                  llm_clipboard_text_enabled=False, llm_clipboard_image_enabled=False, hotkey=""):
        """Create a new instruction set."""
        instruction_set = InstructionSet(
            name, vocabulary, instructions, stt_language, stt_model,
            llm_enabled, llm_model, llm_instructions, 
            llm_clipboard_text_enabled, llm_clipboard_image_enabled, hotkey
        )
        result = self.core_manager.add_set(instruction_set)
        self.save_to_settings()
        return result
    
    def update_set(self, name, vocabulary=None, instructions=None, stt_language=None, stt_model=None,
                  llm_enabled=None, llm_model=None, llm_instructions=None, 
                  llm_clipboard_text_enabled=None, llm_clipboard_image_enabled=None, hotkey=None):
        """Update an existing instruction set."""
        instruction_set = self.core_manager.find_set_by_name(name)
        if not instruction_set:
            return False
        instruction_set.update(
            vocabulary, instructions, stt_language, stt_model,
            llm_enabled, llm_model, llm_instructions, llm_clipboard_text_enabled,
            llm_clipboard_image_enabled, hotkey
        )
        self.save_to_settings()
        return True
    
    def delete_set(self, name):
        """Delete an instruction set."""
        result = self.core_manager.delete_set(name)
        
        # If the deleted set was the selected set, clear the selection
        if name == self._selected_set_name:
            # Find a new set to select
            sets = self.get_all_sets()
            if sets:
                self._selected_set_name = sets[0].name
            else:
                self._selected_set_name = ""
        
        self.save_to_settings()
        return result
    
    def set_selected(self, name):
        """
        Set the selected instruction set for the dropdown.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select.
            
        Returns
        -------
        bool
            True if successful, False if name doesn't exist.
        """
        # Check if set exists
        if not self.core_manager.find_set_by_name(name):
            return False
        
        # Set selected set name
        self._selected_set_name = name
        self.save_to_settings()
        return True
    
    def get_selected_set_name(self):
        """
        Get the name of the currently selected instruction set.
        
        Returns
        -------
        str
            Name of the selected instruction set, or empty string if none selected.
        """
        return self._selected_set_name
    
    def get_selected_set(self):
        """
        Get the currently selected instruction set object.
        
        Returns
        -------
        InstructionSet or None
            The selected instruction set, or None if none selected.
        """
        if not self._selected_set_name:
            return None
        return self.core_manager.find_set_by_name(self._selected_set_name)
    
    def rename_set(self, old_name, new_name):
        """Rename an instruction set."""
        result = self.core_manager.rename_set(old_name, new_name)
        
        # Update selected set name if it was renamed
        if old_name == self._selected_set_name:
            self._selected_set_name = new_name
            
        self.save_to_settings()
        return result
    
    def update_set_hotkey(self, name, hotkey):
        """Update the hotkey for an instruction set."""
        instruction_set = self.core_manager.find_set_by_name(name)
        if not instruction_set:
            return False
        instruction_set.hotkey = hotkey
        self.save_to_settings()
        return True
    
    def get_set_by_hotkey(self, hotkey):
        """Get an instruction set by its hotkey."""
        return self.core_manager.find_set_by_hotkey(hotkey)
    
    def get_set_by_name(self, name):
        """
        Get an instruction set by its name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to retrieve.
            
        Returns
        -------
        Optional[InstructionSet]
            The instruction set with the given name, or None if not found.
        """
        return self.core_manager.find_set_by_name(name)
    
    def save_to_settings(self):
        """
        Save all instruction sets to settings.
        
        Uses ThreadManager for thread-safe operation if available.
        """
        def save_operation():
            data = self.core_manager.export_to_dict()
            
            # Save to QSettings
            prefix = "InstructionSets"
            self.settings.beginGroup(prefix)
            
            # Remove any existing sets first
            self.settings.remove("")
            
            # Save selected set
            self.settings.setValue("SelectedSet", self._selected_set_name)
            
            # Save sets
            self.settings.setValue("Sets", data["sets"])
            
            self.settings.endGroup()
            self.settings.sync()
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_worker_thread(
                "save_instruction_sets",
                save_operation
            )
        else:
            # Synchronous save
            save_operation()
    
    def load_from_settings(self):
        """
        Load instruction sets from settings.
        
        Uses ThreadManager for thread-safe operation if available.
        """
        def load_operation():
            # Get from QSettings
            prefix = "InstructionSets"
            self.settings.beginGroup(prefix)
            
            # Load selected set
            selected_set = self.settings.value("SelectedSet", "")
            
            # No longer need to check for old "ActiveSet" value
            
            # Load sets
            sets = self.settings.value("Sets", [])
            
            self.settings.endGroup()
            
            # Convert to dict for core manager
            data = {
                "sets": sets
            }
            
            # Return data and selected set
            return data, selected_set
            
        def finish_loading(result):
            # Unpack result
            data, selected_set = result
            
            # Load into core manager
            self.core_manager.import_from_dict(data)
            
            # Set selected set if it exists
            if selected_set and self.core_manager.find_set_by_name(selected_set):
                self._selected_set_name = selected_set
            elif self.core_manager.get_all_sets():
                # Default to first set if selected set doesn't exist
                self._selected_set_name = self.core_manager.get_all_sets()[0].name
            else:
                self._selected_set_name = ""
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_worker_thread(
                "load_instruction_sets",
                load_operation,
                callback=finish_loading
            )
        else:
            # Synchronous load
            result = load_operation()
            finish_loading(result)


class InstructionSetsDialog(QDialog):
    """
    Dialog for managing instruction sets.
    
    This dialog allows users to create, edit, delete, and select
    instruction sets with custom vocabulary, system instructions,
    language/model selection, and LLM (Large Language Model) settings.
    It provides a comprehensive interface for customizing how transcription
    and analysis are performed.
    
    Thread Safety:
    --------------
    Operations that might involve I/O or background processing use ThreadManager
    when provided to ensure thread-safe execution. UI updates use
    ThreadManager.run_in_main_thread to ensure they happen on the main/UI thread.
    """
    
    def __init__(self, parent=None, manager=None, hotkey_manager=None, thread_manager=None):
        """
        Initialize the InstructionSetsDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        manager : GUIInstructionSetManager, optional
            Instruction set manager, by default None
        hotkey_manager : HotkeyManager, optional
            Hotkey manager for temporarily disabling hotkeys during dialog, by default None
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operations
        """
        super().__init__(parent)
        
        self.manager = manager
        self.hotkey_manager = hotkey_manager
        self.thread_manager = thread_manager
        
        # Flag to track if hotkeys were disabled
        self.hotkeys_disabled = False
        
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
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.rename_button)
        buttons_layout.addWidget(self.delete_button)
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
        main_form = QWidget()
        main_layout = QFormLayout(main_form)
        
        stt_language_label = QLabel(AppLabels.INSTRUCTION_SETS_LANGUAGE_LABEL)
        self.stt_language_combo = QComboBox()
        
        # Add language options from STTLangModelManager
        stt_languages = STTLangModelManager.get_available_languages()
        for stt_language in stt_languages:
            self.stt_language_combo.addItem(stt_language.name, stt_language.code)
            # Add tooltip
            self.stt_language_combo.setItemData(
                self.stt_language_combo.count() - 1,
                f"{stt_language.name} ({stt_language.code})",
                Qt.ItemDataRole.ToolTipRole
            )
        
        main_layout.addRow(stt_language_label, self.stt_language_combo)
        
        # Model selection
        stt_model_label = QLabel(AppLabels.INSTRUCTION_SETS_MODEL_LABEL)
        self.stt_model_combo = QComboBox()
        
        # Add model options from WhisperModelManager
        stt_models = STTModelManager.get_available_models()
        for stt_model in stt_models:
            self.stt_model_combo.addItem(stt_model.name, stt_model.id)
            # Add tooltip
            self.stt_model_combo.setItemData(
                self.stt_model_combo.count() - 1,
                stt_model.description,
                Qt.ItemDataRole.ToolTipRole
            )
        
        main_layout.addRow(stt_model_label, self.stt_model_combo)
        
        # Add hotkey selection
        hotkey_label = QLabel(AppLabels.INSTRUCTION_SETS_HOTKEY_LABEL)
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.setPlaceholderText(AppLabels.INSTRUCTION_SETS_HOTKEY_PLACEHOLDER)

        hotkey_button = QPushButton(AppLabels.INSTRUCTION_SETS_SET_HOTKEY_BUTTON)
        hotkey_button.clicked.connect(self.show_hotkey_dialog)
        
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addWidget(hotkey_button)
        
        main_layout.addRow(hotkey_label, hotkey_layout)

        # LLM enable/disable
        llm_enabled_label = QLabel(AppLabels.INSTRUCTION_SETS_LLM_TOGGLE_LABEL)
        self.llm_enabled_checkbox = QCheckBox()
        self.llm_enabled_checkbox.stateChanged.connect(self.on_llm_enabled_changed)
        main_layout.addRow(llm_enabled_label, self.llm_enabled_checkbox)
        
        # LLM model selection
        llm_model_label = QLabel(AppLabels.INSTRUCTION_SETS_LLM_MODEL_LABEL)
        self.llm_model_combo = QComboBox()
        
        # Add model options from LLMModelManager
        llm_models = LLMModelManager.get_available_models()
        for model in llm_models:
            self.llm_model_combo.addItem(model.name, model.id)
            # Add tooltip
            self.llm_model_combo.setItemData(
                self.llm_model_combo.count() - 1,
                model.description,
                Qt.ItemDataRole.ToolTipRole
            )
        
        # Connect signal to update UI when LLM model selection changes
        self.llm_model_combo.currentIndexChanged.connect(self.on_llm_model_changed)
        
        main_layout.addRow(llm_model_label, self.llm_model_combo)
        
        # Add checkbox for clipboard text
        self.llm_clipboard_text_checkbox = QCheckBox(AppLabels.INSTRUCTION_SETS_LLM_CLIPBOARD_TEXT_LABEL)
        self.llm_clipboard_text_checkbox.setToolTip(AppLabels.INSTRUCTION_SETS_LLM_CLIPBOARD_TEXT_TOOLTIP)
        main_layout.addRow(AppLabels.INSTRUCTION_SETS_LLM_CONTEXT_LABEL, self.llm_clipboard_text_checkbox)
        
        # Add checkbox for clipboard image
        self.llm_clipboard_image_checkbox = QCheckBox(AppLabels.INSTRUCTION_SETS_LLM_CLIPBOARD_IMAGE_LABEL)
        self.llm_clipboard_image_checkbox.setToolTip(AppLabels.INSTRUCTION_SETS_LLM_CLIPBOARD_IMAGE_TOOLTIP)
        main_layout.addRow("", self.llm_clipboard_image_checkbox)

        settings_layout.addWidget(main_form)
        
        # Add spacer
        settings_layout.addStretch(1)
        
        # LLM Instructions tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        llm_label = QLabel(AppLabels.INSTRUCTION_SETS_LLM_TAB_NAME)
        llm_layout.addWidget(llm_label)
        
        llm_help = QLabel(AppLabels.INSTRUCTION_SETS_LLM_HELP)
        llm_help.setWordWrap(True)
        llm_layout.addWidget(llm_help)
        
        # LLM instructions        
        self.llm_instructions_edit = QTextEdit()
        self.llm_instructions_edit.setEnabled(False)  # Disabled by default
        llm_layout.addWidget(self.llm_instructions_edit)
        
        # Add tabs to the tab widget in specified order
        self.tab_widget.addTab(vocab_tab, AppLabels.INSTRUCTION_SETS_VOCABULARY_TAB_NAME)
        self.tab_widget.addTab(instr_tab, AppLabels.INSTRUCTION_SETS_INSTRUCTIONS_TAB_NAME)
        self.tab_widget.addTab(llm_tab, AppLabels.INSTRUCTION_SETS_LLM_TAB_NAME)
        self.tab_widget.addTab(settings_tab, AppLabels.INSTRUCTION_SETS_SETTINGS_TAB_NAME)
        
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
        
        # Set initial state of LLM-related UI components
        # By default, these should be disabled unless LLM is enabled
        self.llm_model_combo.setEnabled(False)
        self.llm_clipboard_text_checkbox.setEnabled(False)
        self.llm_clipboard_image_checkbox.setEnabled(False)
        # LLM tab's contents will be enabled/disabled when a set is selected
    
    def load_instruction_sets(self):
        """
        Load instruction sets into the UI.
        
        Uses thread_manager to ensure UI updates happen on the main thread
        if thread_manager is provided.
        """
        if not self.manager:
            return
            
        def update_ui():
            # Clear list
            self.sets_list.clear()
            
            # Add sets
            for instruction_set in self.manager.get_all_sets():
                self.sets_list.addItem(instruction_set.name)
            
            # Select the current set
            selected_set_name = self.manager.get_selected_set_name()
            if selected_set_name:
                for i in range(self.sets_list.count()):
                    if self.sets_list.item(i).text() == selected_set_name:
                        self.sets_list.setCurrentRow(i)
                        break
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_main_thread(update_ui)
        else:
            # Synchronous update
            update_ui()
    
    @pyqtSlot(int)
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
            self.llm_instructions_edit.clear()
            self.llm_enabled_checkbox.setChecked(False)
            self.hotkey_input.clear()
            return
        
        # Get selected set
        set_name = self.sets_list.item(row).text()
        
        # Define UI update function
        def update_ui_with_set(instruction_set):
            # Update editors
            self.vocabulary_edit.setPlainText(instruction_set.stt_vocabulary)
            self.instructions_edit.setPlainText(instruction_set.stt_instructions)
            
            # Update language selection
            language_index = 0  # Default to auto-detect
            if instruction_set.stt_language:
                for i in range(self.stt_language_combo.count()):
                    if self.stt_language_combo.itemData(i) == instruction_set.stt_language:
                        language_index = i
                        break
            self.stt_language_combo.setCurrentIndex(language_index)
            
            # Update model selection
            model_index = 0  # Default to first model
            for i in range(self.stt_model_combo.count()):
                if self.stt_model_combo.itemData(i) == instruction_set.stt_model:
                    model_index = i
                    break
            self.stt_model_combo.setCurrentIndex(model_index)
            
            # Update LLM settings
            is_llm_enabled = instruction_set.llm_enabled
            self.llm_enabled_checkbox.setChecked(is_llm_enabled)
            
            # Update LLM clipboard options
            self.llm_clipboard_text_checkbox.setChecked(instruction_set.llm_clipboard_text_enabled)
            self.llm_clipboard_image_checkbox.setChecked(instruction_set.llm_clipboard_image_enabled)
            
            # Update LLM model selection
            llm_model_index = 0  # Default to first model
            for i in range(self.llm_model_combo.count()):
                if self.llm_model_combo.itemData(i) == instruction_set.llm_model:
                    llm_model_index = i
                    break
            self.llm_model_combo.setCurrentIndex(llm_model_index)
            
            # Update LLM instructions
            self.llm_instructions_edit.setPlainText(instruction_set.llm_instructions)
            
            # Check if model supports image input
            supports_image = False
            if instruction_set.llm_model:
                supports_image = LLMModelManager.supports_image_input(instruction_set.llm_model)
            
            # Set enabled state for LLM-related UI components
            self.llm_model_combo.setEnabled(is_llm_enabled)
            self.llm_clipboard_text_checkbox.setEnabled(is_llm_enabled)
            self.llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
            self.llm_instructions_edit.setEnabled(is_llm_enabled)
            
            # Update hotkey field
            self.hotkey_input.setText(instruction_set.hotkey)
        
        # Find corresponding set
        instruction_set = None
        for set_item in self.manager.get_all_sets():
            if set_item.name == set_name:
                instruction_set = set_item
                break
                
        if instruction_set:
            # Use thread manager if available for UI update
            if self.thread_manager:
                self.thread_manager.run_in_main_thread(lambda: update_ui_with_set(instruction_set))
            else:
                # Synchronous update
                update_ui_with_set(instruction_set)
    
    def on_add_set(self):
        """
        Handle adding a new instruction set.
        
        Uses thread_manager to ensure UI updates and dialog operations happen 
        on the main thread if thread_manager is provided.
        """
        def show_input_dialog():
            name, ok = QInputDialog.getText(
                self,
                AppLabels.INSTRUCTION_SETS_NEW_INSTRUCTION_SET_TITLE,
                AppLabels.INSTRUCTION_SETS_NEW_INSTRUCTION_SET_PROMPT
            )
            
            if ok and name:
                self._process_new_set_name(name)
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_main_thread(show_input_dialog)
        else:
            # Synchronous execution
            show_input_dialog()
    
    def _process_new_set_name(self, name):
        """
        Process a new instruction set name.
        
        Parameters
        ----------
        name : str
            Name for the new instruction set.
        """
        # Check if name already exists
        for i in range(self.sets_list.count()):
            if self.sets_list.item(i).text() == name:
                self._show_name_exists_error(name)
                return
        
        # Create new set
        if self.manager.create_set(name):
            # Add to list and select
            self._update_list_after_add(name)
            
    def _update_list_after_add(self, name):
        """
        Update the list widget after adding a new instruction set.
        
        Parameters
        ----------
        name : str
            Name of the newly added instruction set.
        """
        # Add to list
        self.sets_list.addItem(name)
        
        # Select new item
        for i in range(self.sets_list.count()):
            if self.sets_list.item(i).text() == name:
                self.sets_list.setCurrentRow(i)
                break
        
        # Clear all input fields to ensure UI matches the empty state of a new instruction set
        self.vocabulary_edit.clear()
        self.instructions_edit.clear()
        self.llm_instructions_edit.clear()
        self.hotkey_input.clear()  # Explicitly clear hotkey field to fix the inheritance issue
        
        # Reset comboboxes to their default values
        self.stt_language_combo.setCurrentIndex(0)  # First option (usually "Auto-detect")
        self.stt_model_combo.setCurrentIndex(0)     # First option (default model)
        self.llm_model_combo.setCurrentIndex(0) # First option (default LLM model)
        
        # Set initial state of LLM UI components (disabled by default for new sets)
        # New sets have llm_enabled=False by default in the core manager
        is_llm_enabled = False  # New sets have LLM disabled by default
        self.llm_enabled_checkbox.setChecked(False)
        
        # Get default LLM model and check if it supports images
        default_model_id = LLMModelManager.get_default_model().id
        supports_image = LLMModelManager.supports_image_input(default_model_id)
        
        # Reset checkboxes
        self.llm_clipboard_text_checkbox.setChecked(False)
        self.llm_clipboard_image_checkbox.setChecked(False)
        
        # Set enabled states for UI components
        self.llm_model_combo.setEnabled(is_llm_enabled)
        self.llm_clipboard_text_checkbox.setEnabled(is_llm_enabled)
        self.llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
        self.llm_instructions_edit.setEnabled(is_llm_enabled)
    
    def _show_name_exists_error(self, name):
        """
        Show error message that instruction set name already exists.
        
        Parameters
        ----------
        name : str
            The duplicate name.
        """
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_NAME_EXISTS_TITLE,
            AppLabels.INSTRUCTION_SETS_NAME_EXISTS_MESSAGE.format(name),
            SimpleMessageDialog.WARNING,
            self.thread_manager
        )
    
    def on_rename_set(self):
        """
        Handle renaming an instruction set.
        
        Uses thread_manager to ensure UI updates and dialog operations happen
        on the main thread if thread_manager is provided.
        """
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        old_name = self.sets_list.item(row).text()
        
        def show_rename_dialog():
            new_name, ok = QInputDialog.getText(
                self,
                AppLabels.INSTRUCTION_SETS_RENAME_INSTRUCTION_SET_TITLE,
                AppLabels.INSTRUCTION_SETS_RENAME_INSTRUCTION_SET_PROMPT,
                QLineEdit.EchoMode.Normal,
                old_name
            )
            
            if ok and new_name and new_name != old_name:
                self._process_rename(row, old_name, new_name)
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_main_thread(show_rename_dialog)
        else:
            # Synchronous execution
            show_rename_dialog()
    
    def _process_rename(self, row, old_name, new_name):
        """
        Process renaming an instruction set.
        
        Parameters
        ----------
        row : int
            The row index of the item in the list.
        old_name : str
            The original name.
        new_name : str
            The new name.
        """
        # Check if name already exists
        for i in range(self.sets_list.count()):
            if i != row and self.sets_list.item(i).text() == new_name:
                self._show_name_exists_error(new_name)
                return
        
        # Rename set
        if self.manager.rename_set(old_name, new_name):
            # Update list item
            self.sets_list.item(row).setText(new_name)
    
    def on_delete_set(self):
        """
        Handle deleting an instruction set.
        
        Uses thread_manager to ensure UI updates and dialog operations happen
        on the main thread if thread_manager is provided.
        
        NOTE: This method was modified to fix a bug with Yes button not working
        in the confirmation dialog when using thread_manager.
        """
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        # Check if this is the last set - can't delete the last set
        if self.sets_list.count() <= 1:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.INSTRUCTION_SETS_LAST_SET_ERROR_TITLE,
                AppLabels.INSTRUCTION_SETS_LAST_SET_ERROR_MESSAGE,
                SimpleMessageDialog.WARNING,
                self.thread_manager
            )
            return
        
        name = self.sets_list.item(row).text()
        
        # Define confirmation callback that will be used for both sync and async paths
        def confirmation_callback(result):
            """Handle the confirmation dialog result"""
            if result:
                # Use thread manager to safely call _perform_delete in main thread
                if self.thread_manager:
                    self.thread_manager.run_in_main_thread(lambda: self._perform_delete(row, name))
                else:
                    self._perform_delete(row, name)
        
        # Set up confirmation dialog
        confirm_title = AppLabels.INSTRUCTION_SETS_CONFIRM_DELETION_TITLE
        confirm_message = AppLabels.INSTRUCTION_SETS_CONFIRM_DELETION_MESSAGE.format(name)
        
        # Always use the async version with callback when thread_manager is available
        if self.thread_manager:
            # Run the dialog setup in the main thread
            def show_confirmation_async():
                SimpleMessageDialog.show_confirmation_async(
                    self,
                    confirm_title,
                    confirm_message,
                    confirmation_callback,
                    False,  # default_yes=False
                    self.thread_manager
                )
            
            self.thread_manager.run_in_main_thread(show_confirmation_async)
        else:
            # Use synchronous path when thread_manager is not available
            result = SimpleMessageDialog.show_confirmation(
                self,
                confirm_title,
                confirm_message,
                False  # default_yes=False
            )
            
            # Process the result through the same callback for consistency
            confirmation_callback(result)
    
    def _perform_delete(self, row, name):
        """
        Perform the deletion of an instruction set.
        
        Parameters
        ----------
        row : int
            The row index of the item in the list.
        name : str
            The name of the instruction set to delete.
        """
        # Delete set
        result = self.manager.delete_set(name)
        
        if result:
            # Remove from list
            self.sets_list.takeItem(row)
            
            # Select next item and ensure it's properly updated in the UI
            if self.sets_list.count() > 0:
                next_row = min(row, self.sets_list.count() - 1)
                self.sets_list.setCurrentRow(next_row)
                
                # Get the selected set name
                selected_set_name = self.manager.get_selected_set_name()
                if selected_set_name:
                    for i in range(self.sets_list.count()):
                        if self.sets_list.item(i).text() == selected_set_name:
                            if i != next_row:  # Only change if it's different
                                self.sets_list.setCurrentRow(i)
                            break
        else:
            # Show error if deletion failed
            SimpleMessageDialog.show_message(
                self,
                AppLabels.INSTRUCTION_SETS_DELETION_FAILED_TITLE,
                AppLabels.INSTRUCTION_SETS_DELETION_FAILED_MESSAGE.format(name),
                SimpleMessageDialog.ERROR,
                self.thread_manager
            )
    
    def show_hotkey_dialog(self):
        """
        Show dialog to set hotkey for the selected instruction set.
        
        Uses thread_manager to ensure UI updates and dialog operations happen
        on the main thread if thread_manager is provided.
        
        Note: Hotkeys are automatically disabled/re-enabled by the HotkeyDialog class.
        """
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        set_name = self.sets_list.item(row).text()
        
        # Find current hotkey
        current_hotkey = ""
        for instruction_set in self.manager.get_all_sets():
            if instruction_set.name == set_name:
                current_hotkey = instruction_set.hotkey
                break
        
        def show_dialog():
            # Create dialog with thread manager for thread-safe operations
            # HotkeyDialog will handle disabling/re-enabling hotkeys automatically
            dialog = HotkeyDialog(self, current_hotkey, self.thread_manager)
            result = dialog.exec()
            
            if result:
                new_hotkey = dialog.get_hotkey()
                if new_hotkey:
                    self._process_hotkey_change(set_name, new_hotkey)
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_main_thread(show_dialog)
        else:
            # Synchronous execution
            show_dialog()
    
    def _process_hotkey_change(self, set_name, new_hotkey):
        """
        Process a hotkey change for an instruction set.
        
        Parameters
        ----------
        set_name : str
            The name of the instruction set.
        new_hotkey : str
            The new hotkey string.
        """
        # Check for conflicts with other instruction sets
        for instruction_set in self.manager.get_all_sets():
            if instruction_set.name != set_name and instruction_set.hotkey == new_hotkey:
                self._show_hotkey_conflict_error(instruction_set.name)
                return
        
        # Update hotkey
        self.manager.update_set_hotkey(set_name, new_hotkey)
        self.hotkey_input.setText(new_hotkey)
    
    def _show_hotkey_conflict_error(self, conflicting_set_name):
        """
        Show error message for hotkey conflict.
        
        Parameters
        ----------
        conflicting_set_name : str
            The name of the instruction set that already uses the hotkey.
        """
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_HOTKEY_CONFLICT_TITLE,
            AppLabels.INSTRUCTION_SETS_HOTKEY_CONFLICT_MESSAGE.format(conflicting_set_name),
            SimpleMessageDialog.WARNING,
            self.thread_manager
        )
    
    def on_save_changes(self):
        """
        Handle saving changes to the current instruction set.
        
        Uses thread_manager to ensure UI updates and I/O operations happen
        safely if thread_manager is provided.
        """
        row = self.sets_list.currentRow()
        if row < 0:
            return
        
        name = self.sets_list.item(row).text()
        
        # Get edited values
        vocabulary = self.vocabulary_edit.toPlainText()
        instructions = self.instructions_edit.toPlainText()
        
        # Get language and model settings
        stt_language = self.stt_language_combo.currentData()
        stt_model = self.stt_model_combo.currentData()
        
        # Get LLM settings
        llm_enabled = self.llm_enabled_checkbox.isChecked()
        llm_model = self.llm_model_combo.currentData()
        llm_instructions = self.llm_instructions_edit.toPlainText()
        
        # Get LLM clipboard settings
        llm_clipboard_text_enabled = self.llm_clipboard_text_checkbox.isChecked()
        llm_clipboard_image_enabled = self.llm_clipboard_image_checkbox.isChecked()
        
        # Get hotkey
        hotkey = self.hotkey_input.text()
        
        def save_operation():
            # Update set
            return self.manager.update_set(
                name, vocabulary, instructions, stt_language, stt_model,
                llm_enabled, llm_model, llm_instructions, llm_clipboard_text_enabled,
                llm_clipboard_image_enabled, hotkey
            )
            
        def on_save_complete(result):
            # Show confirmation
            if result:
                self._show_changes_saved(name)
            
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_worker_thread(
                "save_instruction_set",
                save_operation,
                callback=on_save_complete
            )
        else:
            # Synchronous save
            result = save_operation()
            on_save_complete(result)
    
    def _show_changes_saved(self, set_name):
        """
        Show confirmation message that changes were saved.
        
        Parameters
        ----------
        set_name : str
            The name of the instruction set.
        """
        SimpleMessageDialog.show_message(
            self,
            AppLabels.INSTRUCTION_SETS_CHANGES_SAVED_TITLE,
            AppLabels.INSTRUCTION_SETS_CHANGES_SAVED_MESSAGE.format(set_name),
            SimpleMessageDialog.INFO,
            self.thread_manager
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
    
    def showEvent(self, event):
        """
        Handle dialog show event.
        
        This method is called when the dialog is shown. It disables all hotkeys
        to prevent them from being triggered while the dialog is open.
        
        Parameters
        ----------
        event : QShowEvent
            Show event
        """
        # Call parent class method first
        super().showEvent(event)
        
        # Disable all hotkeys by using HotkeyBridge's set_recording_mode
        # Setting enabled=True with an empty recording_hotkey effectively disables all hotkeys
        hotkey_bridge = HotkeyBridge.instance()
        if hotkey_bridge:
            try:
                hotkey_bridge.set_recording_mode(True, None)
                self.hotkeys_disabled = True
            except Exception:
                # Silent error handling for hotkey disabling failures
                pass
    
    def closeEvent(self, event):
        """
        Handle dialog close event.
        
        This method is called when the dialog is closed. It re-enables all hotkeys
        that were disabled when the dialog was shown.
        
        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Call parent class method
        super().closeEvent(event)
    
    def accept(self):
        """
        Handle dialog acceptance.
        
        This method is called when the Close button is clicked. It re-enables
        all hotkeys that were disabled when the dialog was shown.
        """
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Call parent class method
        super().accept()
    
    def reject(self):
        """
        Handle dialog rejection.
        
        This method is called when the dialog is rejected (e.g., by pressing Escape).
        It re-enables all hotkeys that were disabled when the dialog was shown.
        """
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Call parent class method
        super().reject()
    
    def _restore_hotkeys(self):
        """
        Restore hotkeys that were disabled.
        
        This method re-enables all hotkeys that were disabled when the dialog was shown.
        """
        if self.hotkeys_disabled:
            hotkey_bridge = HotkeyBridge.instance()
            if hotkey_bridge:
                try:
                    # Disable recording mode to re-enable all hotkeys
                    hotkey_bridge.set_recording_mode(False)
                    self.hotkeys_disabled = False
                except Exception:
                    # Silent error handling for hotkey restoration failures
                    pass
    
    @pyqtSlot(int)
    def on_llm_model_changed(self, index):
        """
        Handle changes to the LLM model selection.
        
        Updates the clipboard image checkbox based on whether the selected model
        supports image inputs.
        
        Parameters
        ----------
        index : int
            The index of the selected item in the combo box.
        """
        # Get the selected model ID
        selected_model_id = self.llm_model_combo.itemData(index)
        
        # Check if LLM is enabled
        is_llm_enabled = self.llm_enabled_checkbox.isChecked()
        
        # Check if model supports image input
        supports_image = False
        if selected_model_id:
            supports_image = LLMModelManager.supports_image_input(selected_model_id)
        
        # Update UI components
        def update_ui():
            # Image checkbox is enabled only if LLM is enabled AND model supports images
            self.llm_clipboard_image_checkbox.setEnabled(is_llm_enabled and supports_image)
            
            # If model doesn't support images, uncheck the checkbox
            if not supports_image:
                self.llm_clipboard_image_checkbox.setChecked(False)
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_main_thread(update_ui)
        else:
            # Synchronous update
            update_ui()
    
    @pyqtSlot(int)
    def on_llm_enabled_changed(self, state):
        """
        Handle changes to the LLM enabled checkbox.
        
        Enables/disables LLM-related UI elements based on the checkbox state.
        
        Parameters
        ----------
        state : int
            Checkbox state (Qt.Checked or Qt.Unchecked).
        """
        # Define if LLM is enabled
        is_enabled = state == Qt.CheckState.Checked.value
        
        # Get current selected LLM model
        selected_model_id = self.llm_model_combo.currentData()
        
        # Check if model supports image input
        supports_image = False
        if selected_model_id:
            supports_image = LLMModelManager.supports_image_input(selected_model_id)
        
        # Update UI components
        def update_ui():
            # Enable/disable LLM model selector
            self.llm_model_combo.setEnabled(is_enabled)
            
            # Enable/disable LLM context checkboxes
            self.llm_clipboard_text_checkbox.setEnabled(is_enabled)
            
            # Image checkbox is enabled only if LLM is enabled AND model supports images
            self.llm_clipboard_image_checkbox.setEnabled(is_enabled and supports_image)
            
            # Enable/disable LLM tab (instructions)
            llm_tab_index = self.tab_widget.indexOf(self.tab_widget.findChild(QWidget, "", 
                                                   Qt.FindChildOption.FindDirectChildrenOnly))
            
            # Since we don't have direct tab references, let's find the LLM tab by index
            # We know it's tab index 2 from the init_ui method
            # (self.tab_widget.addTab(llm_tab, AppLabels.INSTRUCTION_SETS_LLM_TAB_NAME))
            llm_tab_index = 2
            
            # We don't disable the tab entirely as that would make it inaccessible
            # Instead, we disable the contents of the tab
            llm_tab = self.tab_widget.widget(llm_tab_index)
            if llm_tab:
                self.llm_instructions_edit.setEnabled(is_enabled)
        
        # Use thread manager if available
        if self.thread_manager:
            self.thread_manager.run_in_main_thread(update_ui)
        else:
            # Synchronous update
            update_ui()

"""
Instruction Dialog Controller

This module provides the controller component for the instruction dialog in the Super Whisper application.
It mediates between the instruction dialog view and model.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.stt.stt_lang_model import STTLangModel
from core.stt.stt_model import STTModel
from core.llm.llm_model import LLMModel
from core.pipelines.instruction_set import InstructionSet

from ...managers.settings_manager import SettingsManager
from ...models.dialogs.instruction_dialog_model import InstructionDialogModel
from ...views.factories.hotkey_dialog_factory import HotkeyDialogFactory


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "instruction_set_already_exists_format": "An instruction set named '{name}' already exists.",
            "instruction_set_created_successfully_format": "Instruction set '{name}' created successfully.",
            "instruction_set_creation_failed_format": "Failed to create instruction set '{name}'.",
            "instruction_set_not_exists_format": "Instruction set '{name}' does not exist.",
            "instruction_set_updated_successfully_format": "Instruction set '{name}' updated successfully.",
            "instruction_set_update_failed_format": "Failed to update instruction set '{name}'.",
            "cannot_delete_last_instruction_set": "Cannot delete the last instruction set.",
            "instruction_set_deleted_successfully_format": "Instruction set '{name}' deleted successfully.",
            "instruction_set_deletion_failed_format": "Failed to delete instruction set '{name}'.",
            "instruction_set_renamed_successfully_format": "Instruction set renamed from '{old_name}' to '{new_name}' successfully.",
            "instruction_set_rename_failed_format": "Failed to rename instruction set from '{old_name}' to '{new_name}'.",
            "hotkey_update_failed_format": "Failed to update hotkey for '{set_name}'.",
            "hotkey_set_successfully_format": "Hotkey for '{set_name}' set to '{hotkey}' successfully.",
            "hotkey_cleared_successfully_format": "Hotkey for '{set_name}' cleared successfully.",
        },
        "Japanese": {
            "instruction_set_already_exists_format": "'{name}' というインストラクションセットは既に存在します。",
            "instruction_set_created_successfully_format": "インストラクションセット '{name}' を作成しました。",
            "instruction_set_creation_failed_format": "インストラクションセット '{name}' の作成に失敗しました。",
            "instruction_set_not_exists_format": "インストラクションセット '{name}' は存在しません。",
            "instruction_set_updated_successfully_format": "インストラクションセット '{name}' を更新しました。",
            "instruction_set_update_failed_format": "インストラクションセット '{name}' の更新に失敗しました。",
            "cannot_delete_last_instruction_set": "最後のインストラクションセットは削除できません。",
            "instruction_set_deleted_successfully_format": "インストラクションセット '{name}' を削除しました。",
            "instruction_set_deletion_failed_format": "インストラクションセット '{name}' の削除に失敗しました。",
            "instruction_set_renamed_successfully_format": "インストラクションセット名を '{old_name}' から '{new_name}' に変更しました。",
            "instruction_set_rename_failed_format": "インストラクションセット名の変更（{old_name} → {new_name}）に失敗しました。",
            "hotkey_update_failed_format": "'{set_name}' のホットキー更新に失敗しました。",
            "hotkey_set_successfully_format": "'{set_name}' のホットキーを '{hotkey}' に設定しました。",
            "hotkey_cleared_successfully_format": "'{set_name}' のホットキーをクリアしました。",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def instruction_set_already_exists_format(self) -> str:
        return self._labels["instruction_set_already_exists_format"]

    @property
    def instruction_set_created_successfully_format(self) -> str:
        return self._labels["instruction_set_created_successfully_format"]

    @property
    def instruction_set_creation_failed_format(self) -> str:
        return self._labels["instruction_set_creation_failed_format"]

    @property
    def instruction_set_not_exists_format(self) -> str:
        return self._labels["instruction_set_not_exists_format"]

    @property
    def instruction_set_updated_successfully_format(self) -> str:
        return self._labels["instruction_set_updated_successfully_format"]

    @property
    def instruction_set_update_failed_format(self) -> str:
        return self._labels["instruction_set_update_failed_format"]

    @property
    def cannot_delete_last_instruction_set(self) -> str:
        return self._labels["cannot_delete_last_instruction_set"]

    @property
    def instruction_set_deleted_successfully_format(self) -> str:
        return self._labels["instruction_set_deleted_successfully_format"]

    @property
    def instruction_set_deletion_failed_format(self) -> str:
        return self._labels["instruction_set_deletion_failed_format"]

    @property
    def instruction_set_renamed_successfully_format(self) -> str:
        return self._labels["instruction_set_renamed_successfully_format"]

    @property
    def instruction_set_rename_failed_format(self) -> str:
        return self._labels["instruction_set_rename_failed_format"]

    @property
    def hotkey_update_failed_format(self) -> str:
        return self._labels["hotkey_update_failed_format"]

    @property
    def hotkey_set_successfully_format(self) -> str:
        return self._labels["hotkey_set_successfully_format"]

    @property
    def hotkey_cleared_successfully_format(self) -> str:
        return self._labels["hotkey_cleared_successfully_format"]


class InstructionDialogController(QObject):
    """
    Controller for the instruction dialog.

    This class mediates between the instruction dialog view and model,
    handling user interactions and business logic.

    Attributes
    -------
    instruction_set_added : pyqtSignal(str)
        Signal emitted when an instruction set is added
    instruction_set_deleted : pyqtSignal(str)
        Signal emitted when an instruction set is deleted
    instruction_set_renamed : pyqtSignal(str, str)
        Signal emitted when an instruction set is renamed
    hotkey_conflict : pyqtSignal(str, str)
        Signal emitted when there is a hotkey conflict
    operation_result : pyqtSignal(bool, str)
        Signal emitted with the result of an operation
    """

    #
    # Signals
    #
    instruction_set_added = pyqtSignal(str)  # Name of added set
    instruction_set_deleted = pyqtSignal(str)  # Name of deleted set
    instruction_set_renamed = pyqtSignal(str, str)  # Old name, new name
    operation_result = pyqtSignal(bool, str)  # Success/failure, message

    def __init__(self, instruction_dialog: QObject | None = None) -> None:
        """
        Initialize the InstructionDialogController.

        Parameters
        ----------
        instruction_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=instruction_dialog)

        # Initialize label manager
        self._label_manager = LabelManager()

        # Create model
        self._model = InstructionDialogModel(instruction_dialog=instruction_dialog)

        # Connect model signals
        self._connect_model_signals()

        # Currently selected set name
        self._selected_set_name = ""

    #
    # Model Signals
    #
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model.
        """
        self._model.instruction_set_added.connect(self._handle_instruction_set_added)
        self._model.instruction_set_deleted.connect(self._handle_instruction_set_deleted)
        self._model.instruction_set_renamed.connect(self._handle_instruction_set_renamed)
        self._model.hotkey_updated.connect(self._handle_hotkey_updated)

    #
    # Model Events
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
        # Forward signal to view
        self.instruction_set_added.emit(name)

    @pyqtSlot(str)
    def _handle_instruction_set_deleted(self, name: str) -> None:
        """
        Handle instruction set deleted event.

        Parameters
        ----------
        name : str
            Name of the deleted set
        """
        # Forward signal to view
        self.instruction_set_deleted.emit(name)

        # If this was the selected set, clear selection
        if name == self._selected_set_name:
            self._selected_set_name = ""

    @pyqtSlot(str, str)
    def _handle_instruction_set_renamed(self, old_name: str, new_name: str) -> None:
        """
        Handle instruction set renamed event.

        Parameters
        ----------
        old_name : str
            Old name of the set
        new_name : str
            New name of the set
        """
        # Forward signal to view
        self.instruction_set_renamed.emit(old_name, new_name)

        # Update selected set name if it was renamed
        if old_name == self._selected_set_name:
            self._selected_set_name = new_name

    @pyqtSlot(str)
    def _handle_hotkey_updated(self, hotkey: str) -> None:
        """
        Handle hotkey updated event.

        Parameters
        ----------
        hotkey : str
            The new hotkey
        """
        # Register new hotkey if not empty
        if hotkey:
            # Register the hotkey
            self._model.register_hotkey(hotkey=hotkey)

    #
    # Controller Methods
    #
    def get_available_stt_languages(self) -> list[STTLangModel]:
        """
        Get available languages for speech recognition.

        Returns
        -------
        list[STTLangModel]
            List of available language objects
        """
        return self._model.get_available_stt_languages()

    def get_available_stt_models(self) -> list[STTModel]:
        """
        Get available speech recognition models.

        Returns
        -------
        list[STTModel]
            List of available STT model objects
        """
        return self._model.get_available_stt_models()

    def get_available_llm_models(self) -> list[LLMModel]:
        """
        Get available LLM models.

        Returns
        -------
        list[LLMModel]
            List of available LLM model objects
        """
        return self._model.get_available_llm_models()

    def check_image_input_supported(self, model_id: str) -> bool:
        """
        Check if an LLM model supports image input.

        Parameters
        ----------
        model_id : str
            ID of the LLM model to check

        Returns
        -------
        bool
            True if the model supports image input, False otherwise
        """
        return self._model.check_image_input_supported(model_id=model_id)
    
    def check_mcp_servers_json_str(self, json_str: str) -> None:
        """
        Check if the MCP servers JSON string is valid.

        Parameters
        ----------
        json_str : str
            MCP servers JSON string.

        Raises
        ------
        AssertionError
            If the MCP servers JSON string is invalid.
        json.JSONDecodeError
            If the MCP servers JSON string is not valid JSON.
        """
        return self._model.check_mcp_servers_json_str(json_str=json_str)

    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.

        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        return self._model.start_listening()

    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.

        Returns
        -------
        bool
            True if listening stopped successfully, False otherwise
        """
        return self._model.stop_listening()

    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.

        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._model.get_all_sets()

    def get_set_by_name(self, name: str) -> InstructionSet | None:
        """
        Get an instruction set by name.

        Parameters
        ----------
        name : str
            Name of the instruction set to find

        Returns
        -------
        InstructionSet | None
            The instruction set with the specified name, or None if not found
        """
        return self._model.get_set_by_name(name=name)

    def select_set(self, name: str) -> InstructionSet | None:
        """
        Select an instruction set by name.

        Parameters
        ----------
        name : str
            Name of the instruction set to select

        Returns
        -------
        bool
            True if successful, False if the set doesn't exist
        """
        instruction_set = self._model.get_set_by_name(name=name)
        if not instruction_set:
            return None

        self._selected_set_name = name
        return instruction_set

    def get_selected_set(self) -> InstructionSet | None:
        """
        Get the currently selected instruction set.

        Returns
        -------
        InstructionSet | None
            The currently selected instruction set, or None if none selected
        """
        if not self._selected_set_name:
            return None

        return self._model.get_set_by_name(name=self._selected_set_name)

    def add_set(self, name: str) -> bool:
        """
        Add a new instruction set with default settings.

        Parameters
        ----------
        name : str
            Name for the new instruction set

        Returns
        -------
        bool
            True if successful, False if a set with the name already exists
        """
        # Check if name already exists
        if self._model.get_set_by_name(name=name):
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_already_exists_format.format(name=name),
            )
            return False

        # Add set with default settings
        result = self._model.add_set(name=name)

        if result:
            self.operation_result.emit(
                True,
                self._label_manager.instruction_set_created_successfully_format.format(name=name),
            )
        else:
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_creation_failed_format.format(name=name),
            )

        return result

    def update_set(self, name: str, **kwargs) -> bool:
        """
        Update an existing instruction set.

        Parameters
        ----------
        name : str
            Name of the instruction set to update
        **kwargs : dict
            Keyword arguments with properties to update

        Returns
        -------
        bool
            True if successful, False if the set doesn't exist
        """
        # Check if set exists
        if not self._model.get_set_by_name(name=name):
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_not_exists_format.format(name=name),
            )
            return False

        # Update the set
        result = self._model.update_set(name=name, **kwargs)

        if result:
            self.operation_result.emit(
                True,
                self._label_manager.instruction_set_updated_successfully_format.format(name=name),
            )
        else:
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_update_failed_format.format(name=name),
            )

        return result

    def delete_set(self, name: str) -> bool:
        """
        Delete an instruction set.

        Parameters
        ----------
        name : str
            Name of the instruction set to delete

        Returns
        -------
        bool
            True if successful, False if the set doesn't exist or is the last one
        """
        # Check if set exists
        if not self._model.get_set_by_name(name=name):
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_not_exists_format.format(name=name),
            )
            return False

        # Check if this is the last set
        if len(self._model.get_all_sets()) <= 1:
            self.operation_result.emit(
                False,
                self._label_manager.cannot_delete_last_instruction_set,
            )
            return False

        # Delete the set
        result = self._model.delete_set(name=name)

        if result:
            self.operation_result.emit(
                True,
                self._label_manager.instruction_set_deleted_successfully_format.format(name=name),
            )
        else:
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_deletion_failed_format.format(name=name),
            )

        return result

    def rename_set(self, old_name: str, new_name: str) -> bool:
        """
        Rename an instruction set.

        Parameters
        ----------
        old_name : str
            Current name of the instruction set
        new_name : str
            New name for the instruction set

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        # Check if old name exists
        if not self._model.get_set_by_name(name=old_name):
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_not_exists_format.format(name=old_name),
            )
            return False

        # Check if new name already exists
        if self._model.get_set_by_name(name=new_name):
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_already_exists_format.format(name=new_name),
            )
            return False

        # Rename the set
        result = self._model.rename_set(old_name=old_name, new_name=new_name)

        if result:
            self.operation_result.emit(
                True,
                self._label_manager.instruction_set_renamed_successfully_format.format(old_name=old_name, new_name=new_name),
            )
        else:
            self.operation_result.emit(
                False,
                self._label_manager.instruction_set_rename_failed_format.format(old_name=old_name, new_name=new_name),
            )

        return result

    def _update_hotkey(self, set_name: str, hotkey: str) -> bool:
        """
        Update the hotkey for an instruction set.

        Parameters
        ----------
        set_name : str
            Name of the instruction set
        hotkey : str
            New hotkey string

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        # Update the hotkey
        result = self._model.update_set(name=set_name, hotkey=hotkey)

        # Emit the result
        if not result:
            self.operation_result.emit(
                False,
                self._label_manager.hotkey_update_failed_format.format(set_name=set_name),
            )
            return False
        if hotkey:
            self.operation_result.emit(
                True,
                self._label_manager.hotkey_set_successfully_format.format(set_name=set_name, hotkey=hotkey),
            )
        else:
            self.operation_result.emit(
                True,
                self._label_manager.hotkey_cleared_successfully_format.format(set_name=set_name),
            )
        return True

    def show_hotkey_dialog(
        self,
        current_hotkey: str,
        set_name: str,
        instruction_dialog: QObject | None = None,
    ) -> str | None:
        """
        Show the hotkey dialog and handle the result.

        This method creates, displays, and handles the result of a hotkey dialog,
        encapsulating the dialog flow logic.

        Parameters
        ----------
        current_hotkey : str
            The current hotkey
        set_name : str
            The name of the instruction set
        instruction_dialog : QObject | None, optional
            The instruction dialog, by default None

        Returns
        -------
        str | None
            The new hotkey if it has changed, None otherwise
        """
        # Create hotkey dialog using factory
        dialog = HotkeyDialogFactory.create_dialog(
            current_hotkey=current_hotkey,
            instruction_dialog=instruction_dialog,
        )

        # Show dialog and get result
        result = dialog.exec()

        # Handle dialog result
        if result == dialog.DialogCode.Accepted:
            # Update hotkey if it has changed
            new_hotkey = dialog.get_hotkey()
            if new_hotkey != current_hotkey:
                self._update_hotkey(set_name=set_name, hotkey=new_hotkey)
                return new_hotkey
            else:
                return None
        else:
            return None

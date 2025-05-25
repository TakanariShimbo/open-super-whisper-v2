"""
Settings Manager

This module provides a centralized manager for application settings using JSON files.
It serves as a single point of interaction with configuration files to enforce consistent
access patterns and reduce direct dependencies throughout the application.
"""

import os
import json
import pathlib
import threading
from typing import Any

from core.api.api_client_factory import APIClientFactory


class SettingsManager:
    """
    Centralized manager for JSON settings operations.

    This class provides a unified interface for interacting with application settings,
    abstracting away direct file access dependencies from other parts of the application.
    It offers both generic methods for settings access and specific methods for
    commonly used settings. Settings are stored in JSON format in the user's home directory.
    """

    # Define common setting keys as constants to avoid string duplication
    # and ensure consistency
    KEY_API_KEY = "api_key"
    KEY_INSTRUCTION_SETS = "instruction_sets"
    KEY_SELECTED_INSTRUCTION_SET = "selected_instruction_set"
    KEY_AUDIO_NOTIFICATIONS_ENABLED = "audio_notifications_enabled"
    KEY_AUDIO_NOTIFICATIONS_VOLUME = "audio_notifications_volume"
    KEY_INDICATOR_VISIBLE = "indicator_visible"
    KEY_AUTO_CLIPBOARD = "auto_clipboard"
    KEY_LANGUAGE = "language"

    # Directory and file constants
    CONFIG_DIR_NAME = ".open_super_whisper"
    CONFIG_FILE_NAME = "settings.json"

    _instance = None
    _lock = threading.RLock()  # Reentrant lock for thread safety

    @classmethod
    def instance(cls) -> "SettingsManager":
        """
        Get the singleton instance of the SettingsManager.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the SettingsManager with JSON configuration file.

        Raises
        ------
        Exception
            If the SettingsManager is instantiated directly
        """
        if self._instance is not None:
            raise Exception("SettingsManager is a singleton class and cannot be instantiated directly.")

        self._instance = self
        self._settings = {}  # In-memory settings cache

        # Determine the configuration directory and file path
        self._config_dir = pathlib.Path.home() / self.CONFIG_DIR_NAME
        self._config_file = self._config_dir / self.CONFIG_FILE_NAME

        # Ensure config directory exists
        self._ensure_config_dir()

        # Load settings from file or create defaults
        self._load_settings()

    def _ensure_config_dir(self) -> None:
        """
        Ensure that the configuration directory exists.
        """
        if not self._config_dir.exists():
            os.makedirs(name=self._config_dir, exist_ok=True)

    def _load_settings(self) -> None:
        """
        Load settings from the JSON file or initialize with defaults if file doesn't exist.
        """
        with self._lock:
            if self._config_file.exists():
                try:
                    with open(file=self._config_file, mode="r", encoding="utf-8") as file:
                        self._settings = json.load(file)
                except (json.JSONDecodeError, IOError) as e:
                    # If the file is corrupted or can't be read, use defaults
                    print(f"Error loading settings file: {e}. Using defaults.")
            else:
                # Initialize with defaults
                self._settings = self._get_default_settings()
                self._save_settings()  # Create initial settings file

    def _save_settings(self) -> None:
        """
        Save the current settings to the JSON file.
        """
        with self._lock:
            try:
                with open(file=self._config_file, mode="w", encoding="utf-8") as file:
                    json.dump(obj=self._settings, fp=file, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"Error saving settings file: {e}")

    def _get_default_settings(self) -> dict[str, Any]:
        """
        Get the default settings.

        Returns
        -------
        dict[str, Any]
            A dictionary containing default settings
        """
        return {
            self.KEY_API_KEY: "",
            self.KEY_INSTRUCTION_SETS: [],
            self.KEY_SELECTED_INSTRUCTION_SET: "",
            self.KEY_AUDIO_NOTIFICATIONS_ENABLED: True,
            self.KEY_AUDIO_NOTIFICATIONS_VOLUME: 0.7,
            self.KEY_INDICATOR_VISIBLE: True,
            self.KEY_AUTO_CLIPBOARD: False,
            self.KEY_LANGUAGE: "English",
        }

    def _get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from settings.

        Parameters
        ----------
        key : SettingsKey
            The setting key to retrieve
        default : SettingsValue, optional
            The default value to return if key is not found, by default None

        Returns
        -------
        SettingsValue
            The value associated with the key, or the default if not found
        """
        with self._lock:
            return self._settings.get(key, default)

    def _set_value(self, key: str, value: Any) -> None:
        """
        Set a value in settings.

        Parameters
        ----------
        key : SettingsKey
            The setting key to set
        value : SettingsValue
            The value to associate with the key
        """
        with self._lock:
            self._settings[key] = value
            self._save_settings()

    def _remove_value(self, key: str) -> None:
        """
        Remove a key-value pair from settings.

        Parameters
        ----------
        key : str
            The setting key to remove
        """
        with self._lock:
            if key in self._settings:
                del self._settings[key]
                self._save_settings()

    # API key methods

    def get_api_key(self) -> str:
        """
        Get the stored API key.

        Returns
        -------
        str
            The stored API key, or an empty string if none is stored
        """
        return self._get_value(key=self.KEY_API_KEY, default="")

    def set_api_key(self, api_key: str) -> None:
        """
        Store an API key.

        Parameters
        ----------
        api_key : str
            The API key to store
        """
        self._set_value(key=self.KEY_API_KEY, value=api_key)

    def has_valid_api_key(self) -> bool:
        """
        Check if the stored API key is valid.

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        stored_api_key = self.get_api_key()
        if not stored_api_key:
            return False

        is_successful, _ = APIClientFactory.create_client(api_key=stored_api_key)
        return is_successful

    # Audio notification methods

    def get_audio_notifications_enabled(self) -> bool:
        """
        Check if audio notifications are enabled.

        Returns
        -------
        bool
            True if notifications are enabled, False otherwise
        """
        return self._get_value(key=self.KEY_AUDIO_NOTIFICATIONS_ENABLED, default=True)

    def set_audio_notifications_enabled(self, enabled: bool) -> None:
        """
        Set whether audio notifications are enabled.

        Parameters
        ----------
        enabled : bool
            True to enable notifications, False to disable
        """
        self._set_value(key=self.KEY_AUDIO_NOTIFICATIONS_ENABLED, value=enabled)

    def get_audio_notifications_volume(self) -> float:
        """
        Get the volume level for audio notifications.

        Returns
        -------
        float
            Volume level between 0.0 and 1.0
        """
        return self._get_value(key=self.KEY_AUDIO_NOTIFICATIONS_VOLUME, default=0.7)

    def set_audio_notifications_volume(self, volume: float) -> None:
        """
        Set the volume level for audio notifications.

        Parameters
        ----------
        volume : float
            Volume level between 0.0 and 1.0

        Raises
        ------
        ValueError
            If the volume is outside the valid range
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")

        self._set_value(key=self.KEY_AUDIO_NOTIFICATIONS_VOLUME, value=volume)

    # Instruction set methods

    def get_instruction_sets(self) -> list[dict[str, Any]]:
        """
        Get the stored instruction sets.

        Returns
        -------
        list[dict[str, Any]]
            The serialized instruction sets data, or empty list if not found
        """
        return self._get_value(key=self.KEY_INSTRUCTION_SETS, default=[])

    def set_instruction_sets(self, instruction_sets_data: Any) -> None:
        """
        Store instruction sets data.

        Parameters
        ----------
        instruction_sets_data : Any
            The serialized instruction sets data to store
        """
        self._set_value(key=self.KEY_INSTRUCTION_SETS, value=instruction_sets_data)

    def get_selected_instruction_set(self) -> str:
        """
        Get the name of the selected instruction set.

        Returns
        -------
        str
            The name of the selected instruction set, or an empty string if none selected
        """
        return self._get_value(key=self.KEY_SELECTED_INSTRUCTION_SET, default="")

    def set_selected_instruction_set(self, name: str) -> None:
        """
        Set the selected instruction set by name.

        Parameters
        ----------
        name : str
            Name of the instruction set to select
        """
        self._set_value(key=self.KEY_SELECTED_INSTRUCTION_SET, value=name)

    # Status indicator visibility methods

    def get_indicator_visible(self) -> bool:
        """
        Check if status indicator should be visible.

        Returns
        -------
        bool
            True if indicator should be visible, False otherwise
        """
        return self._get_value(key=self.KEY_INDICATOR_VISIBLE, default=True)

    def set_indicator_visible(self, visible: bool) -> None:
        """
        Set whether status indicator should be visible.

        Parameters
        ----------
        visible : bool
            True to make indicator visible, False to hide
        """
        self._set_value(key=self.KEY_INDICATOR_VISIBLE, value=visible)

    # Auto clipboard methods

    def get_auto_clipboard(self) -> bool:
        """
        Check if results should be automatically copied to clipboard.

        Returns
        -------
        bool
            True if auto-clipboard is enabled, False otherwise
        """
        return self._get_value(key=self.KEY_AUTO_CLIPBOARD, default=False)

    def set_auto_clipboard(self, enabled: bool) -> None:
        """
        Set whether results should be automatically copied to clipboard.

        Parameters
        ----------
        enabled : bool
            True to enable auto-clipboard, False to disable
        """
        self._set_value(key=self.KEY_AUTO_CLIPBOARD, value=enabled)

    # Language methods

    def get_language(self) -> str:
        """
        Get the selected application language.

        Returns
        -------
        str | None
            The selected language name, or None if not set
        """
        return self._get_value(key=self.KEY_LANGUAGE, default="English")

    def set_language(self, language: str) -> None:
        """
        Set the application language.

        Parameters
        ----------
        language : str
            The language name to set
        """
        self._set_value(key=self.KEY_LANGUAGE, value=language)

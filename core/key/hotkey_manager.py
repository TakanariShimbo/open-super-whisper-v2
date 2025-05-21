"""
Hotkey Manager Implementation

This module provides functionality for registering and managing global hotkeys.
"""

from typing import Callable

from pynput import keyboard

from .key_formatter import KeyFormatter


class HotkeyManager:
    """
    Implementation for managing global hotkeys.

    This class provides methods to register and unregister global hotkeys
    that can be triggered even when the application is not in focus.
    Uses pynput library for the actual keyboard monitoring.

    Examples
    --------
    Basic usage:

    >>> hotkey_manager = HotkeyManager()
    >>> # Register a hotkey for Ctrl+Shift+R
    >>> hotkey_manager.register_hotkey("ctrl+shift+r", lambda: print("Hotkey pressed!"))
    >>> # Start listening for hotkeys
    >>> hotkey_manager.start_listening()
    >>> # Unregister the hotkey when no longer needed
    >>> hotkey_manager.stop_listening()
    >>> hotkey_manager.unregister_hotkey("ctrl+shift+r")

    Filtered mode example:

    >>> hotkey_manager = HotkeyManager()
    >>> # Register multiple hotkeys
    >>> hotkey_manager.register_hotkey("ctrl+shift+r", lambda: print("Action R"))
    >>> hotkey.register("ctrl+shift+s", lambda: print("Action S"))
    >>> # Start listening with filtered mode to only allow specific hotkey
    >>> hotkey_manager.enable_filtered_mode(["ctrl+shift+r"])
    >>> hotkey_manager.start_listening()
    >>> # Later, stop and disable filtered mode to restore all hotkeys
    >>> hotkey_manager.stop_listening()
    >>> hotkey_manager.disable_filtered_mode()
    """

    def __init__(self) -> None:
        """
        Initialize the HotkeyManager.
        """
        self._hotkeys: dict[str, Callable] = {}  # Dictionary to store hotkey strings and their callbacks
        self._listener: keyboard.GlobalHotKeys | None = None  # Will be set to a listener object when active
        self._active_hotkeys: list[str] | None = None  # None = filter mode off, list = filter mode on (even empty list)

    @property
    def is_listening(self) -> bool:
        """
        Check if the hotkey manager is currently listening for hotkeys.

        Returns
        -------
        bool
            True if the manager is actively listening, False otherwise.
        """
        return self._listener is not None and self._listener.running

    @property
    def is_filter_mode_active(self) -> bool:
        """
        Check if the hotkey manager is in filtered mode.

        Returns
        -------
        bool
            True if filter mode is active, False otherwise.
        """
        return self._active_hotkeys is not None

    def register_hotkey(
        self,
        hotkey_string: str,
        callback: Callable,
    ) -> None:
        """
        Register a global hotkey.

        Parameters
        ----------
        hotkey_string : str
            String representation of the hotkey (e.g., "ctrl+shift+r").
        callback : Callable
            Function to call when the hotkey is pressed.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        ValueError
            If the hotkey string is invalid.
        """
        # Only allow registration if not listening
        if self.is_listening:
            raise RuntimeError("Cannot register hotkey: listener is active. Stop listening first.")

        # Parse hotkey string into the format pynput expects
        hotkey_combination = KeyFormatter.parse_hotkey_string(hotkey_string=hotkey_string)
        if not hotkey_combination:
            raise ValueError(f"Invalid hotkey string: {hotkey_string}")

        # Add the hotkey to our dictionary
        self._hotkeys[hotkey_combination] = callback

    def unregister_hotkey(self, hotkey_string: str) -> bool:
        """
        Unregister a previously registered global hotkey.

        Parameters
        ----------
        hotkey_string : str
            String representation of the hotkey to unregister.

        Returns
        -------
        bool
            True if the hotkey was successfully unregistered, False if it was not registered.

        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        ValueError
            If the hotkey string is invalid.
        """
        # Only allow unregistration if not listening
        if self.is_listening:
            raise RuntimeError("Cannot unregister hotkey: listener is active. Stop listening first.")

        # Parse hotkey string
        hotkey_combination = KeyFormatter.parse_hotkey_string(hotkey_string=hotkey_string)

        # Check if hotkey string is valid
        if not hotkey_combination:
            raise ValueError(f"Invalid hotkey string: {hotkey_string}")

        # Check if hotkey is registered
        if hotkey_combination not in self._hotkeys:
            return False

        # Remove hotkey from dictionary
        del self._hotkeys[hotkey_combination]
        return True

    def enable_filtered_mode(self, active_hotkeys: list[str]) -> None:
        """
        Enable filtered mode to allow only specific hotkeys to work.

        When filtered mode is enabled, only the specified hotkeys will trigger callbacks.
        All other hotkeys will be ignored.

        Parameters
        ----------
        active_hotkeys : list[str]
            List of hotkey strings that should remain active when filtered mode is enabled.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        ValueError
            If the hotkey string is invalid.
        """
        # Only allow mode change if not listening
        if self.is_listening:
            raise RuntimeError("Cannot enable filtered mode: listener is active. Stop listening first.")

        # Create a temporary list for parsed hotkeys
        parsed_hotkeys = []

        # Parse and validate each active hotkey
        for hotkey in active_hotkeys:
            parsed_hotkey = KeyFormatter.parse_hotkey_string(hotkey_string=hotkey)
            if not parsed_hotkey:
                raise ValueError(f"Invalid hotkey string: {hotkey}")
            parsed_hotkeys.append(parsed_hotkey)

        # All hotkeys are valid, now set the active hotkeys list
        self._active_hotkeys = parsed_hotkeys

    def disable_filtered_mode(self) -> None:
        """
        Disable filtered mode and allow all registered hotkeys to work.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        """
        # Only allow mode change if not listening
        if self.is_listening:
            raise RuntimeError("Cannot disable filtered mode: listener is active. Stop listening first.")

        # Set to None to indicate filter mode is inactive
        self._active_hotkeys = None

    def start_listening(self) -> None:
        """
        Start the hotkey listener.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If there are no hotkeys registered or if the listener is already active.
        """
        # Only start if we have hotkeys to listen for
        if not self._hotkeys:
            raise RuntimeError("Cannot start listening: no hotkeys registered")

        if self.is_listening:
            raise RuntimeError("Listener is already active")

        # Create and start a listener with our hotkeys and event filtering
        if self.is_filter_mode_active:
            self._start_filtered_listening()
        else:
            self._start_normal_listening()

        self._listener.start()

    def _start_filtered_listening(self) -> None:
        """
        Start listening with filtered mode active.

        Only the active hotkeys will be monitored.
        """
        # Create filtered hotkeys using dictionary comprehension
        filtered_hotkeys = {hotkey: callback for hotkey, callback in self._hotkeys.items() if hotkey in self._active_hotkeys}

        # Filtered mode, use only active hotkeys
        self._listener = keyboard.GlobalHotKeys(hotkeys=filtered_hotkeys)

    def _start_normal_listening(self) -> None:
        """
        Start listening in normal mode.

        All registered hotkeys will be monitored.
        """
        # Normal mode, use all hotkeys
        self._listener = keyboard.GlobalHotKeys(hotkeys=self._hotkeys)

    def stop_listening(self) -> bool:
        """
        Stop the hotkey listener.

        This method stops the listener without unregistering the hotkeys.

        Returns
        -------
        bool
            True if the listener was stopped, False if there was no active listener.
        """
        if not self.is_listening:
            return False

        self._listener.stop()
        self._listener = None
        return True

    def clear_all_hotkeys(self) -> None:
        """
        Clear all registered hotkeys.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        """
        # Only allow clearing if not listening
        if self.is_listening:
            raise RuntimeError("Cannot clear hotkeys: listener is active. Stop listening first.")

        # Clear the hotkeys dictionary
        self._hotkeys.clear()

    def get_registered_hotkeys(self) -> list[str]:
        """
        Get a list of all registered hotkey strings.

        Returns
        -------
        list[str]
            List of registered hotkey strings in the internal format.
        """
        return list(self._hotkeys.keys())

    def get_active_hotkeys(self) -> list[str] | None:
        """
        Get the list of active hotkeys when in filter mode.

        Returns
        -------
        list[str] | None
            List of active hotkey strings in the internal format,
            or None if filter mode is not active.
        """
        return self._active_hotkeys

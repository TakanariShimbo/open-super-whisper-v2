"""
Audio Manager

This module provides functionality to manage and play audio notifications
in the Open Super Whisper application.
"""

import os
import sys

from PyQt6.QtCore import QObject, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from ..utils.pyinstaller_utils import PyInstallerUtils
from .settings_manager import SettingsManager


class AudioManager(QObject):
    """
    Manager for audio notifications in the application.

    This class is responsible for loading and playing audio notifications,
    as well as managing user preferences for audio feedback.

    Attributes
    ----------
    SOUND_TYPES : Dict[str, str]
        Dictionary mapping sound types to their filenames.
    """

    # Define sound types
    _START_RECORDING = "start_recording"
    _STOP_RECORDING = "stop_recording"
    _COMPLETE_PROCESSING = "complete_processing"
    _CANCEL_PROCESSING = "cancel_processing"

    SOUND_TYPES = {
        _START_RECORDING: "start_recording.wav",
        _STOP_RECORDING: "stop_recording.wav",
        _COMPLETE_PROCESSING: "complete_processing.wav",
        _CANCEL_PROCESSING: "cancel_processing.wav",
    }

    # Singleton instance
    _instance = None

    @classmethod
    def instance(cls) -> "AudioManager":
        """
        Get the singleton instance of the AudioManager.

        Returns
        -------
        AudioManager
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the AudioManager.

        Raises
        ------
        Exception
            If the AudioManager is instantiated directly
        """
        # Check if singleton already exists
        if self._instance is not None:
            # If this is not the first instantiation, don't reinitialize
            raise Exception("AudioManager is a singleton class and cannot be instantiated directly.")

        self._instance = self

        super().__init__()

        # Store settings manager
        self._settings_manager = SettingsManager.instance()

        # Initialize media players for each sound type
        self._players: dict[str, QMediaPlayer] = {}
        self._audio_outputs: dict[str, QAudioOutput] = {}

        # Set up the media players
        self._setup_players()

        # Load settings
        self._is_enabled = self._settings_manager.get_audio_notifications_enabled()
        self._volume = self._settings_manager.get_audio_notifications_volume()

        # Apply volume setting to all players
        self._apply_volume_setting()

    @property
    def is_enabled(self) -> bool:
        """
        Check if audio notifications are enabled.

        Returns
        -------
        bool
            True if notifications are enabled, False otherwise
        """
        return self._is_enabled

    def set_enabled(self, value: bool) -> None:
        """
        Set whether audio notifications are enabled.

        Parameters
        ----------
        value : bool
            True to enable notifications, False to disable
        """
        self._is_enabled = value
        self._settings_manager.set_audio_notifications_enabled(enabled=value)

    def get_volume(self) -> float:
        """
        Get the current volume level.

        Returns
        -------
        float
            Volume level between 0.0 and 1.0
        """
        return self._volume

    def set_volume(self, value: float) -> None:
        """
        Set the volume level for audio notifications.

        Parameters
        ----------
        value : float
            Volume level between 0.0 and 1.0

        Raises
        ------
        ValueError
            If the value is outside the valid range
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")

        self._volume = value
        self._settings_manager.set_audio_notifications_volume(volume=value)

        # Apply the new volume setting
        self._apply_volume_setting()

    def _setup_players(self) -> None:
        """
        Set up media players for each sound type.
        """
        for sound_type, filename in self.SOUND_TYPES.items():
            # Create audio output
            audio_output = QAudioOutput()

            # Create media player
            player = QMediaPlayer()
            player.setAudioOutput(audio_output)

            # Store references
            self._players[sound_type] = player
            self._audio_outputs[sound_type] = audio_output

            # Load the sound file
            sound_path = self._get_sound_path(filename=filename)
            if sound_path:
                player.setSource(QUrl.fromLocalFile(sound_path))

    def _apply_volume_setting(self) -> None:
        """
        Apply the current volume setting to all audio outputs.
        """
        for audio_output in self._audio_outputs.values():
            audio_output.setVolume(self._volume)

    def _get_sound_path(self, filename: str) -> str | None:
        """
        Get the full path to a sound file.

        Parameters
        ----------
        filename : str
            Name of the sound file

        Returns
        -------
        str | None
            Full path to the sound file, or None if not found
        """
        # Try to get the path using the resource helper
        relative_sound_path = os.path.join("assets", filename)
        absolute_sound_path = PyInstallerUtils.get_resource_path(relative_path=relative_sound_path)

        # Check if the file exists
        if absolute_sound_path and os.path.exists(path=absolute_sound_path):
            return absolute_sound_path
        else:
            # Log a warning if the sound file is not found
            print(f"Warning: Sound file '{filename}' not found", file=sys.stderr)
            return None

    def _play_sound(self, sound_type: str) -> bool:
        """
        Play a sound notification.

        Parameters
        ----------
        sound_type : str
            Type of sound to play, must be one of SOUND_TYPES keys

        Returns
        -------
        bool
            True if the sound was played, False otherwise

        Raises
        ------
        ValueError
            If the sound_type is not valid
        """
        # Check if notifications are enabled
        if not self._is_enabled:
            return False

        # Check if the sound type is valid
        if sound_type not in self.SOUND_TYPES:
            raise ValueError(f"Invalid sound type: {sound_type}")

        # Get the player for this sound type
        player = self._players.get(sound_type)
        if not player:
            return False

        # Play the sound
        player.stop()  # Stop if already playing
        player.setPosition(0)  # Rewind to start
        player.play()

        return True

    def play_start_recording(self) -> bool:
        """
        Play the start recording sound.

        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self._play_sound(sound_type=self._START_RECORDING)

    def play_stop_recording(self) -> bool:
        """
        Play the stop recording sound.

        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self._play_sound(sound_type=self._STOP_RECORDING)

    def play_complete_processing(self) -> bool:
        """
        Play the complete processing sound.

        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self._play_sound(sound_type=self._COMPLETE_PROCESSING)

    def play_cancel_processing(self) -> bool:
        """
        Play the cancel processing sound.

        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self._play_sound(sound_type=self._CANCEL_PROCESSING)

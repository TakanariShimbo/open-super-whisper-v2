"""
Audio Manager

This module provides functionality to manage and play audio notifications
in the Super Whisper application.
"""

import os
import sys

from PyQt6.QtCore import QObject, QUrl, QSettings
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from .pyinstaller_utils import PyInstallerUtils


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
    SOUND_TYPES = {
        'start_recording': 'start_recording.wav',
        'stop_recording': 'stop_recording.wav',
        'complete_processing': 'complete_processing.wav',
        'cancel_processing': 'cancel_processing.wav'
    }
    
    def __init__(self, settings: QSettings) -> None:
        """
        Initialize the AudioManager.
        
        Parameters
        ----------
        settings : QSettings
            Application settings for persistence
        """
        super().__init__()
        
        # Store settings
        self._settings = settings
        
        # Initialize media players for each sound type
        self._players: dict[str, QMediaPlayer] = {}
        self._audio_outputs: dict[str, QAudioOutput] = {}
        
        # Set up the media players
        self._setup_players()
        
        # Load settings
        self._enabled = self._settings.value("audio_notifications_enabled", True, type=bool)
        self._volume = self._settings.value("audio_notifications_volume", 0.7, type=float)
        
        # Apply volume setting to all players
        self._apply_volume_setting()
    
    @property
    def enabled(self) -> bool:
        """
        Check if audio notifications are enabled.
        
        Returns
        -------
        bool
            True if notifications are enabled, False otherwise
        """
        return self._enabled
    
    def set_enabled(self, value: bool) -> None:
        """
        Set whether audio notifications are enabled.
        
        Parameters
        ----------
        value : bool
            True to enable notifications, False to disable
        """
        self._enabled = value
        self._settings.setValue("audio_notifications_enabled", value)
        self._settings.sync()
    
    @property
    def volume(self) -> float:
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
        self._settings.setValue("audio_notifications_volume", value)
        self._settings.sync()
        
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
            sound_path = self._get_sound_path(filename)
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
        relative_sound_path = os.path.join('assets', filename)
        absolute_sound_path = PyInstallerUtils.get_resource_path(relative_sound_path)
        
        # Check if the file exists
        if absolute_sound_path and os.path.exists(absolute_sound_path):
            return absolute_sound_path
        else:
            # Log a warning if the sound file is not found
            print(f"Warning: Sound file '{filename}' not found", file=sys.stderr)
            return None
    
    def play_sound(self, sound_type: str) -> bool:
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
        if not self._enabled:
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
        return self.play_sound('start_recording')
    
    def play_stop_recording(self) -> bool:
        """
        Play the stop recording sound.
        
        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self.play_sound('stop_recording')
    
    def play_complete_processing(self) -> bool:
        """
        Play the complete processing sound.
        
        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self.play_sound('complete_processing')
    
    def play_cancel_processing(self) -> bool:
        """
        Play the cancel processing sound.
        
        Returns
        -------
        bool
            True if the sound was played, False otherwise
        """
        return self.play_sound('cancel_processing')

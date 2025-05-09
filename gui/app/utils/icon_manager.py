"""
Icon Manager

This module provides the IconManager class for handling application icons
in a centralized way, following the Single Responsibility Principle.
"""

import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QStyle, QApplication

from .pyinstaller_utils import PyInstallerUtils


class IconManager:
    """
    Manages icon loading and provides icons to different parts of the application.
    
    This class handles loading icons from files, providing fallbacks when icons
    are unavailable, and centralizes icon management in the application.
    
    Attributes
    ----------
    _app_icon : QIcon
        The main application icon
    _icon_paths : dict
        Dictionary of icon names to file paths
    """

    def __init__(self) -> None:
        """
        Initialize the IconManager.
        
        Sets up icon paths and loads the application icon.
        """
        # Initialize icon cache
        self._app_icon = None
        
        # Set up icon paths
        self._icon_paths = {
            "app": self._get_icon_path("icon.png"),
            "app_ico": self._get_icon_path("icon.ico"),
            "app_icns": self._get_icon_path("icon.icns"),
        }
        
        # Load the main application icon
        self._load_app_icon()
    
    def _get_icon_path(self, icon_name: str) -> str | None:
        """
        Get the full path to an icon file.
        
        Parameters
        ----------
        icon_name : str
            The name of the icon file
            
        Returns
        -------
        str | None
            The full path to the icon file, or None if it doesn't exist
        """
        relative_icon_path = os.path.join("assets", icon_name)
        absolute_icon_path = PyInstallerUtils.get_resource_path(relative_icon_path)
        
        # Check if the resolved path exists
        if os.path.exists(absolute_icon_path):
            return absolute_icon_path
        else:
            print(f"Icon file not found: {absolute_icon_path}")
            return None
    
    def _load_app_icon(self) -> None:
        """
        Load the main application icon.
        
        Tries to load the icon from the configured paths, with fallbacks
        for different platforms. If no icon is found, falls back to a
        standard system icon.
        """
        # Try to load the most appropriate icon for the platform
        icon_paths = [
            self._icon_paths["app"],      # PNG first (universal)
            self._icon_paths["app_ico"],  # ICO for Windows
            self._icon_paths["app_icns"]  # ICNS for macOS
        ]
        
        # Try each path in order
        for path in icon_paths:
            if path:
                icon = QIcon(path)
                if not icon.isNull():
                    self._app_icon = icon
                    return
        
        # Fallback to a standard system icon if none of the custom icons work
        self._app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
    
    def get_app_icon(self) -> QIcon:
        """
        Get the main application icon.
        
        Returns
        -------
        QIcon
            The application icon
        """
        return self._app_icon
    
    def get_icon_path(self, icon_name: str) -> str | None:
        """
        Get the path to a named icon.
        
        Parameters
        ----------
        icon_name : str
            The name of the icon
            
        Returns
        -------
        str | None
            The path to the icon, or None if it doesn't exist
        """
        if icon_name in self._icon_paths:
            return self._icon_paths[icon_name]
        
        # If not in the predefined paths, try to find it
        return self._get_icon_path(icon_name)

"""
Resource Helper Utilities

This module provides helper functions for managing application resources. 
"""

import os
import sys


class PyInstallerUtils:
    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """
        Get the absolute path to a resource file.
        
        This function resolves the correct path to a resource file, whether the application is running from source or is bundled by PyInstaller.
        
        Parameters
        ----------
        relative_path : str
            Path relative to the application root or executable.
        
        Returns
        -------
        str
            Absolute path to the resource.
        """
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        try:
            base_path = sys._MEIPASS  # type: ignore
        except Exception:
            base_path = os.getcwd()
        
        return os.path.normpath(os.path.join(base_path, relative_path))

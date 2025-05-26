#!/usr/bin/env python3
"""
Open Super Whisper App Runner

This script runs the Open Super Whisper application.
"""

import os
import sys
import subprocess


# Configure ffmpeg environment before any imports
def setup_ffmpeg_environment() -> None:
    """
    Set up the ffmpeg environment by adding ffmpeg to the system PATH if it's not already there
    """
    # Get the current path
    current_path = os.environ.get("PATH", "")

    # Add ffmpeg/bin path from the project root directory
    project_ffmpeg_bin = os.path.join(
        os.path.dirname(p=os.path.abspath(path=__file__)),
        "ffmpeg",
        "bin",
    )

    # Check if ffmpeg/bin exists and is not already in the PATH
    is_ffmpeg_bin_exists = os.path.exists(path=project_ffmpeg_bin)
    is_ffmpeg_bin_in_path = project_ffmpeg_bin not in current_path
    if is_ffmpeg_bin_exists and is_ffmpeg_bin_in_path:
        os.environ["PATH"] = project_ffmpeg_bin + os.pathsep + current_path
        print(f"Added {project_ffmpeg_bin} to PATH for ffmpeg")


if __name__ == "__main__":
    # Set up ffmpeg environment
    setup_ffmpeg_environment()

    # Run the application in a loop until it is not required to restart
    while True:
        result = subprocess.run([sys.executable, "-m", "gui.main"])
        if result.returncode == 100:
            continue
        else:
            break

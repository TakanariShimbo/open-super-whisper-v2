#!/usr/bin/env python3
"""
Super Whisper App Runner

This script runs the Super Whisper application.
"""

import sys
import os

# Add the project root to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from super_whisper_app.main import main

if __name__ == "__main__":
    main()

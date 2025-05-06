#!/usr/bin/env python3
"""
Recorder Application Main Entry Point

This module allows running the recorder application as a Python package:
python -m recorder_app
"""
# Fix import to allow running the module directly
if __name__ == "__main__":
    import os
    import sys
    package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, package_dir)

from recorder_app.main import launch_recorder_app

if __name__ == "__main__":
    launch_recorder_app()

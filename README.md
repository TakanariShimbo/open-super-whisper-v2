# Open Super Whisper

A PyQt6-based GUI application for audio transcription using OpenAI's Whisper API. This application allows users to record audio, send it to Whisper for transcription, and view the results.

## Features

- Fully implemented PyQt6-based GUI
- Global hotkey support for starting and stopping recordings
- Advanced instruction set management:
  - Custom vocabulary lists for improved transcription accuracy
  - System instructions for controlling transcription behavior
  - Unified language and model settings in each instruction set
  - Simple switching between configuration profiles
- System tray integration
- Support for multiple languages and model configurations
- Clipboard integration
- Status indicator window
- Settings management

## Project Structure

```
.
├── main.py                      # Application entry point
├── README.md                    # Project description
├── pyproject.toml               # Project configuration and dependencies
├── assets/                      # Assets (icons, audio files, etc.)
│   ├── complete_sound.wav       # Sound played when transcription completes
│   ├── icon.icns                # Application icon (macOS)
│   ├── icon.ico                 # Application icon (Windows)
│   ├── icon.png                 # Application icon (cross-platform)
│   ├── start_sound.wav          # Sound played when recording starts
│   └── stop_sound.wav           # Sound played when recording stops
├── core/                # Core functionality (GUI-independent, fully implemented)
│   ├── __init__.py
│   ├── transcriber.py           # Audio transcription module
│   ├── recorder.py              # Audio recording module
│   ├── instructions.py          # Custom vocabularies and instruction sets
│   ├── hotkeys.py               # Global hotkey management
│   └── models/                  # Data models for languages and whisper models
│       ├── __init__.py
│       ├── language.py          # Language data models and manager
│       └── whisper.py           # Whisper model data models and manager
└── gui/                 # GUI-related functionality (Qt-dependent)
    ├── __init__.py
    ├── main.py                  # GUI entry point
    ├── components/              # Reusable UI components
    │   ├── __init__.py
    │   └── widgets/             # Custom widgets
    │       ├── __init__.py
    │       └── status_indicator.py
    ├── dialogs/                 # Dialog windows
    │   ├── __init__.py
    │   ├── api_key_dialog.py
    │   ├── hotkey_dialog.py
    │   ├── instruction_sets_dialog.py
    │   └── simple_message_dialog.py
    ├── resources/               # Application resources
    │   ├── __init__.py
    │   ├── config.py            # Configuration settings
    │   └── labels.py            # UI text labels
    ├── utils/                   # Utility functions
    │   ├── __init__.py
    │   └── resource_helper.py   # Resource path resolution
    └── windows/                 # Main application windows
        ├── __init__.py
        └── main_window.py       # Main application window
```

## Key Highlights

1. Clear Separation of Responsibilities
   - `core`: Core functionality independent of the GUI
   - `gui`: Qt-based GUI code that depends on core modules

2. Modular Design
   - Logical organization of features into dedicated directories
   - Reduced duplication of shared functionality

## How to Run

To start the application, run:

```bash
python main.py
```

## Packaging

To package the application into a standalone executable:

```bash
# Windows
python -m PyInstaller --onefile --windowed --icon assets/icon.ico --name "OpenSuperWhisper" --add-data "assets;assets" main.py

# For macOS
python -m PyInstaller --onefile --windowed --icon assets/icon.icns --name "OpenSuperWhisper" --add-data "assets:assets" main.py

# For Linux
python -m PyInstaller --onefile --windowed --icon assets/icon.png --name "OpenSuperWhisper" --add-data "assets:assets" main.py
```

The Windows command does the following:
- `--onefile`: Creates a single executable file
- `--windowed`: Prevents a console window from appearing
- `--icon assets/icon.ico`: Sets the application icon
- `--name "OpenSuperWhisper"`: Specifies the output filename
- `--add-data "assets;assets"`: Includes the entire assets directory in the executable

Once the build is complete, you'll find `OpenSuperWhisper.exe` in the `dist` folder on Windows, `OpenSuperWhisper.app` in the `dist` folder on macOS, or `OpenSuperWhisper` in the `dist` folder on Linux.

## Core and GUI Modules

The core module (`core`) is fully implemented and independent of the GUI, providing transcription, recording, instruction set, and hotkey management features that can be reused in other projects.

The GUI module (`gui`) leverages the core module to provide a user interface.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

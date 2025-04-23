# Open Super Whisper - Qt Remake

This project is a Qt implementation of the Open Super Whisper application, focusing on the GUI components. The actual transcription functionality is not fully implemented, but the interface and structure are completely set up.

## Features

- Complete PyQt6-based GUI implementation 
- Global hotkey support for starting/stopping recording
- Custom vocabulary and instruction sets management
- System tray integration
- Multiple language and model support
- Clipboard integration
- Status indicator window
- Settings management

## Project Structure

- `main.py` - Application entry point
- `src/` - Source code directory
  - `core/` - Core interfaces (no actual implementation)
    - `audio_recorder.py` - Audio recording interface
    - `hotkeys.py` - Global hotkey management
    - `instruction_sets.py` - Custom vocabulary and instructions
    - `whisper_api.py` - Transcription API interface
  - `gui/` - UI implementation
    - `components/` - Reusable UI components
      - `dialogs/` - Dialog windows
      - `widgets/` - Custom widgets
    - `resources/` - Application resources
      - `config.py` - Configuration settings
      - `labels.py` - UI text labels
    - `utils/` - Utility functions
      - `resource_helper.py` - Resource path resolver
    - `windows/` - Main application windows
      - `main_window.py` - Main application window
    - `main.py` - GUI entry point
- `assets/` - Application assets (icons, sounds)

## How to Run

This is a UI-only implementation without the actual transcription and recording functionality. To run the application:

```bash
python main.py
```

## Implementation Notes

This implementation focuses only on the GUI components using Qt. To make it fully functional, you would need to:

1. Implement the actual audio recording functionality in `src/core/audio_recorder.py`
2. Implement the actual whisper transcription API integration in `src/core/whisper_api.py`
3. Implement the actual global hotkey functionality in `src/core/hotkeys.py`

The current implementation provides placeholders for these functions that log actions but don't actually perform the operations.

## Requirements

- Python 3.8+
- PyQt6
- pynput (for global hotkeys)
- openai (for API integration)

# Update Open Super Whisper V2

## Remove Legacy Hotkey Recording Features
- [x] Identify all legacy hotkey recording functions in main_window.py
  - Legacy functions: `show_hotkey_dialog()`, `setup_global_hotkey()` (partially legacy)
  - Legacy toolbar button: "hotkey_action" in `create_toolbar()`
  - Legacy settings: `self.hotkey = self.settings.value("hotkey", AppConfig.DEFAULT_HOTKEY)`
- [x] Identify legacy hotkey recording features in hotkey_bridge.py
  - The `HotkeyBridge` class is not fully legacy, but has legacy recording hotkey references
- [x] Identify legacy hotkey recording features in HotkeyManager class
  - The core `HotkeyManager` class is not fully legacy, but has legacy recording features
- [ ] Remove legacy hotkey dialog from main toolbar
- [ ] Remove main recording hotkey references from MainWindow class
- [ ] Retain instruction set hotkey functionality
- [ ] Remove legacy hotkey dialog class (optional if not used elsewhere)

## Add Instruction Set Selection Dropdown to Main Window
- [ ] Add instruction set selection dropdown to the main control panel
- [ ] Connect the dropdown to the instruction set manager
- [ ] Implement dropdown change event handling to activate the selected instruction set
- [ ] Ensure the dropdown reflects the currently active instruction set
- [ ] Update the dropdown when instruction sets are modified

## Testing and Verification
- [ ] Verify the application runs without errors after changes
- [ ] Verify the instruction set selection dropdown works correctly
- [ ] Verify that the application no longer depends on legacy hotkey functionality

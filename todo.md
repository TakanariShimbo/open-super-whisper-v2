# Qt6 Thread Management Implementation Tasks

## Phase 1: Prepare Directory Structure and Basic Classes
- [x] 1.1. Create thread_management directory structure
  - [x] Create thread_management directory
  - [x] Create thread_management/__init__.py
  - [x] Create thread_management/workers directory
  - [x] Create thread_management/workers/__init__.py

- [x] 1.2. Implement thread_management/thread_manager.py
  - [x] Basic structure and initialization of ThreadManager class
  - [x] Signal definitions for thread-to-thread communication
  - [x] Timer management functionality
  - [x] Hotkey management functionality

- [x] 1.3. Implement thread_management/workers/task_worker.py
  - [x] Implement TaskWorker class for long-running task execution
  - [x] Add proper signal handling for task completion and failures

## Phase 2: Implement Supporting Classes
- [x] 2.1. Implement thread_management/hotkey_bridge.py
  - [x] Implement HotkeyBridge class with singleton pattern
  - [x] Thread-safe callback processing
  - [x] Integration with existing HotkeyManager

- [x] 2.2. Implement thread_management/ui_updater.py
  - [x] Implement UIUpdater class for centralized UI updates
  - [x] Status bar update functionality
  - [x] Recording indicator update functionality

## Phase 3: Integrate with MainWindow
- [x] 3.1. Review and cleanup existing thread management integration in MainWindow
  - [x] Review existing ThreadManager initialization
  - [x] Review existing UIUpdater initialization
  - [x] Review existing signal-slot connections
  - [x] Identify remaining direct timer and UI updates to replace

- [x] 3.2. Complete MainWindow integration (gui/windows/main_window.py)
  - [x] Replace deprecated update_recording_time method with ThreadManager methods
  - [x] Ensure all UI updates use UIUpdater instead of direct UI access
  - [x] Use Qt.ConnectionType.QueuedConnection consistently for cross-thread signals
  - [x] Replace QTimer.singleShot with ThreadManager.run_in_main_thread for thread-safe UI updates

- [x] 3.3. Modify StatusIndicatorWindow class (gui/components/widgets/status_indicator.py)
  - [x] Add thread-safe update methods
  - [x] Ensure proper connection with ThreadManager signals

## Phase 4: Testing and Refinement
- [ ] 4.1. Test Thread Management Implementation
  - [ ] Test timer functionality
  - [ ] Test hotkey processing
  - [ ] Test asynchronous task execution
  - [ ] Test UI updates

- [ ] 4.2. Address any issues discovered during testing
  - [ ] Fix timer-related issues
  - [ ] Fix hotkey-related issues
  - [ ] Fix thread safety issues

# Thread Management for Qt6 Applications

This module provides a robust thread management system for Qt6 applications, ensuring thread-safe operations and UI updates. It addresses common thread-related issues in Qt applications, especially those involving background processing, file I/O, and UI updates.

## Core Components

### 1. ThreadManager

The central hub for managing thread-to-thread communication and operations. Ensures that UI updates happen on the main (UI) thread and long-running tasks run in background threads.

Key features:
- Safe UI updates through `run_in_main_thread`
- Background processing with `run_in_worker_thread`
- Thread-safe timer management
- Centralized signal emission for cross-thread communication

### 2. UIUpdater

Provides centralized UI update functionality for status bars, indicators, and other UI elements. Ensures all UI updates happen on the main thread.

### 3. TaskWorker

Handles long-running tasks in background threads, reporting progress and results safely back to the main thread.

### 4. HotkeyBridge

Provides safe bridging between native hotkey events and the Qt UI thread.

## Thread Safety Guidelines

### General Rules

1. **Never manipulate UI from non-UI threads**
   - All UI operations must happen on the main thread
   - Use `ThreadManager.run_in_main_thread()` for UI updates from background threads

2. **Never block the UI thread**
   - Long-running operations should use `ThreadManager.run_in_worker_thread()`
   - File I/O, network requests, and heavy computations should be offloaded

3. **Use proper signal connections**
   - Always specify `Qt.ConnectionType.QueuedConnection` for cross-thread signals
   - Direct connections can be used for same-thread signals

4. **Avoid direct timer manipulation across threads**
   - Timers should be created, started, and stopped in the same thread
   - Use ThreadManager for timer operations

### Dialog Thread Safety

Dialogs must follow specific patterns to ensure thread safety:

1. **Message dialogs**
   - Use `SimpleMessageDialog` with thread_manager parameter
   - For asynchronous operations, use `show_message_async` or `show_confirmation_async`

2. **API Key validation**
   - Use `ThreadManager.run_in_worker_thread()` for network validation
   - Update UI with validation results using `ThreadManager.run_in_main_thread()`

3. **Hotkey configuration**
   - Register and unregister hotkeys through `HotkeyBridge`
   - Hotkey callbacks should be executed on the main thread

4. **Instruction Set operations**
   - Settings load/save should happen in background threads
   - UI list population and form updates must occur on the main thread

## Common Patterns

### Safe UI Updates

```python
# BAD - Direct update from background thread
def on_task_complete(self, result):
    self.status_bar.showMessage("Task complete")  # THREAD SAFETY VIOLATION

# GOOD - Thread-safe update using ThreadManager
def on_task_complete(self, result):
    self.thread_manager.run_in_main_thread(
        lambda: self.status_bar.showMessage("Task complete")
    )
```

### Background Processing

```python
# BAD - Blocking the UI thread
def process_file(self):
    with open(large_file, 'r') as f:
        data = f.read()  # UI FREEZES during file read
    self.process_data(data)

# GOOD - Non-blocking background processing
def process_file(self):
    def worker_task():
        with open(large_file, 'r') as f:
            return f.read()
            
    def on_read_complete(data):
        self.process_data(data)
        
    self.thread_manager.run_in_worker_thread(
        "file_read",
        worker_task,
        callback=on_read_complete
    )
```

### Showing Dialogs

```python
# BAD - Showing dialog from background thread
def show_error(self, message):
    QMessageBox.critical(self, "Error", message)  # THREAD SAFETY VIOLATION

# GOOD - Thread-safe dialog display
def show_error(self, message):
    SimpleMessageDialog.show_message(
        self,
        "Error",
        message,
        SimpleMessageDialog.ERROR,
        self.thread_manager
    )
```

## Known Limitations

1. QTimer instances must be created on the thread they will run on
2. Signal-slot connections with lambda functions may capture local variables incorrectly
3. Qt models (like QStandardItemModel) are not thread-safe and must be modified on the main thread

## Additional Resources

- [Qt Threading Basics](https://doc.qt.io/qt-6/thread-basics.html)
- [QThread Documentation](https://doc.qt.io/qt-6/qthread.html)
- [Signals and Slots Across Threads](https://doc.qt.io/qt-6/threads-qobject.html)

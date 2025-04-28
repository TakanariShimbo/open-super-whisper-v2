# LLM Clipboard Content Input Feature

## Research and Analysis
- [x] Understand the LLM input flow in the application
  - The `UnifiedProcessor` class in `core/processor.py` handles the processing flow
  - `process()` method takes audio transcription and passes it to LLM when enabled
  - Need to add a way to inject clipboard content before LLM processing
- [x] Identify where the LLM is started/initialized
  - LLM processing is done in `UnifiedProcessor.process()`
  - `LLMProcessor` class in `core/llm.py` handles the actual LLM interaction
- [x] Determine how to access clipboard content
  - Use `QApplication.clipboard()` to access the system clipboard
  - `setText()` to set clipboard content, `text()` to retrieve text
  - This should be done at the GUI layer to avoid Qt dependencies in core
- [x] Identify where in the instruction sets dialog to add clipboard option
  - Add as a checkbox in the LLM tab in `instruction_sets_dialog.py`
  - Need to update the `InstructionSet` class to store this preference

## Implementation Plan
- [x] Modify the `InstructionSet` class to include clipboard paste option
  - Added `llm_clipboard_enabled` field to `InstructionSet` dataclass
  - Updated relevant methods in `InstructionSetManager`
- [x] Update the `GUIInstructionSetManager` to handle the new setting
  - Ensured serialization/deserialization includes the new field
- [x] Update `instruction_sets_dialog.py` UI to add checkbox for clipboard option
  - Added a checkbox in the LLM tab section
  - Updated UI handlers to save/load the setting
- [x] Modify `UnifiedProcessor` to handle clipboard content
  - Added a new parameter to `process()` method to accept clipboard text
  - Combined with transcription text before sending to LLM
- [x] Update main_window.py to pass clipboard content to the processor
  - Retrieved clipboard content when LLM is starting in `start_processing` method
  - Passed clipboard content to the processor if enabled for active instruction set
  - Updated `perform_processing` method to handle the clipboard content parameter

## Testing and Documentation
- [x] Test the feature in different scenarios
  - Tested with empty clipboard
  - Tested with text-only clipboard
  - Tested with combination of transcription and clipboard content
  - Tested enabling/disabling the feature
- [x] Update documentation if necessary
  - The code is self-documenting with appropriate comments and docstrings
  - Parameter documentation was added to method signatures

## Summary
The implementation allows users to include clipboard content when using LLM processing. A checkbox in the instruction set dialog controls whether clipboard content should be included when starting the LLM. When enabled, the clipboard text is combined with the transcription and sent to the LLM as a unified input. This gives users the flexibility to provide additional context or instructions to the LLM that complement the audio transcription.

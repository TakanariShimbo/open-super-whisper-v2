# LLM Clipboard Image Input Feature

## Research and Analysis
- [x] Understand how to access clipboard images in PyQt6
  - Use QApplication.clipboard().image() to get QImage from clipboard
  - Check for empty/valid images using QImage.isNull()
  - Can use QApplication.clipboard().mimeData() to check available formats
- [x] Determine how to handle images for OpenAI API
  - OpenAI GPT-4o model accepts base64-encoded images
  - Need to convert QImage to QByteArray using QBuffer, then encode to base64
  - Format for API: {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,BASE64_STRING"}}
  - Need to include image in the messages array along with text
- [x] Identify needed changes to the LLMProcessor class
  - Current implementation uses chat.completions.create() for text-only processing
  - Need to add capability to handle images in content array
  - Must update process() method to accept optional image parameter
  - Need to use GPT-4o model for both text and image content
  - Need to ensure backward compatibility for text-only processing
- [x] Examine the InstructionSet implementation
  - Confirmed InstructionSet already has llm_clipboard_enabled flag that can be reused
  - No need to modify the InstructionSet class since the flag is just controlling whether to include clipboard content
  - The clipboard content type detection will be handled at runtime in main_window.py

## Implementation Plan
- [x] Update the UnifiedProcessor class to handle image input
  - Added clipboard_image parameter to process() method
  - Modified LLM input preparation to include image data
- [x] Modify the LLMProcessor class to support images
  - Updated the process() method to accept optional image_data parameter 
  - Implemented base64 encoding for images with proper import
  - Configured the correct API format for GPT-4o image and text inputs
- [x] Update the main_window.py to detect and pass clipboard images
  - Added get_clipboard_content() method to detect and convert clipboard images
  - Modified start_processing to check for and handle both text and images
  - Updated perform_processing to accept and handle clipboard_image parameter
- [x] Add proper error handling for image processing
  - Added checks for image.isNull() to avoid processing invalid images
  - Ensured graceful handling of clipboard content with robust error handling

## Testing and Documentation
- [x] Add appropriate documentation
  - Added docstrings and comments to all new and modified methods
  - Updated parameter descriptions in method signatures
  - Made sure code is self-documenting with clear variable names

## Final Testing
- [ ] Test the feature with different scenarios
  - Test with text-only clipboard
  - Test with image-only clipboard
  - Test with clipboard containing both text and image
  - Test enabling/disabling the feature
  - Test with various image types (JPG, PNG) and sizes

## Model Optimization
- [x] Update to use only GPT-4o model
  - Modified LLMModelManager to only include GPT-4o model
  - Updated LLMProcessor to always use GPT-4o for both text and images
  - Modified text/image format to be compatible with GPT-4o API
  - Updated UnifiedProcessor class to use GPT-4o as default
  - Updated docstrings to reflect the model change

## Summary
The implementation allows users to include clipboard images when using LLM processing. The existing checkbox in the instruction set dialog controls whether clipboard content should be included when starting the LLM. When enabled, the clipboard image and/or text is processed with the transcription and sent to the LLM (using the GPT-4o model) as a unified input. GPT-4o was selected as the exclusive model because it efficiently handles both text and image inputs. This gives users the flexibility to provide visual context or additional information to the LLM that complements the audio transcription.


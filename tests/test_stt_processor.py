#!/usr/bin/env python3
"""
Command-line test for STTProcessor

This test verifies the functionality of the STTProcessor class
from the new_core.stt module.
"""

import os
import sys
import argparse
import time

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from new_core.stt.stt_processor import STTProcessor


def test_stt_processor(audio_file_path: str, api_key: str = None, 
                       model_id: str = "gpt-4o-transcribe", language: str = None,
                       vocabulary: str = None, instruction: str = None):
    """
    Test STTProcessor functionality
    
    Parameters
    ----------
    audio_file_path : str
        Path to the audio file to transcribe
    api_key : str, optional
        OpenAI API key, by default None (will use environment variable)
    model_id : str, optional
        STT model ID to use, by default "gpt-4o-transcribe"
    language : str, optional
        Language code (e.g., "en", "ja"), by default None (auto-detect)
    vocabulary : str, optional
        Custom vocabulary to improve transcription, by default None
    instruction : str, optional
        System instruction for transcription, by default None
    """
    print(f"Testing STTProcessor with file: {audio_file_path}")
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: File {audio_file_path} does not exist")
        return 1

    # Get file size
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    
    try:
        # Initialize processor
        print(f"Initializing STTProcessor with model: {model_id}")
        processor = STTProcessor(api_key=api_key, model_id=model_id)
        
        # Set custom vocabulary if provided
        if vocabulary:
            print(f"Setting custom vocabulary: {vocabulary}")
            processor.set_custom_vocabulary(vocabulary)
        
        # Set system instruction if provided
        if instruction:
            print(f"Setting system instruction: {instruction}")
            processor.set_system_instruction(instruction)
            
        # Process the audio file
        print(f"Starting transcription (language: {language or 'auto-detect'})...")
        start_time = time.time()
        
        transcription = processor.transcribe_file_with_chunks(audio_file_path, language)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Print results
        print("\nTranscription completed")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Transcription length: {len(transcription)} characters")
        
        print("\nTranscription result:")
        print("-" * 40)
        print(transcription)
        print("-" * 40)
        
        return 0
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test STTProcessor functionality")
    
    parser.add_argument(
        "audio_file", 
        help="Path to the audio file to transcribe"
    )
    
    parser.add_argument(
        "--api-key", 
        help="OpenAI API key (optional, will use environment variable if not provided)"
    )
    
    parser.add_argument(
        "--model", 
        default="gpt-4o-transcribe",
        help="STT model ID (default: gpt-4o-transcribe)"
    )
    
    parser.add_argument(
        "--language", 
        help="Language code (e.g., 'en', 'ja') or None for auto-detection"
    )
    
    parser.add_argument(
        "--vocabulary", 
        help="Custom vocabulary to improve transcription"
    )
    
    parser.add_argument(
        "--instruction", 
        help="System instruction for transcription"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_stt_processor(
        args.audio_file, 
        args.api_key, 
        args.model, 
        args.language, 
        args.vocabulary, 
        args.instruction
    )
    
    # Return the result code
    sys.exit(result)

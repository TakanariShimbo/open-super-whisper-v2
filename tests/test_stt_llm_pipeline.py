#!/usr/bin/env python3
"""
Command-line test for Pipeline

This test verifies the functionality of the Pipeline class
from the core.pipelines module.
"""

import os
import sys
import argparse
import time

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipelines.pipeline import Pipeline


def stream_callback(chunk: str) -> None:
    """
    Callback function for streaming LLM output
    
    Parameters
    ----------
    chunk : str
        Text chunk from the LLM
    """
    print(chunk, end="", flush=True)


def test_pipeline(audio_file_path: str, api_key: str = None, 
                 stt_model: str = "gpt-4o-transcribe", llm_model: str = "gpt-4o",
                 language: str = None, stream: bool = False, 
                 llm_enabled: bool = True, with_image: bool = False,
                 image_file_path: str = None):
    """
    Test Pipeline functionality
    
    Parameters
    ----------
    audio_file_path : str
        Path to the audio file to process
    api_key : str, optional
        OpenAI API key, by default None (will use environment variable)
    stt_model : str, optional
        STT model ID to use, by default "gpt-4o-transcribe"
    llm_model : str, optional
        LLM model ID to use, by default "gpt-4o"
    language : str, optional
        Language code for transcription, by default None (auto-detect)
    stream : bool, optional
        Whether to use streaming API for LLM, by default False
    llm_enabled : bool, optional
        Whether to enable LLM processing, by default True
    with_image : bool, optional
        Whether to include image data, by default False
    image_file_path : str, optional
        Path to an image file to include in the LLM context, by default None
    """
    print(f"Testing Pipeline with file: {audio_file_path}")
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: File {audio_file_path} does not exist")
        return 1

    # Get file size
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    
    try:
        # Initialize pipeline
        print(f"Initializing pipeline with STT model: {stt_model}, LLM model: {llm_model}")
        pipeline = Pipeline(api_key=api_key)
        pipeline.set_stt_model(stt_model)
        pipeline.set_llm_model(llm_model)
        
        # Set LLM processing
        pipeline.enable_llm_processing(llm_enabled)
        print(f"LLM processing enabled: {llm_enabled}")
        
        # Set some system instructions
        stt_instruction = "Transcribe accurately with proper punctuation."
        llm_instruction = "You are an assistant that analyzes transcribed audio. Keep your responses brief and focused."
        
        pipeline.set_stt_instruction(stt_instruction)
        pipeline.set_llm_instruction(llm_instruction)
        
        print(f"Set STT instruction: '{stt_instruction}'")
        print(f"Set LLM instruction: '{llm_instruction}'")
        
        # Prepare optional parameters
        clipboard_text = "This is sample clipboard text for context." if llm_enabled else None
        clipboard_image = None
        
        # Handle image data
        if with_image and llm_enabled:
            if image_file_path and os.path.exists(image_file_path):
                try:
                    with open(image_file_path, 'rb') as img_file:
                        clipboard_image = img_file.read()
                    print(f"Using image file: {image_file_path}")
                except Exception as e:
                    print(f"Error reading image file: {str(e)}")
                    return 1
            else:
                print("Error: --with-image requires a valid image file path using --image-file parameter")
                return 1
        
        callback = stream_callback if stream and llm_enabled else None
        
        if clipboard_text:
            print(f"Using clipboard text: '{clipboard_text}'")

        
        # Process the audio file
        print(f"Starting pipeline processing (language: {language or 'auto-detect'})...")
        start_time = time.time()
        
        result = pipeline.process(
            audio_file_path=audio_file_path,
            language=language,
            clipboard_text=clipboard_text,
            clipboard_image=clipboard_image,
            stream_callback=callback
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Print results
        print("\nPipeline processing completed")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Transcription length: {len(result.transcription)} characters")
        
        if result.llm_processed:
            print(f"LLM response length: {len(result.llm_response)} characters")
        
        print("\nTranscription result:")
        print("-" * 40)
        print(result.transcription)
        print("-" * 40)
        
        if result.llm_processed and not stream:
            print("\nLLM response:")
            print("-" * 40)
            print(result.llm_response)
            print("-" * 40)
            
        return 0
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test Pipeline functionality")
    
    parser.add_argument(
        "audio_file", 
        help="Path to the audio file to process"
    )
    
    parser.add_argument(
        "--api-key", 
        help="OpenAI API key (optional, will use environment variable if not provided)"
    )
    
    parser.add_argument(
        "--stt-model", 
        default="gpt-4o-transcribe",
        help="STT model ID (default: gpt-4o-transcribe)"
    )
    
    parser.add_argument(
        "--llm-model", 
        default="gpt-4o",
        help="LLM model ID (default: gpt-4o)"
    )
    
    parser.add_argument(
        "--language", 
        help="Language code (e.g., 'en', 'ja') or None for auto-detection"
    )
    
    parser.add_argument(
        "--stream", 
        action="store_true",
        help="Use streaming API for LLM responses"
    )
    
    parser.add_argument(
        "--no-llm", 
        action="store_true",
        help="Disable LLM processing (transcription only)"
    )
    
    parser.add_argument(
        "--with-image", 
        action="store_true",
        help="Include image data in LLM context (requires --image-file parameter)"
    )
    
    parser.add_argument(
        "--image-file",
        help="Path to an image file to include in the LLM context"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # If image file is provided, automatically enable with-image flag
    if args.image_file:
        args.with_image = True
    
    # Run the test
    result = test_pipeline(
        args.audio_file, 
        args.api_key, 
        args.stt_model, 
        args.llm_model, 
        args.language, 
        args.stream, 
        not args.no_llm,
        args.with_image,
        args.image_file
    )
    
    # Return the result code
    sys.exit(result)

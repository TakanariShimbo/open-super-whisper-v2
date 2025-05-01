#!/usr/bin/env python3
"""
Command-line test for LLMProcessor

This test verifies the functionality of the LLMProcessor class
from the new_core.llm module.
"""

import os
import sys
import argparse
import time

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from new_core.llm.llm_processor import LLMProcessor


def stream_callback(chunk: str) -> None:
    """
    Callback function for streaming LLM output
    
    Parameters
    ----------
    chunk : str
        Text chunk from the LLM
    """
    print(chunk, end="", flush=True)


def test_llm_processor(text: str, api_key: str = None, model_id: str = "gpt-4o", 
                      image_path: str = None, instruction: str = None, stream: bool = False):
    """
    Test LLMProcessor functionality
    
    Parameters
    ----------
    text : str
        Text to process with the LLM
    api_key : str, optional
        OpenAI API key, by default None (will use environment variable)
    model_id : str, optional
        LLM model ID to use, by default "gpt-4o"
    image_path : str, optional
        Path to image file for multimodal processing, by default None
    instruction : str, optional
        System instruction to control LLM behavior, by default None
    stream : bool, optional
        Whether to use streaming API, by default False
    """
    print(f"Testing LLMProcessor with model: {model_id}")
    
    # Check if image exists
    image_data = None
    if image_path:
        if not os.path.exists(image_path):
            print(f"Error: Image file {image_path} does not exist")
            return 1
        
        # Read image data
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        print(f"Loaded image: {image_path}")
    
    try:
        # Initialize processor
        print("Initializing LLMProcessor...")
        processor = LLMProcessor(api_key=api_key, model_id=model_id)
        
        # Set system instruction if provided
        if instruction:
            print(f"Setting system instruction: {instruction}")
            processor.set_system_instruction(instruction)
        
        # Process the text
        print(f"Processing text with LLM (streaming: {stream})...")
        start_time = time.time()
        
        if stream:
            print("\nLLM response:")
            print("-" * 40)
            response = processor.process_text_with_stream(text, stream_callback, image_data)
            print("\n" + "-" * 40)
        else:
            response = processor.process_text(text, image_data)
            print("\nLLM response:")
            print("-" * 40)
            print(response)
            print("-" * 40)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Print timing results
        print(f"\nProcessing completed in {elapsed_time:.2f} seconds")
        print(f"Response length: {len(response)} characters")
        
        return 0
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test LLMProcessor functionality")
    
    parser.add_argument(
        "text", 
        help="Text to process with the LLM"
    )
    
    parser.add_argument(
        "--api-key", 
        help="OpenAI API key (optional, will use environment variable if not provided)"
    )
    
    parser.add_argument(
        "--model", 
        default="gpt-4o",
        help="LLM model ID (default: gpt-4o)"
    )
    
    parser.add_argument(
        "--image", 
        help="Path to image file for multimodal processing"
    )
    
    parser.add_argument(
        "--instruction", 
        help="System instruction to control LLM behavior"
    )
    
    parser.add_argument(
        "--stream", 
        action="store_true",
        help="Use streaming API"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_llm_processor(
        args.text, 
        args.api_key, 
        args.model, 
        args.image, 
        args.instruction, 
        args.stream
    )
    
    # Return the result code
    sys.exit(result)

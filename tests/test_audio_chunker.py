#!/usr/bin/env python3
"""
Command-line test for AudioChunker

This test verifies the functionality of the AudioChunker class
from the core.stt module.
"""

import os
import sys
import argparse

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stt.audio_chunker import AudioChunker


def test_audio_chunking(audio_file_path: str, max_size_mb: float = 24.0, verbose: bool = False):
    """
    Test audio chunking functionality
    
    Parameters
    ----------
    audio_file_path : str
        Path to the audio file to chunk
    max_size_mb : float, optional
        Maximum chunk size in MB, by default 24.0
    verbose : bool, optional
        Whether to output verbose information, by default False
    """
    print(f"Testing AudioChunker with file: {audio_file_path}")
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: File {audio_file_path} does not exist")
        return 1

    # Get file size
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    
    # Create chunker with optional custom max size
    chunker = AudioChunker(max_chunk_size_mb=max_size_mb)
    
    try:
        # Process the audio file
        print("Chunking audio file...")
        chunk_paths = chunker.chunk_audio_file(audio_file_path)
        
        # Get results
        print(f"Created {len(chunk_paths)} chunks:")
        
        for i, chunk_path in enumerate(chunk_paths):
            chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
            print(f"  Chunk {i+1}: {os.path.basename(chunk_path)} - {chunk_size_mb:.2f} MB")
            
            # Print more info if verbose
            if verbose:
                print(f"    Full path: {chunk_path}")
        
        print("\nChunking completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during chunking: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test AudioChunker functionality")
    
    parser.add_argument(
        "audio_file", 
        help="Path to the audio file to chunk"
    )
    
    parser.add_argument(
        "--max-size", 
        type=float, 
        default=24.0,
        help="Maximum chunk size in MB (default: 24.0)"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_audio_chunking(args.audio_file, args.max_size, args.verbose)
    
    # Return the result code
    sys.exit(result)

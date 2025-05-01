#!/usr/bin/env python3
"""
Command-line test for STTModel

This test verifies the functionality of the STTModel class
from the core.stt module.
"""

import os
import sys
import argparse

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stt.stt_model import STTModel


def test_stt_model(verbose: bool = False):
    """
    Test STTModel functionality
    
    Parameters
    ----------
    verbose : bool, optional
        Whether to output detailed model information, by default False
    """
    print("Testing STTModel creation and methods")
    
    try:
        # Create sample models
        models = [
            STTModel(
                id="gpt-4o-transcribe",
                name="GPT-4o Transcribe",
                description="Transcription model based on GPT-4o",
                performance_tier="premium",
                is_default=True
            ),
            STTModel(
                id="whisper-1",
                name="Whisper v1",
                description="OpenAI's Whisper model",
                performance_tier="standard",
                is_default=False
            )
        ]
        
        print(f"Created {len(models)} sample STT models:")
        
        for i, model in enumerate(models):
            print(f"\nModel {i+1}:")
            print(f"  ID: {model.id}")
            print(f"  Name: {model.name}")
            print(f"  Performance Tier: {model.performance_tier}")
            print(f"  Is Default: {model.is_default}")
            
            if verbose:
                print(f"  Description: {model.description}")
        
        # Test string representation
        print("\nTesting string representation:")
        print(f"  str(model): {str(models[0])}")
        print(f"  repr(model): {repr(models[0])}")
        
        # Test equality check
        print("\nTesting equality check:")
        same_model = STTModel(
            id=models[0].id,
            name=models[0].name,
            description=models[0].description,
            performance_tier=models[0].performance_tier,
            is_default=models[0].is_default
        )
        
        print(f"  Original model == Same model: {models[0] == same_model}")
        print(f"  Original model == Different model: {models[0] == models[1]}")
            
        print("\nTesting completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test STTModel functionality")
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed model information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_stt_model(args.verbose)
    
    # Return the result code
    sys.exit(result)

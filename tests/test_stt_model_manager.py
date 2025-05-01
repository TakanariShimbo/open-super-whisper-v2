#!/usr/bin/env python3
"""
Command-line test for STTModelManager

This test verifies the functionality of the STTModelManager class
from the core.stt module.
"""

import os
import sys
import argparse
import json

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stt.stt_model_manager import STTModelManager


def test_model_manager(verbose: bool = False):
    """
    Test STTModelManager functionality
    
    Parameters
    ----------
    verbose : bool, optional
        Whether to output detailed model information, by default False
    """
    print("Testing STTModelManager")
    
    try:
        # Get available models
        models = STTModelManager.get_available_models()
        print(f"Found {len(models)} available STT models:")
        
        for i, model in enumerate(models):
            print(f"  {i+1}. {model.name}")
            
            if verbose:
                print(f"     ID: {model.id}")
                print(f"     Performance Tier: {model.performance_tier}")
                print(f"     Description: {model.description}")
                print(f"     Is Default: {model.is_default}")
                print("")
        
        # Test API format conversion
        api_format = STTModelManager.to_api_format()
        print(f"\nAPI Format contains {len(api_format)} models")
        
        if verbose:
            print("API Format:")
            print(json.dumps(api_format, indent=2))
        
        # Test looking up a model by ID directly from the model ID map
        test_id = models[0].id if models else "gpt-4o-transcribe"
        found_model = STTModelManager._STT_MODEL_ID_MAP.get(test_id)
        
        if found_model:
            print(f"\nSuccessfully found model with ID: {test_id}")
            print(f"  Name: {found_model.name}")
            print(f"  Performance Tier: {found_model.performance_tier}")
        else:
            print(f"\nCould not find model with ID: {test_id}")
            
        print("\nTesting completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test STTModelManager functionality")
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed model information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_model_manager(args.verbose)
    
    # Return the result code
    sys.exit(result)

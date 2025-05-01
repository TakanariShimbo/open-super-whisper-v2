#!/usr/bin/env python3
"""
Command-line test for LLMModelManager

This test verifies the functionality of the LLMModelManager class
from the core.llm module.
"""

import os
import sys
import argparse
import json

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.llm_model_manager import LLMModelManager


def test_model_manager(verbose: bool = False):
    """
    Test LLMModelManager functionality
    
    Parameters
    ----------
    verbose : bool, optional
        Whether to output detailed model information, by default False
    """
    print("Testing LLMModelManager")
    
    try:
        # Get available models
        models = LLMModelManager.get_available_models()
        print(f"Found {len(models)} available LLM models:")
        
        for i, model in enumerate(models):
            print(f"  {i+1}. {model.name}")
            
            if verbose:
                print(f"     ID: {model.id}")
                print(f"     Performance Tier: {model.performance_tier}")
                print(f"     Description: {model.description}")
                print(f"     Supports Image: {model.supports_image}")
                print(f"     Is Default: {model.is_default}")
                print("")
        
        # Test API format conversion
        api_format = LLMModelManager.to_api_format()
        print(f"\nAPI Format contains {len(api_format)} models")
        
        if verbose:
            print("API Format:")
            print(json.dumps(api_format, indent=2))
        
        # Test finding models
        test_id = models[0].id if models else "gpt-4o"
        found_model = LLMModelManager.find_model_by_id(test_id)
        
        if found_model:
            print(f"\nSuccessfully found model with ID: {test_id}")
            print(f"  Name: {found_model.name}")
            print(f"  Supports Image: {found_model.supports_image}")
        else:
            print(f"\nCould not find model with ID: {test_id}")
            
        # Test getting image-capable models
        image_models = [model for model in models if model.supports_image]
        print(f"\nFound {len(image_models)} image-capable models:")
        
        for i, model in enumerate(image_models):
            print(f"  {i+1}. {model.name} ({model.id})")
            
        print("\nTesting completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test LLMModelManager functionality")
    
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

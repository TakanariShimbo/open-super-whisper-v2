#!/usr/bin/env python3
"""
Command-line test for LLMModel

This test verifies the functionality of the LLMModel class
from the core.llm module.
"""

import os
import sys
import argparse

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.llm_model import LLMModel


def test_llm_model(verbose: bool = False):
    """
    Test LLMModel functionality
    
    Parameters
    ----------
    verbose : bool, optional
        Whether to output detailed model information, by default False
    """
    print("Testing LLMModel creation and methods")
    
    try:
        # Create sample models
        models = [
            LLMModel(
                id="gpt-4o",
                name="GPT-4o",
                description="OpenAI's multimodal LLM model",
                performance_tier="premium",
                supports_image=True,
                is_default=True
            ),
            LLMModel(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="OpenAI's efficient LLM model",
                performance_tier="standard",
                supports_image=False,
                is_default=False
            )
        ]
        
        print(f"Created {len(models)} sample LLM models:")
        
        for i, model in enumerate(models):
            print(f"\nModel {i+1}:")
            print(f"  ID: {model.id}")
            print(f"  Name: {model.name}")
            print(f"  Performance Tier: {model.performance_tier}")
            print(f"  Supports Image: {model.supports_image}")
            print(f"  Is Default: {model.is_default}")
            
            if verbose:
                print(f"  Description: {model.description}")
        
        # Test string representation
        print("\nTesting string representation:")
        print(f"  str(model): {str(models[0])}")
        print(f"  repr(model): {repr(models[0])}")
        
        # Test model equality check
        print("\nTesting equality check:")
        same_model = LLMModel(
            id=models[0].id,
            name=models[0].name,
            description=models[0].description,
            performance_tier=models[0].performance_tier,
            supports_image=models[0].supports_image,
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
    parser = argparse.ArgumentParser(description="Test LLMModel functionality")
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed model information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_llm_model(args.verbose)
    
    # Return the result code
    sys.exit(result)

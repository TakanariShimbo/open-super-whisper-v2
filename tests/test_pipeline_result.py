#!/usr/bin/env python3
"""
Command-line test for PipelineResult

This test verifies the functionality of the PipelineResult class
from the core.pipelines module.
"""

import os
import sys
import argparse

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipelines.pipeline_result import PipelineResult


def test_pipeline_result(verbose: bool = False):
    """
    Test PipelineResult functionality
    
    Parameters
    ----------
    verbose : bool, optional
        Whether to output detailed result information, by default False
    """
    print("Testing PipelineResult creation and methods")
    
    try:
        # Test initialization with transcription only
        trans_result = PipelineResult(transcription="This is a test transcription.")
        print(f"\nCreated result with transcription:")
        print(f"  Transcription: '{trans_result.transcription}'")
        print(f"  LLM Response: '{trans_result.llm_response}'")
        print(f"  LLM Processed: {trans_result.llm_processed}")
        
        # Test initialization with all fields
        full_result = PipelineResult(
            transcription="This is a test transcription.",
            llm_response="This is a test LLM response.",
            llm_processed=True
        )
        print(f"\nCreated result with all fields:")
        print(f"  Transcription: '{full_result.transcription}'")
        print(f"  LLM Response: '{full_result.llm_response}'")
        print(f"  LLM Processed: {full_result.llm_processed}")
        
        # Test get_combined_output method
        combined_output = full_result.get_combined_output()
        print(f"\nCombined output:")
        if verbose:
            print(combined_output)
        else:
            print(f"  Length: {len(combined_output)} characters")
        
        # Test get_combined_output with transcription only
        trans_only_output = trans_result.get_combined_output()
        print(f"\nTranscription-only combined output:")
        if verbose:
            print(trans_only_output)
        else:
            print(f"  Length: {len(trans_only_output)} characters")
        
        # Test direct comparison
        print(f"\nTesting equality check:")
        print(f"  Same content == Same content: {full_result == PipelineResult(transcription=full_result.transcription, llm_response=full_result.llm_response, llm_processed=full_result.llm_processed)}")
        print(f"  Full result == Transcription only: {full_result == trans_result}")
            
        print("\nTesting completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test PipelineResult functionality")
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed result information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_pipeline_result(args.verbose)
    
    # Return the result code
    sys.exit(result)

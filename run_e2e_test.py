#!/usr/bin/env python3
"""End-to-end test runner for Paper2Repo."""
import sys
from pathlib import Path
from paper2repo.workflows.pipeline_orchestrator import PipelineOrchestrator


def main():
    """Run end-to-end test."""
    print("=" * 60)
    print("Paper2Repo End-to-End Test")
    print("=" * 60)
    
    # Sample test document
    test_doc = """
    # Machine Learning Algorithm
    
    This paper presents a simple classification algorithm.
    
    ## Algorithm
    1. Load data
    2. Train model
    3. Evaluate
    """
    
    # Create output directory
    output_dir = Path('./test_output')
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nOutput directory: {output_dir}")
    
    try:
        # Initialize pipeline
        print("\nInitializing pipeline...")
        pipeline = PipelineOrchestrator(
            output_dir=output_dir,
            total_token_budget=100000  # Lower budget for testing
        )
        
        # Prepare input
        input_data = {
            'document_text': test_doc,
            'document_id': 'test_paper',
            'user_input': 'Generate a simple Python implementation'
        }
        
        # Run pipeline
        print("\nRunning pipeline (this may take a moment)...")
        results = pipeline.run(input_data)
        
        # Display results
        print("\n" + "=" * 60)
        print("Results:")
        print("=" * 60)
        
        print(f"\nSuccess: {results['success']}")
        
        if results.get('token_budget'):
            budget = results['token_budget']
            print(f"Token Usage: {budget['used_tokens']:,} / {budget['total_budget']:,}")
            print(f"Utilization: {budget['utilization']:.1%}")
        
        print("\nPhases completed:")
        for phase_name in results.get('phases', {}).keys():
            print(f"  ✓ {phase_name}")
        
        if results.get('artifacts', {}).get('code_files'):
            files = results['artifacts']['code_files'].get('generated_files', [])
            print(f"\nGenerated {len(files)} files:")
            for file_info in files:
                print(f"  - {file_info['path']}")
        
        print("\n" + "=" * 60)
        
        if results['success']:
            print("✅ End-to-end test PASSED")
            return 0
        else:
            print("❌ End-to-end test FAILED")
            return 1
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

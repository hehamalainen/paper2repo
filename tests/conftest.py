"""Test configuration and fixtures."""
import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_document_text():
    """Sample research paper text."""
    return """
    # Neural Network Architecture
    
    ## Abstract
    This paper presents a novel neural network architecture for image classification.
    
    ## Introduction
    Deep learning has revolutionized computer vision tasks. We propose an efficient
    architecture that combines convolutional and attention mechanisms.
    
    ## Method
    Our approach uses a three-layer convolutional network followed by multi-head
    attention. The algorithm can be described as:
    
    1. Apply convolution layers
    2. Apply batch normalization
    3. Apply attention mechanism
    4. Output classification
    
    ## Results
    We achieve 95% accuracy on the test dataset.
    """


@pytest.fixture
def sample_user_input():
    """Sample user input."""
    return "Generate a Python implementation of the neural network from the paper"


@pytest.fixture
def sample_blueprint():
    """Sample blueprint structure."""
    return {
        'project_file_hierarchy': {
            'root': 'neural_net',
            'files': [
                {'path': 'model.py', 'purpose': 'Neural network model'},
                {'path': 'train.py', 'purpose': 'Training script'},
                {'path': 'README.md', 'purpose': 'Documentation'}
            ]
        },
        'component_specification': {
            'components': [
                {
                    'name': 'NeuralNetwork',
                    'type': 'class',
                    'purpose': 'Main model class'
                }
            ]
        },
        'verification_protocol': {
            'test_strategy': 'unit_testing',
            'test_files': ['test_model.py']
        },
        'execution_environment': {
            'language': 'python',
            'version': '3.11',
            'dependencies': {'numpy': '1.24.0'}
        },
        'staged_development_plan': {
            'phases': [
                {'phase_id': 'p1', 'name': 'Core', 'tasks': ['model']}
            ]
        },
        'build_order': ['model.py', 'train.py'],
        'entrypoints': [
            {'name': 'train', 'file': 'train.py'}
        ],
        'traceability_matrix': {
            'mappings': [
                {
                    'concept_id': 'neural_network',
                    'component': 'NeuralNetwork',
                    'rationale': 'Core model'
                }
            ]
        }
    }

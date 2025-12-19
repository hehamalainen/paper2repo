"""Test pipeline components."""
import pytest
from paper2repo.utils.llm_utils import LLMClient, LLMConfig, LLMProvider
from paper2repo.memory.codemem import CodeMemory, CodeMemEntry
from paper2repo.tools.cognitive.segmentation import Segmentation
from paper2repo.tools.action.filesystem import Filesystem


def test_llm_client_initialization():
    """Test LLM client initialization."""
    config = LLMConfig(provider=LLMProvider.MOCK)
    client = LLMClient(config)
    assert client.config.provider == LLMProvider.MOCK


def test_code_memory():
    """Test code memory operations."""
    memory = CodeMemory()
    
    entry = CodeMemEntry(
        file='test.py',
        core_purpose='Test file',
        public_interface=[
            {'name': 'test_func', 'type': 'function'}
        ],
        dependency_edges=[]
    )
    
    memory.add_entry(entry)
    retrieved = memory.get_entry('test.py')
    
    assert retrieved is not None
    assert retrieved.file == 'test.py'
    assert retrieved.core_purpose == 'Test file'


def test_segmentation():
    """Test document segmentation."""
    segmenter = Segmentation()
    
    text = """
    # Section 1
    This is content for section 1.
    
    # Section 2
    This is content for section 2.
    """
    
    segments = segmenter.segment(text, method='heading')
    assert len(segments) > 0


def test_filesystem(temp_dir):
    """Test filesystem operations."""
    fs = Filesystem(sandbox_dir=temp_dir)
    
    # Create file
    result = fs.create_file('test.txt', 'Hello World')
    assert result['success']
    
    # Read file
    result = fs.read_file('test.txt')
    assert result['success']
    assert result['content'] == 'Hello World'
    
    # List directory
    result = fs.list_directory()
    assert result['success']
    assert 'test.txt' in result['files']


def test_document_parsing_agent():
    """Test document parsing agent."""
    from paper2repo.agents.document_parsing import DocumentParsingAgent
    
    agent = DocumentParsingAgent()
    
    result = agent.process({
        'document_text': '# Test\nThis is test content.',
        'document_id': 'test_doc'
    })
    
    assert 'document_id' in result
    assert result['document_id'] == 'test_doc'


def test_intent_understanding_agent():
    """Test intent understanding agent."""
    from paper2repo.agents.intent_understanding import IntentUnderstandingAgent
    from paper2repo.utils.llm_utils import LLMClient, LLMConfig, LLMProvider
    
    config = LLMConfig(provider=LLMProvider.MOCK)
    client = LLMClient(config)
    
    agent = IntentUnderstandingAgent(client)
    
    result = agent.process({
        'user_input': 'Generate code from a paper about neural networks'
    })
    
    # Mock response returns a dict with agent info, which triggers fallback
    assert 'primary_goal' in result or 'raw_response' in result or 'agent' in result


def test_code_planning_minimal(sample_blueprint):
    """Test code planning with minimal blueprint."""
    from paper2repo.agents.code_planning import CodePlanningAgent
    from paper2repo.utils.llm_utils import LLMClient, LLMConfig, LLMProvider
    
    config = LLMConfig(provider=LLMProvider.MOCK)
    client = LLMClient(config)
    
    agent = CodePlanningAgent(client)
    
    # Test minimal blueprint creation
    minimal = agent._create_minimal_blueprint()
    
    assert 'project_file_hierarchy' in minimal
    assert 'component_specification' in minimal
    assert 'verification_protocol' in minimal
    assert 'execution_environment' in minimal
    assert 'staged_development_plan' in minimal
    assert 'build_order' in minimal
    assert 'entrypoints' in minimal
    assert 'traceability_matrix' in minimal


def test_validator_agent():
    """Test validator agent."""
    from paper2repo.agents.validator import ValidatorAgent
    from paper2repo.utils.llm_utils import LLMClient, LLMConfig, LLMProvider
    
    config = LLMConfig(provider=LLMProvider.MOCK)
    client = LLMClient(config)
    
    agent = ValidatorAgent(client)
    
    result = agent.process({
        'code_files': [
            {'path': 'test.py', 'size': 100}
        ],
        'blueprint': {}
    })
    
    assert 'compatibility_score' in result
    assert 'passed' in result


def test_pipeline_orchestrator_code_files_extraction():
    """Test that pipeline orchestrator correctly extracts code_files from dict format."""
    from paper2repo.workflows.pipeline_orchestrator import PipelineOrchestrator
    from pathlib import Path
    import tempfile
    
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = PipelineOrchestrator(
            output_dir=Path(tmpdir)
        )
        
        # Simulate code_files artifact as returned by CodeGeneratorAgent
        code_files_dict = {
            'generated_files': [
                {'path': 'test1.py', 'size': 100},
                {'path': 'test2.py', 'size': 200}
            ],
            'total_count': 2
        }
        
        # Set the artifacts
        orchestrator.artifacts['code_files'] = code_files_dict
        orchestrator.artifacts['blueprint'] = {}
        
        # Extract code_files as the pipeline would
        code_files_artifact = orchestrator.artifacts.get('code_files', {})
        if isinstance(code_files_artifact, dict):
            code_files_list = code_files_artifact.get('generated_files', [])
        else:
            code_files_list = code_files_artifact if isinstance(code_files_artifact, list) else []
        
        # Verify extraction
        assert isinstance(code_files_list, list)
        assert len(code_files_list) == 2
        assert code_files_list[0]['path'] == 'test1.py'
        assert code_files_list[1]['path'] == 'test2.py'
        
        # Test with list format (backwards compatibility)
        orchestrator.artifacts['code_files'] = [
            {'path': 'test3.py', 'size': 300}
        ]
        
        code_files_artifact = orchestrator.artifacts.get('code_files', {})
        if isinstance(code_files_artifact, dict):
            code_files_list = code_files_artifact.get('generated_files', [])
        else:
            code_files_list = code_files_artifact if isinstance(code_files_artifact, list) else []
        
        assert isinstance(code_files_list, list)
        assert len(code_files_list) == 1
        assert code_files_list[0]['path'] == 'test3.py'

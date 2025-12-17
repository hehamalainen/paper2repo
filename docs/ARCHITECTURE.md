# Paper2Repo Architecture

## Overview

Paper2Repo is an AI-powered multi-agent platform that transforms research papers into production-ready code repositories. The system follows a three-phase pipeline architecture with specialized agents, memory systems, and tool layers.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Pipeline Orchestrator                  │
│              (Token Budget & Artifact Store)             │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌─────┐    ┌─────┐    ┌─────┐
    │ P1  │───▶│ P2  │───▶│ P3  │
    │Blue │    │Code │    │Verify│
    │print│    │Gen  │    │      │
    └─────┘    └─────┘    └─────┘
```

## Pipeline Phases

### Phase 1: Blueprint Generation (P1_BLUEPRINT)

**Purpose**: Understand requirements and generate detailed code blueprint

**Agents Involved**:
1. **IntentUnderstandingAgent**: Semantic analysis of user requirements
2. **DocumentParsingAgent**: PDF/text ingestion and segmentation
3. **ConceptAnalysisAgent**: Extract concepts (data structures, models, techniques)
4. **AlgorithmAnalysisAgent**: Extract algorithms and equations
5. **CodePlanningAgent**: Generate comprehensive blueprint

**Outputs**:
- Intent specification
- Document index with semantic segmentation
- Extracted concepts with relationships
- Algorithm specifications
- **Blueprint** (YAML) with 8 required sections:
  - `project_file_hierarchy`: Complete file structure
  - `component_specification`: Detailed component specs
  - `verification_protocol`: Testing strategy
  - `execution_environment`: Language, dependencies, build system
  - `staged_development_plan`: Phased approach
  - `build_order`: Dependency-based ordering
  - `entrypoints`: Main entry points
  - `traceability_matrix`: Concept-to-code mapping

### Phase 2: Code Generation (P2_CODEGEN)

**Purpose**: Generate production-ready code from blueprint

**Agents Involved**:
1. **ReferenceMiningAgent**: Discover and index external repositories
2. **MemoryManagerAgent**: Manage code memory (clean-slate approach)
3. **CodeGeneratorAgent**: File-by-file code synthesis

**Memory Systems**:
- **CodeMemory**: Per-file interface tracking with dependency edges
- **CodeRAG**: External grounding with relationship tuples and retrieval gate
- **SkillMemory**: Long-term learning patterns

**Outputs**:
- Indexed external references
- Generated source files
- CodeMem entries for each file
- Updated memory systems

### Phase 3: Verification & Refinement (P3_VERIFY)

**Purpose**: Validate and refine generated code

**Agents Involved**:
1. **ValidatorAgent**: Static analysis and execution testing

**Validation**:
- **Static Analysis**: Syntax, types, logic, quality, security
- **Execution Tests**: Correctness, performance, error handling
- **Compatibility Score** (target ≥ 0.80):
  - Spec Preservation (30%): Implements requirements
  - Structural Consistency (25%): Follows blueprint
  - Domain Grounding (20%): Aligned with concepts
  - Executability (25%): Functional and runnable

**Refinement Loop**:
- Max 3 iterations
- Iterative improvement based on validation feedback
- Stops when compatibility ≥ 0.80 or max iterations reached

## Agent Specifications

### Orchestrator
**Role**: Central coordination and workflow management
- Registers and manages all agents
- Coordinates phase execution
- Manages token budget
- Maintains artifact store

### IntentUnderstandingAgent
**Role**: Extract actionable intent from user input
- Identifies primary goal
- Determines input type (PDF, text, URL)
- Extracts output requirements
- Defines success criteria

### DocumentParsingAgent
**Role**: Ingest and structure research papers
- PDF extraction (PyMuPDF)
- Text segmentation (heading/paragraph/sentence)
- Semantic indexing
- Section hierarchy

### ConceptAnalysisAgent
**Role**: Extract key concepts from papers
- Identifies data structures, algorithms, models
- Extracts properties and attributes
- Builds concept relationships (depends_on, extends, uses)

### AlgorithmAnalysisAgent
**Role**: Extract algorithms and equations
- Pseudocode generation
- Complexity analysis (time/space)
- Input/output specifications
- LaTeX equation extraction

### CodePlanningAgent
**Role**: Generate comprehensive code blueprint
- Designs file hierarchy
- Specifies component interfaces
- Plans verification strategy
- Creates traceability matrix

### ReferenceMiningAgent
**Role**: Discover external code references
- GitHub repository search
- Code snippet indexing
- Concept-to-code mapping

### MemoryManagerAgent
**Role**: Manage code memory and context
- Clean-slate approach (clears at start of P2)
- Tracks file interfaces and dependencies
- Computes build order
- Manages CodeRAG and SkillMemory

### CodeGeneratorAgent
**Role**: Synthesize code files
- File-by-file generation
- Uses blueprint and CodeMem context
- Writes to sandboxed filesystem
- Maintains interface contracts

### ValidatorAgent
**Role**: Validate and score generated code
- Static analysis
- Execution testing (sandboxed)
- Compatibility scoring
- Identifies refinement needs

## Tool Layers

### Perception Layer (No Side Effects)
- **PDFIngest**: Extract text and metadata from PDFs
- **WebFetch**: Retrieve online content and paper metadata
- **GitHubSearch**: Search repositories and code

### Cognitive Layer (No Side Effects)
- **Segmentation**: Split documents into logical sections
- **SemanticIndex**: Create searchable embeddings
- **Retrieval**: Find relevant content with retrieval gate

### Action Layer (Sandboxed Side Effects)
- **Filesystem**: Safe file operations in sandbox
- **CommandExec**: Execute commands with allowlist
- **Sandbox**: Isolated execution environments
- **GitPatch**: Generate and apply patches

## Memory Systems

### CodeMemory (codemem.py)
**Purpose**: Track per-file interfaces and dependencies

**Schema** (codemem_entry.json):
```json
{
  "file": "path/to/file.py",
  "core_purpose": "Brief description",
  "public_interface": [
    {"name": "func", "type": "function", "signature": "..."}
  ],
  "dependency_edges": [
    {"target": "other.py", "type": "import", "imports": ["..."]
    }
  ]
}
```

**Operations**:
- `add_entry()`: Add file tracking
- `get_dependencies()`: Get file dependencies
- `get_dependents()`: Get reverse dependencies
- `compute_build_order()`: Topological sort

### CodeRAG (coderag.py)
**Purpose**: External grounding with relationship tuples

**Features**:
- Relationship tuples: (subject, predicate, object, confidence)
- Repository indexing
- Concept-to-code mapping
- Retrieval gate (threshold: 0.3)

**Operations**:
- `add_relationship()`: Add tuple
- `retrieve_grounding()`: Find relevant code
- `extract_relationships_from_text()`: Parse relationships

### SkillMemory (skill_memory.py)
**Purpose**: Long-term learning through reflection

**Features**:
- Post-run reflection
- Pattern extraction
- Success rate tracking
- Context-based retrieval

**Operations**:
- `reflect_on_run()`: Extract learnings
- `search_skills()`: Find applicable patterns
- `get_top_skills()`: Best-performing skills

## Artifact Contracts

### Blueprint (blueprint.yaml)
Must contain 8 canonical sections (see Phase 1 above)

### CodeMem Entry
Must have: `file`, `core_purpose`, `public_interface`, `dependency_edges`

### Compatibility Score
Formula: `0.3 * spec + 0.25 * struct + 0.2 * domain + 0.25 * exec`
Target: ≥ 0.80 for success

## Token Budget Management

### Configuration
- Total budget: 1,000,000 tokens (configurable)
- Per-agent tracking
- Hybrid routing:
  - **Fast**: Simple tasks (e.g., gpt-3.5-turbo)
  - **Balanced**: Most tasks (e.g., gpt-4)
  - **Powerful**: Complex tasks (e.g., gpt-4-turbo)

### Monitoring
- Real-time usage tracking
- Budget reports per phase
- Automatic allocation management

## Extension Guide

### Adding a New Agent

1. **Create Agent Class**:
```python
from paper2repo.utils.llm_utils import LLMClient

class MyAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.agent_name = "my_agent"
    
    def process(self, input_data):
        # Agent logic here
        return results
```

2. **Register with Orchestrator**:
```python
orchestrator.register_agent('my_agent', MyAgent(llm_client))
```

3. **Integrate in Workflow**:
```python
if 'my_agent' in self.agents:
    result = self.agents['my_agent'].process(input_data)
```

### Adding a New Tool

1. **Create Tool Class**:
```python
class MyTool:
    def __init__(self, config):
        self.config = config
    
    def execute(self, params):
        # Tool logic here
        return result
```

2. **Use in Agent**:
```python
from paper2repo.tools.my_category.my_tool import MyTool

class MyAgent:
    def __init__(self):
        self.tool = MyTool(config)
    
    def process(self, input_data):
        result = self.tool.execute(params)
        return result
```

### Adding a New Memory System

1. **Define Schema** (JSON schema in `schemas/`)
2. **Implement Memory Class**:
```python
class MyMemory:
    def __init__(self):
        self.storage = {}
    
    def store(self, key, value):
        self.storage[key] = value
    
    def retrieve(self, key):
        return self.storage.get(key)
```

3. **Integrate with MemoryManager**:
```python
self.my_memory = MyMemory()
```

## Configuration

### Config File (mcp_agent.config.yaml)
```yaml
llm:
  provider: openai
  max_tokens: 4096
  temperature: 0.7

budget:
  total_tokens: 1000000

workflow:
  max_refinement_iterations: 3
  enable_reference_mining: true
```

### Environment Variables
- `LLM_PROVIDER`: LLM provider (openai, anthropic, mock)
- `OPENAI_API_KEY`: OpenAI API key
- `GITHUB_TOKEN`: GitHub API token

## Testing

### Test Structure
```
tests/
├── conftest.py              # Fixtures
├── test_imports.py          # Import checks
├── test_cli_help.py         # CLI functionality
└── test_pipeline_components.py  # Component tests
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### End-to-End Test
```bash
python run_e2e_test.py
```

## Deployment

### Installation
```bash
pip install -e .
```

### Optional Dependencies
```bash
pip install 'paper2repo[cli]'    # CLI with rich formatting
pip install 'paper2repo[ui]'     # Web UI
pip install 'paper2repo[pdf]'    # PDF support
pip install 'paper2repo[all]'    # Everything
```

### Usage
```bash
# CLI
python main.py --version
python main.py generate paper.pdf -o output/

# Web UI
python -m paper2repo.ui.streamlit_app
```

## Performance Considerations

### Token Efficiency
- Use fast models for simple tasks
- Batch similar operations
- Cache frequently used results

### Memory Management
- Clean-slate approach in P2
- Selective context loading
- Periodic garbage collection

### Parallelization
- Independent agent operations can run in parallel
- Tool operations are thread-safe
- Batch processing for multiple files

## Security

### Sandboxing
- All file operations in isolated sandbox
- Command execution with allowlist
- No network access from generated code during validation

### Input Validation
- Path traversal prevention
- Content sanitization
- Size limits on inputs

### API Key Management
- Store in separate secrets file
- Environment variable fallback
- Never commit secrets

## Troubleshooting

### Common Issues

1. **Import Errors**: Run `pip install -e .`
2. **Missing Dependencies**: Install optional deps
3. **Token Budget Exceeded**: Increase budget or use faster models
4. **Validation Failing**: Check compatibility score breakdown

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python main.py generate paper.pdf
```

## References

- PRD Specification: See original requirements
- JSON Schemas: `paper2repo/schemas/`
- Example Workflows: `tests/conftest.py`

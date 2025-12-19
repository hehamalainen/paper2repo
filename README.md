---
title: Paper2Repo
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.40.0"
app_file: app.py
pinned: false
---

# Paper2Repo 📄➡️💻

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Transform research papers into production-ready code repositories using AI-powered multi-agent orchestration.**

Paper2Repo is an intelligent system that reads research papers and automatically generates working code implementations, complete with documentation, tests, and proper structure.

## ✨ Features

- 📄 **Multi-Format Input**: PDF, text, or URL input for research papers
- 🤖 **10 Specialized Agents**: Each optimized for specific tasks
- 🔄 **3-Phase Pipeline**: Blueprint → Code Generation → Verification
- 💾 **Advanced Memory Systems**: CodeMemory, CodeRAG, SkillMemory
- 🎯 **High Accuracy**: Targets ≥80% compatibility score
- 🔧 **Extensible Architecture**: Easy to add new agents and tools
- 💻 **Multiple Interfaces**: CLI and Web UI
- 🧪 **Comprehensive Testing**: Full test suite included

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/hehamalainen/paper2repo.git
cd paper2repo

# Install in editable mode
pip install -e .

# Or install with optional features
pip install 'paper2repo[all]'  # All features
pip install 'paper2repo[cli]'  # CLI with rich formatting
pip install 'paper2repo[ui]'   # Web UI
pip install 'paper2repo[pdf]'  # PDF support
```

### Basic Usage

#### Command Line

```bash
# Show version
python main.py --version

# Generate code from paper (if click is installed)
python main.py generate paper.pdf -o output/

# With additional requirements
python main.py generate paper.pdf -u "Implement in Python with tests"
```

#### Web Interface

```bash
# Launch web UI (requires streamlit)
python -m paper2repo.ui.streamlit_app

# Or using streamlit directly
streamlit run paper2repo/ui/streamlit_app.py
```

#### Python API

```python
from pathlib import Path
from paper2repo.workflows.pipeline_orchestrator import PipelineOrchestrator

# Initialize pipeline
pipeline = PipelineOrchestrator(
    output_dir=Path("./output"),
    total_token_budget=1_000_000
)

# Prepare input
input_data = {
    'document_path': 'paper.pdf',
    'user_input': 'Generate Python implementation'
}

# Run pipeline
results = pipeline.run(input_data)

# Check results
if results['success']:
    print(f"Code generated in: {pipeline.get_output_directory()}")
    print(f"Compatibility score: {results['artifacts']['validation']['compatibility_score']:.2f}")
```

## 🏗️ Architecture

Paper2Repo uses a three-phase pipeline architecture:

### Phase 1: Blueprint Generation (P1)
1. **Intent Understanding**: Analyze user requirements
2. **Document Parsing**: Extract and segment paper content
3. **Concept Analysis**: Identify key concepts and relationships
4. **Algorithm Analysis**: Extract algorithms and equations
5. **Code Planning**: Generate comprehensive blueprint

### Phase 2: Code Generation (P2)
1. **Reference Mining**: Discover relevant external code
2. **Memory Management**: Clean-slate approach for context
3. **Code Synthesis**: File-by-file generation

### Phase 3: Verification & Refinement (P3)
1. **Validation**: Static analysis and compatibility scoring
2. **Refinement**: Iterative improvement (up to 3 iterations)
3. **Final Output**: Production-ready code

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

## 🤖 Agents

Paper2Repo includes 10 specialized agents:

| Agent | Purpose |
|-------|---------|
| **Orchestrator** | Central coordination and workflow management |
| **IntentUnderstanding** | Semantic analysis of requirements |
| **DocumentParsing** | Paper ingestion and segmentation |
| **ConceptAnalysis** | Concept extraction and relationships |
| **AlgorithmAnalysis** | Algorithm and equation extraction |
| **CodePlanning** | Blueprint generation |
| **ReferenceMining** | External repository discovery |
| **MemoryManager** | Context and memory management |
| **CodeGenerator** | File-by-file code synthesis |
| **Validator** | Static analysis and validation |

## 🛠️ Tool Layers

### Perception Layer (No Side Effects)
- **PDFIngest**: Extract text from PDFs
- **WebFetch**: Retrieve online content
- **GitHubSearch**: Search repositories

### Cognitive Layer (No Side Effects)
- **Segmentation**: Document segmentation
- **SemanticIndex**: Semantic search
- **Retrieval**: Content retrieval with quality gate

### Action Layer (Sandboxed)
- **Filesystem**: Safe file operations
- **CommandExec**: Command execution
- **Sandbox**: Isolated environments
- **GitPatch**: Patch generation

## 📊 Memory Systems

### CodeMemory
Tracks per-file interfaces and dependencies with build order computation.

### CodeRAG
External grounding with relationship tuples and retrieval gate.

### SkillMemory
Long-term learning through post-run reflection.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_imports.py -v

# Run end-to-end test
python run_e2e_test.py

# Check imports
python -c "import paper2repo; print(f'v{paper2repo.__version__}')"

# Compile all Python files
python -m compileall paper2repo/
```

## 📋 Requirements

- **Python 3.11+** (required)
- **Core dependencies**: pyyaml, requests, pydantic, python-dotenv, jinja2, numpy
- **Optional dependencies**:
  - CLI: click, rich
  - UI: streamlit
  - PDF: pymupdf
  - Dev: pytest, black, ruff

## ⚙️ Configuration

Configuration is managed through `paper2repo/config/mcp_agent.config.yaml`:

```yaml
llm:
  provider: mock  # or openai, anthropic
  max_tokens: 4096
  temperature: 0.7

budget:
  total_tokens: 1000000

workflow:
  max_refinement_iterations: 3
  enable_reference_mining: true
```

Environment variables (optional):
- `LLM_PROVIDER`: Override LLM provider
- `OPENAI_API_KEY`: OpenAI API key
- `GITHUB_TOKEN`: GitHub API token

## 📖 Examples

### Generate from PDF

```bash
python main.py generate research_paper.pdf -o output/neural_net/
```

### Generate with Custom Requirements

```bash
python main.py generate paper.pdf \
  -u "Implement in Python 3.11 with type hints and pytest tests" \
  -o output/
```

### Use Python API

```python
from paper2repo.workflows.pipeline_orchestrator import PipelineOrchestrator

pipeline = PipelineOrchestrator(output_dir="./output")

results = pipeline.run({
    'document_text': 'Paper content...',
    'user_input': 'Generate TypeScript implementation'
})

print(f"Success: {results['success']}")
print(f"Files: {len(results['artifacts']['code_files']['generated_files'])}")
```

## 🎯 Compatibility Scoring

Paper2Repo uses a weighted compatibility score:

- **Spec Preservation (30%)**: Implements required features
- **Structural Consistency (25%)**: Follows blueprint structure  
- **Domain Grounding (20%)**: Aligned with paper concepts
- **Executability (25%)**: Functional and runnable

**Target**: ≥ 0.80 for success

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/hehamalainen/paper2repo.git
cd paper2repo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e '.[dev]'

# Run tests
python -m pytest tests/ -v
```

### Run Reproduction Script

```bash
chmod +x reproduce.sh
./reproduce.sh
```

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- [CHANGELOG](CHANGELOG.md) - Version history
- API Documentation - In code docstrings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built following PRD-B baseline specifications
- Inspired by research in multi-agent systems and code generation
- Uses modern Python packaging best practices

## 📬 Contact

- GitHub: [@hehamalainen](https://github.com/hehamalainen)
- Repository: [paper2repo](https://github.com/hehamalainen/paper2repo)

## 🗺️ Roadmap

- [ ] Support for more LLM providers
- [ ] Enhanced code refinement strategies
- [ ] Multi-language support beyond Python
- [ ] Interactive debugging mode
- [ ] Cloud deployment options
- [ ] API service endpoint

---

**Paper2Repo v1.0.0** - Transform research into reality 🚀

# Changelog

All notable changes to Paper2Repo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of Paper2Repo
- Three-phase pipeline architecture (Blueprint, CodeGen, Verify)
- 10 specialized agents:
  - Orchestrator for workflow coordination
  - IntentUnderstandingAgent for semantic analysis
  - DocumentParsingAgent for paper ingestion
  - ConceptAnalysisAgent for concept extraction
  - AlgorithmAnalysisAgent for algorithm extraction
  - CodePlanningAgent for blueprint generation
  - ReferenceMiningAgent for repository discovery
  - MemoryManagerAgent for context management
  - CodeGeneratorAgent for file-by-file synthesis
  - ValidatorAgent for static analysis and validation
- Three memory systems:
  - CodeMemory for per-file tracking
  - CodeRAG for external grounding
  - SkillMemory for long-term learning
- Tool layers:
  - Perception: PDF ingest, web fetch, GitHub search
  - Cognitive: Segmentation, semantic indexing, retrieval
  - Action: Filesystem, command exec, sandbox, git patch
- CLI interface with optional rich formatting
- Web UI with Streamlit
- Comprehensive test suite
- Full documentation

### Features
- Blueprint generation with 8 canonical sections
- Token budget management
- Hybrid LLM routing (fast/balanced/powerful)
- Compatibility scoring (target ≥0.80)
- Clean-slate memory approach
- Retrieval gate for quality control

### Documentation
- README with quick start guide
- ARCHITECTURE.md with system design
- Inline code documentation
- Example workflows

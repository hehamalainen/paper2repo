"""Pipeline orchestrator for managing complete workflow execution."""
from typing import Dict, Any, Optional
import logging
from pathlib import Path
from paper2repo.agents.orchestrator import Orchestrator
from paper2repo.utils.llm_utils import LLMClient, LLMConfig, TokenBudget
from paper2repo.tools.action.filesystem import Filesystem

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Main pipeline orchestrator for Paper2Repo."""
    
    def __init__(
        self,
        output_dir: Path,
        llm_config: Optional[LLMConfig] = None,
        total_token_budget: int = 1_000_000
    ):
        """Initialize pipeline orchestrator.
        
        Args:
            output_dir: Output directory for generated code
            llm_config: LLM configuration
            total_token_budget: Total token budget for pipeline
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize token budget
        self.token_budget = TokenBudget(total_budget=total_token_budget)
        
        # Initialize LLM client
        llm_config = llm_config or LLMConfig()
        self.llm_client = LLMClient(llm_config, self.token_budget)
        
        # Initialize filesystem
        self.filesystem = Filesystem(sandbox_dir=self.output_dir)
        
        # Initialize orchestrator
        self.orchestrator = Orchestrator(self.llm_client, self.token_budget)
        
        # Artifact store
        self.artifacts: Dict[str, Any] = {}
        
        # Register all agents
        self._register_agents()
        
        logger.info(f"Pipeline initialized. Output: {self.output_dir}")
    
    def _register_agents(self) -> None:
        """Register all agents with orchestrator."""
        from paper2repo.agents.intent_understanding import IntentUnderstandingAgent
        from paper2repo.agents.document_parsing import DocumentParsingAgent
        from paper2repo.agents.concept_analysis import ConceptAnalysisAgent
        from paper2repo.agents.algorithm_analysis import AlgorithmAnalysisAgent
        from paper2repo.agents.code_planning import CodePlanningAgent
        from paper2repo.agents.reference_mining import ReferenceMiningAgent
        from paper2repo.agents.memory_manager import MemoryManagerAgent
        from paper2repo.agents.code_generator import CodeGeneratorAgent
        from paper2repo.agents.validator import ValidatorAgent
        
        self.orchestrator.register_agent(
            'intent_understanding',
            IntentUnderstandingAgent(self.llm_client)
        )
        self.orchestrator.register_agent(
            'document_parsing',
            DocumentParsingAgent()
        )
        self.orchestrator.register_agent(
            'concept_analysis',
            ConceptAnalysisAgent(self.llm_client)
        )
        self.orchestrator.register_agent(
            'algorithm_analysis',
            AlgorithmAnalysisAgent(self.llm_client)
        )
        self.orchestrator.register_agent(
            'code_planning',
            CodePlanningAgent(self.llm_client)
        )
        self.orchestrator.register_agent(
            'reference_mining',
            ReferenceMiningAgent()
        )
        self.orchestrator.register_agent(
            'memory_manager',
            MemoryManagerAgent()
        )
        self.orchestrator.register_agent(
            'code_generator',
            CodeGeneratorAgent(self.llm_client, self.filesystem)
        )
        self.orchestrator.register_agent(
            'validator',
            ValidatorAgent(self.llm_client)
        )
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete pipeline.
        
        Args:
            input_data: Input data (document path, user input, etc.)
            
        Returns:
            Pipeline results
        """
        logger.info("Starting Paper2Repo pipeline")
        
        results = {
            'phases': {},
            'artifacts': {},
            'success': False,
            'errors': []
        }
        
        try:
            # Phase 1: Blueprint Generation
            logger.info("Phase 1: Blueprint Generation")
            p1_result = self.orchestrator.coordinate_workflow('blueprint', input_data)
            results['phases']['p1_blueprint'] = p1_result
            self.artifacts.update(p1_result.get('artifacts', {}))
            
            # Phase 2: Code Generation
            logger.info("Phase 2: Code Generation")
            p2_input = {
                'blueprint': self.artifacts.get('blueprint', {}),
                'concepts': self.artifacts.get('concepts', {})
            }
            p2_result = self.orchestrator.coordinate_workflow('codegen', p2_input)
            results['phases']['p2_codegen'] = p2_result
            self.artifacts.update(p2_result.get('artifacts', {}))
            
            # Phase 3: Verification
            logger.info("Phase 3: Verification & Refinement")
            p3_input = {
                'code_files': self.artifacts.get('code_files', []),
                'blueprint': self.artifacts.get('blueprint', {})
            }
            p3_result = self.orchestrator.coordinate_workflow('verify', p3_input)
            results['phases']['p3_verify'] = p3_result
            self.artifacts.update(p3_result.get('artifacts', {}))
            
            # Check success
            validation = self.artifacts.get('validation', {})
            results['success'] = validation.get('passed', False)
            
            # Store artifacts
            results['artifacts'] = self.artifacts
            
            # Get budget report
            results['token_budget'] = self.orchestrator.get_budget_report()
            
            logger.info(f"Pipeline completed. Success: {results['success']}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results['errors'].append(str(e))
            results['success'] = False
        
        return results
    
    def get_artifacts(self) -> Dict[str, Any]:
        """Get all pipeline artifacts."""
        return self.artifacts
    
    def get_output_directory(self) -> Path:
        """Get output directory path."""
        return self.output_dir

"""Central orchestrator for coordinating all agents and workflows."""
from typing import Dict, Any, Optional
import logging
from paper2repo.utils.llm_utils import LLMClient, TokenBudget

logger = logging.getLogger(__name__)


class Orchestrator:
    """Central orchestrator for Paper2Repo system."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        token_budget: Optional[TokenBudget] = None
    ):
        """Initialize orchestrator.
        
        Args:
            llm_client: LLM client for agent communication
            token_budget: Token budget for orchestration
        """
        self.llm_client = llm_client
        self.token_budget = token_budget or TokenBudget()
        self.agents: Dict[str, Any] = {}
        self.workflow_state: Dict[str, Any] = {}
        
    def register_agent(self, agent_name: str, agent: Any) -> None:
        """Register an agent with the orchestrator.
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
        """
        self.agents[agent_name] = agent
        logger.info(f"Registered agent: {agent_name}")
    
    def coordinate_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate a multi-agent workflow.
        
        Args:
            workflow_name: Name of workflow to execute
            input_data: Input data for workflow
            
        Returns:
            Workflow results
        """
        logger.info(f"Starting workflow: {workflow_name}")
        
        self.workflow_state = {
            'workflow_name': workflow_name,
            'status': 'running',
            'artifacts': {},
            'errors': []
        }
        
        try:
            # Execute workflow based on name
            if workflow_name == 'blueprint':
                result = self._execute_blueprint_workflow(input_data)
            elif workflow_name == 'codegen':
                result = self._execute_codegen_workflow(input_data)
            elif workflow_name == 'verify':
                result = self._execute_verify_workflow(input_data)
            else:
                raise ValueError(f"Unknown workflow: {workflow_name}")
            
            self.workflow_state['status'] = 'completed'
            self.workflow_state['result'] = result
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self.workflow_state['status'] = 'failed'
            self.workflow_state['errors'].append(str(e))
            raise
        
        return self.workflow_state
    
    def _execute_blueprint_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase 1: Blueprint workflow."""
        logger.info("Executing blueprint workflow (P1)")
        
        artifacts = {}
        
        # 1. Intent Understanding
        if 'intent_understanding' in self.agents:
            intent_result = self.agents['intent_understanding'].process(input_data)
            artifacts['intent'] = intent_result
        
        # 2. Document Parsing
        if 'document_parsing' in self.agents:
            doc_result = self.agents['document_parsing'].process(input_data)
            artifacts['document_index'] = doc_result
        
        # 3. Concept Analysis
        if 'concept_analysis' in self.agents:
            concept_result = self.agents['concept_analysis'].process(
                artifacts.get('document_index', {})
            )
            artifacts['concepts'] = concept_result
        
        # 4. Algorithm Analysis
        if 'algorithm_analysis' in self.agents:
            algo_result = self.agents['algorithm_analysis'].process(
                artifacts.get('document_index', {})
            )
            artifacts['algorithms'] = algo_result
        
        # 5. Code Planning
        if 'code_planning' in self.agents:
            blueprint_result = self.agents['code_planning'].process({
                'concepts': artifacts.get('concepts', {}),
                'algorithms': artifacts.get('algorithms', {}),
                'intent': artifacts.get('intent', {})
            })
            artifacts['blueprint'] = blueprint_result
        
        self.workflow_state['artifacts'] = artifacts
        return artifacts
    
    def _execute_codegen_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase 2: Code Generation workflow."""
        logger.info("Executing code generation workflow (P2)")
        
        artifacts = {}
        blueprint = input_data.get('blueprint', {})
        
        # 1. Reference Mining
        if 'reference_mining' in self.agents:
            ref_result = self.agents['reference_mining'].process(input_data)
            artifacts['references'] = ref_result
        
        # 2. Memory Manager (clean slate)
        if 'memory_manager' in self.agents:
            self.agents['memory_manager'].clear_memory()
        
        # 3. Code Generation
        if 'code_generator' in self.agents:
            code_result = self.agents['code_generator'].process({
                'blueprint': blueprint,
                'references': artifacts.get('references', {})
            })
            artifacts['code_files'] = code_result
        
        self.workflow_state['artifacts'] = artifacts
        return artifacts
    
    def _execute_verify_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Phase 3: Verification workflow."""
        logger.info("Executing verification workflow (P3)")
        
        artifacts = {}
        code_files = input_data.get('code_files', [])
        
        # 1. Validation
        if 'validator' in self.agents:
            validation_result = self.agents['validator'].process({
                'code_files': code_files,
                'blueprint': input_data.get('blueprint', {})
            })
            artifacts['validation'] = validation_result
        
        # 2. Refinement loop if needed
        if not validation_result.get('passed', False):
            logger.info("Validation failed, entering refinement loop")
            # Could implement iterative refinement here
        
        self.workflow_state['artifacts'] = artifacts
        return artifacts
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return self.workflow_state
    
    def get_budget_report(self) -> Dict[str, Any]:
        """Get token budget report."""
        return self.llm_client.get_budget_report()

"""Phase 2: Code Generation Workflow."""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CodeGenWorkflow:
    """Workflow for Phase 2: Code Generation."""
    
    def __init__(self, orchestrator):
        """Initialize code generation workflow.
        
        Args:
            orchestrator: Main orchestrator instance
        """
        self.orchestrator = orchestrator
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation workflow.
        
        Args:
            input_data: Blueprint and context
            
        Returns:
            Generated code artifacts
        """
        logger.info("Executing P2: Code Generation Workflow")
        
        artifacts = {}
        
        # Step 1: Reference Mining
        logger.info("Step 1: Reference Mining")
        ref_agent = self.orchestrator.agents.get('reference_mining')
        if ref_agent:
            artifacts['references'] = ref_agent.process(input_data)
        
        # Step 2: Memory Manager (Clean Slate)
        logger.info("Step 2: Memory Manager - Clean Slate")
        mem_agent = self.orchestrator.agents.get('memory_manager')
        if mem_agent:
            mem_agent.clear_memory()
        
        # Step 3: Code Generation
        logger.info("Step 3: File-by-File Code Generation")
        code_agent = self.orchestrator.agents.get('code_generator')
        if code_agent:
            artifacts['code_files'] = code_agent.process({
                'blueprint': input_data.get('blueprint', {}),
                'references': artifacts.get('references', {})
            })
        
        logger.info("P2 Code Generation workflow completed")
        
        return artifacts

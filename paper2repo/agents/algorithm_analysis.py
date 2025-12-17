"""Algorithm Analysis Agent for extracting algorithms and equations."""
from typing import Dict, Any
import logging
import json
from paper2repo.utils.llm_utils import LLMClient, ModelTier
from paper2repo.prompts.algorithm_prompts import get_algorithm_extraction_prompt

logger = logging.getLogger(__name__)


class AlgorithmAnalysisAgent:
    """Agent for extracting and analyzing algorithms from papers."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize algorithm analysis agent.
        
        Args:
            llm_client: LLM client for processing
        """
        self.llm_client = llm_client
        self.agent_name = "algorithm_analysis"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract algorithms from document.
        
        Args:
            input_data: Document index
            
        Returns:
            Extracted algorithms
        """
        sections = input_data.get('sections', [])
        
        if not sections:
            return {'algorithms': []}
        
        # Process sections to extract algorithms
        all_algorithms = []
        
        for section in sections[:10]:  # Process first 10 sections
            content = section.get('content', '')
            
            # Look for algorithm indicators
            if not any(keyword in content.lower() for keyword in 
                      ['algorithm', 'procedure', 'method', 'equation', 'formula']):
                continue
            
            # Generate prompt
            prompt = get_algorithm_extraction_prompt(content)
            
            # Call LLM
            response = self.llm_client.generate(
                prompt=prompt,
                agent_name=self.agent_name,
                model_tier=ModelTier.POWERFUL
            )
            
            try:
                # Parse algorithms from response
                algorithms = json.loads(response)
                if isinstance(algorithms, list):
                    all_algorithms.extend(algorithms)
                elif isinstance(algorithms, dict) and 'algorithms' in algorithms:
                    all_algorithms.extend(algorithms['algorithms'])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse algorithms from section")
        
        logger.info(f"Extracted {len(all_algorithms)} algorithms")
        
        return {
            'algorithms': all_algorithms,
            'total_count': len(all_algorithms)
        }

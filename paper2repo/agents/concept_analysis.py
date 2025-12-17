"""Concept Analysis Agent for extracting concepts from papers."""
from typing import Dict, Any
import logging
import json
from paper2repo.utils.llm_utils import LLMClient, ModelTier
from paper2repo.prompts.concept_prompts import get_concept_extraction_prompt

logger = logging.getLogger(__name__)


class ConceptAnalysisAgent:
    """Agent for extracting and analyzing concepts from papers."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize concept analysis agent.
        
        Args:
            llm_client: LLM client for processing
        """
        self.llm_client = llm_client
        self.agent_name = "concept_analysis"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract concepts from document.
        
        Args:
            input_data: Document index
            
        Returns:
            Extracted concepts
        """
        sections = input_data.get('sections', [])
        
        if not sections:
            return {'concepts': []}
        
        # Process sections to extract concepts
        all_concepts = []
        
        for section in sections[:10]:  # Process first 10 sections
            content = section.get('content', '')
            
            if len(content) < 50:  # Skip very short sections
                continue
            
            # Generate prompt
            prompt = get_concept_extraction_prompt(content)
            
            # Call LLM
            response = self.llm_client.generate(
                prompt=prompt,
                agent_name=self.agent_name,
                model_tier=ModelTier.POWERFUL
            )
            
            try:
                # Parse concepts from response
                concepts = json.loads(response)
                if isinstance(concepts, list):
                    all_concepts.extend(concepts)
                elif isinstance(concepts, dict) and 'concepts' in concepts:
                    all_concepts.extend(concepts['concepts'])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse concepts from section")
        
        logger.info(f"Extracted {len(all_concepts)} concepts")
        
        return {
            'concepts': all_concepts,
            'total_count': len(all_concepts)
        }

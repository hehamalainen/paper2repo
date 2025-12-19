"""Intent Understanding Agent for semantic analysis of user requirements."""
from typing import Dict, Any
import logging
import json
from paper2repo.utils.llm_utils import LLMClient, ModelTier, extract_json_from_response
from paper2repo.prompts.intent_prompts import get_intent_prompt

logger = logging.getLogger(__name__)


class IntentUnderstandingAgent:
    """Agent for understanding and extracting user intent."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize intent understanding agent.
        
        Args:
            llm_client: LLM client for processing
        """
        self.llm_client = llm_client
        self.agent_name = "intent_understanding"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input and extract intent.
        
        Args:
            input_data: User input
            
        Returns:
            Extracted intent
        """
        user_input = input_data.get('user_input', '')
        
        if not user_input:
            return {'error': 'No user input provided'}
        
        # Generate prompt
        prompt = get_intent_prompt(user_input)
        
        # Call LLM
        response = self.llm_client.generate(
            prompt=prompt,
            agent_name=self.agent_name,
            model_tier=ModelTier.BALANCED
        )
        
        try:
            # Parse response as JSON
            intent = extract_json_from_response(response)
            logger.info(f"Extracted intent: {intent.get('primary_goal', 'unknown')}")
            return intent
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback to raw response
            logger.warning(f"Failed to parse intent as JSON: {e}")
            return {
                'primary_goal': user_input,
                'input_type': 'unknown',
                'output_requirements': ['code repository'],
                'constraints': [],
                'success_criteria': ['functional code'],
                'raw_response': response
            }

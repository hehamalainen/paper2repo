"""Code Planning Agent for blueprint generation."""
from typing import Dict, Any
import logging
import json
import yaml
from paper2repo.utils.llm_utils import LLMClient, ModelTier, extract_json_from_response
from paper2repo.prompts.planning_prompts import get_blueprint_prompt

logger = logging.getLogger(__name__)


class CodePlanningAgent:
    """Agent for generating code blueprints."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize code planning agent.
        
        Args:
            llm_client: LLM client for processing
        """
        self.llm_client = llm_client
        self.agent_name = "code_planning"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code blueprint.
        
        Args:
            input_data: Concepts, algorithms, and requirements
            
        Returns:
            Blueprint
        """
        concepts = input_data.get('concepts', {})
        algorithms = input_data.get('algorithms', {})
        intent = input_data.get('intent', {})
        
        # Prepare context
        concepts_str = json.dumps(concepts, indent=2)
        algorithms_str = json.dumps(algorithms, indent=2)
        requirements_str = json.dumps(intent, indent=2)
        
        # Generate prompt
        prompt = get_blueprint_prompt(concepts_str, algorithms_str, requirements_str)
        
        # Call LLM
        response = self.llm_client.generate(
            prompt=prompt,
            agent_name=self.agent_name,
            model_tier=ModelTier.POWERFUL,
            max_tokens=8000
        )
        
        try:
            # Try to parse as YAML
            blueprint = yaml.safe_load(response)
            logger.info("Generated blueprint successfully")
            return blueprint
        except yaml.YAMLError:
            try:
                # Fallback to JSON
                blueprint = extract_json_from_response(response)
                return blueprint
            except (json.JSONDecodeError, ValueError):
                # Return minimal blueprint
                logger.warning("Failed to parse blueprint, returning minimal structure")
                return self._create_minimal_blueprint()
    
    def _create_minimal_blueprint(self) -> Dict[str, Any]:
        """Create a minimal valid blueprint."""
        return {
            'project_file_hierarchy': {
                'root': 'project',
                'files': []
            },
            'component_specification': {
                'components': []
            },
            'verification_protocol': {
                'test_strategy': 'unit_testing',
                'test_files': []
            },
            'execution_environment': {
                'language': 'python',
                'version': '3.11',
                'dependencies': {}
            },
            'staged_development_plan': {
                'phases': []
            },
            'build_order': [],
            'entrypoints': [],
            'traceability_matrix': {
                'mappings': []
            }
        }

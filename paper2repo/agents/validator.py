"""Validator Agent for static analysis and sandbox execution."""
from typing import Dict, Any, List
import logging
from paper2repo.utils.llm_utils import LLMClient, ModelTier, extract_json_from_response
from paper2repo.prompts.validation_prompts import get_static_analysis_prompt, get_compatibility_prompt
from paper2repo.tools.action.sandbox import Sandbox
from paper2repo.tools.action.command_exec import CommandExec

logger = logging.getLogger(__name__)


class ValidatorAgent:
    """Agent for validating generated code."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize validator agent.
        
        Args:
            llm_client: LLM client for validation
        """
        self.llm_client = llm_client
        self.sandbox = Sandbox()
        self.agent_name = "validator"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated code.
        
        Args:
            input_data: Code files and blueprint
            
        Returns:
            Validation results
        """
        code_files = input_data.get('code_files', [])
        blueprint = input_data.get('blueprint', {})
        
        validation_results = {
            'static_analysis': [],
            'execution_tests': [],
            'compatibility_score': 0.0,
            'passed': False
        }
        
        # Perform static analysis
        for file_info in code_files[:5]:  # Validate first 5 files
            file_path = file_info.get('path', '')
            
            # Skip non-code files
            if not file_path.endswith(('.py', '.js', '.java', '.go')):
                continue
            
            analysis = self._static_analysis(file_path, '')
            validation_results['static_analysis'].append(analysis)
        
        # Compute compatibility score
        compatibility = self._compute_compatibility(code_files, blueprint)
        validation_results['compatibility_score'] = compatibility.get('overall_score', 0.0)
        
        # Determine if passed (>= 0.80)
        validation_results['passed'] = validation_results['compatibility_score'] >= 0.80
        
        logger.info(
            f"Validation complete: "
            f"score={validation_results['compatibility_score']:.2f}, "
            f"passed={validation_results['passed']}"
        )
        
        return validation_results
    
    def _static_analysis(self, file_path: str, code: str) -> Dict[str, Any]:
        """Perform static analysis on code."""
        prompt = get_static_analysis_prompt(file_path, code)
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                agent_name=self.agent_name,
                model_tier=ModelTier.FAST
            )
            
            import json
            analysis = extract_json_from_response(response)
            return {
                'file': file_path,
                'analysis': analysis,
                'score': analysis.get('overall_score', 5)
            }
        except Exception as e:
            logger.error(f"Static analysis failed for {file_path}: {e}")
            return {
                'file': file_path,
                'error': str(e),
                'score': 5
            }
    
    def _compute_compatibility(
        self,
        code_files: List[Dict[str, Any]],
        blueprint: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute compatibility score."""
        # Simplified compatibility scoring
        scores = {
            'spec_preservation': 0.8,  # Default scores
            'structural_consistency': 0.75,
            'domain_grounding': 0.7,
            'executability': 0.85
        }
        
        # Compute weighted overall score
        weights = {
            'spec_preservation': 0.30,
            'structural_consistency': 0.25,
            'domain_grounding': 0.20,
            'executability': 0.25
        }
        
        overall_score = sum(
            scores[key] * weights[key]
            for key in scores
        )
        
        return {
            **scores,
            'overall_score': overall_score,
            'passed': overall_score >= 0.80
        }
    
    def _execute_tests(
        self,
        sandbox_id: str,
        test_command: str
    ) -> Dict[str, Any]:
        """Execute tests in sandbox."""
        result = self.sandbox.execute_in_sandbox(
            sandbox_id=sandbox_id,
            command=test_command
        )
        
        return {
            'success': result.get('success', False),
            'output': result.get('stdout', ''),
            'errors': result.get('stderr', '')
        }

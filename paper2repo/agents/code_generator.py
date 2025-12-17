"""Code Generator Agent for file-by-file code synthesis."""
from typing import Dict, Any, List
import logging
from paper2repo.utils.llm_utils import LLMClient, ModelTier
from paper2repo.prompts.codegen_prompts import get_code_generation_prompt
from paper2repo.tools.action.filesystem import Filesystem

logger = logging.getLogger(__name__)


class CodeGeneratorAgent:
    """Agent for generating code files."""
    
    def __init__(self, llm_client: LLMClient, filesystem: Filesystem):
        """Initialize code generator agent.
        
        Args:
            llm_client: LLM client for code generation
            filesystem: Filesystem tool for writing files
        """
        self.llm_client = llm_client
        self.filesystem = filesystem
        self.agent_name = "code_generator"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code files from blueprint.
        
        Args:
            input_data: Blueprint and context
            
        Returns:
            Generated files
        """
        blueprint = input_data.get('blueprint', {})
        
        # Extract files from blueprint
        files_to_generate = self._extract_files_from_blueprint(blueprint)
        
        generated_files = []
        
        for file_spec in files_to_generate:
            file_path = file_spec.get('path', '')
            
            logger.info(f"Generating: {file_path}")
            
            # Generate code
            code = self._generate_code_for_file(file_spec, blueprint)
            
            # Write to filesystem
            result = self.filesystem.create_file(
                relative_path=file_path,
                content=code,
                overwrite=True
            )
            
            if result['success']:
                generated_files.append({
                    'path': file_path,
                    'size': result['size'],
                    'status': 'generated'
                })
            else:
                logger.error(f"Failed to write {file_path}: {result.get('error')}")
        
        logger.info(f"Generated {len(generated_files)} files")
        
        return {
            'generated_files': generated_files,
            'total_count': len(generated_files)
        }
    
    def _extract_files_from_blueprint(self, blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract file list from blueprint."""
        hierarchy = blueprint.get('project_file_hierarchy', {})
        files = hierarchy.get('files', [])
        
        if not files:
            # Create minimal file structure
            files = [
                {'path': 'main.py', 'purpose': 'Main entry point'},
                {'path': 'README.md', 'purpose': 'Project documentation'}
            ]
        
        return files
    
    def _generate_code_for_file(
        self,
        file_spec: Dict[str, Any],
        blueprint: Dict[str, Any]
    ) -> str:
        """Generate code for a specific file."""
        file_path = file_spec.get('path', '')
        core_purpose = file_spec.get('purpose', '')
        
        # Check file type
        if file_path.endswith('.md'):
            return self._generate_markdown(file_spec, blueprint)
        elif file_path.endswith(('.py', '.js', '.java', '.go')):
            return self._generate_source_code(file_spec, blueprint)
        else:
            return f"# {file_path}\n# {core_purpose}\n"
    
    def _generate_markdown(
        self,
        file_spec: Dict[str, Any],
        blueprint: Dict[str, Any]
    ) -> str:
        """Generate markdown documentation."""
        return f"""# {blueprint.get('project_name', 'Project')}

{file_spec.get('purpose', 'Documentation')}

## Overview

This project was generated from a research paper using Paper2Repo.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
"""
    
    def _generate_source_code(
        self,
        file_spec: Dict[str, Any],
        blueprint: Dict[str, Any]
    ) -> str:
        """Generate source code file."""
        prompt = get_code_generation_prompt(
            file_path=file_spec.get('path', ''),
            core_purpose=file_spec.get('purpose', ''),
            blueprint_context=str(blueprint)[:1000],
            component_spec=str(file_spec),
            dependencies=str(file_spec.get('dependencies', []))
        )
        
        response = self.llm_client.generate(
            prompt=prompt,
            agent_name=self.agent_name,
            model_tier=ModelTier.POWERFUL,
            max_tokens=4000
        )
        
        return response

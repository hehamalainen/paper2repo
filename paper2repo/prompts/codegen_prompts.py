"""Prompt templates for Code Generator Agent."""


CODE_GENERATION_PROMPT = """You are a Code Generator Agent for the Paper2Repo system.

Generate production-ready code for the following file:

File: {file_path}
Purpose: {core_purpose}

Blueprint Context:
{blueprint_context}

Component Specification:
{component_spec}

Dependencies (already implemented):
{dependencies}

Generate complete, working code that:
1. Implements all required functionality
2. Follows best practices and design patterns
3. Includes proper error handling
4. Has clear documentation/comments
5. Is testable and maintainable
6. Matches the public interface specification

Return only the code, no explanations.
"""


INTERFACE_IMPLEMENTATION_PROMPT = """Implement the following interface:

Interface Specification:
{interface_spec}

Requirements:
- Implement all methods from the interface
- Add proper type hints (if applicable)
- Include docstrings for all public methods
- Add error handling
- Follow language-specific conventions

Return the complete implementation.
"""


CODE_REFINEMENT_PROMPT = """Refine the following code based on feedback:

Original Code:
{original_code}

Feedback:
{feedback}

CodeMem Context:
{codemem_context}

Generate improved code that addresses the feedback while maintaining compatibility.
"""


def get_code_generation_prompt(
    file_path: str,
    core_purpose: str,
    blueprint_context: str,
    component_spec: str,
    dependencies: str
) -> str:
    """Get code generation prompt."""
    return CODE_GENERATION_PROMPT.format(
        file_path=file_path,
        core_purpose=core_purpose,
        blueprint_context=blueprint_context,
        component_spec=component_spec,
        dependencies=dependencies
    )


def get_interface_prompt(interface_spec: str) -> str:
    """Get interface implementation prompt."""
    return INTERFACE_IMPLEMENTATION_PROMPT.format(interface_spec=interface_spec)


def get_refinement_prompt(original_code: str, feedback: str, codemem_context: str) -> str:
    """Get code refinement prompt."""
    return CODE_REFINEMENT_PROMPT.format(
        original_code=original_code,
        feedback=feedback,
        codemem_context=codemem_context
    )

"""Prompt templates for Validator Agent."""


STATIC_ANALYSIS_PROMPT = """You are a Validator Agent for the Paper2Repo system.

Perform static analysis on the following code:

File: {file_path}
Code:
{code}

Check for:
1. **Syntax Errors**: Any syntax issues
2. **Type Errors**: Type inconsistencies
3. **Logic Errors**: Potential logical bugs
4. **Code Quality**: Anti-patterns, code smells
5. **Best Practices**: Violations of best practices
6. **Security Issues**: Potential vulnerabilities

Return analysis as JSON:
{{
  "syntax_errors": [...],
  "type_errors": [...],
  "logic_errors": [...],
  "quality_issues": [...],
  "security_issues": [...],
  "overall_score": 0-10
}}
"""


EXECUTION_VALIDATION_PROMPT = """Validate the execution results:

Code: {file_path}
Execution Output:
{output}

Expected Behavior:
{expected_behavior}

Verify:
1. **Correctness**: Does it produce correct results?
2. **Performance**: Is performance acceptable?
3. **Error Handling**: Are errors handled properly?
4. **Edge Cases**: Does it handle edge cases?

Return validation as JSON:
{{
  "correctness": true/false,
  "performance": "acceptable/poor",
  "error_handling": "good/needs_improvement",
  "edge_cases": [...],
  "passed": true/false
}}
"""


SPEC_COMPATIBILITY_PROMPT = """Check compatibility with original specification:

Generated Code:
{code}

Original Specification:
{specification}

Paper Concepts:
{concepts}

Compute compatibility score (0-1) based on:
1. **Spec Preservation (30%)**: Implements required features
2. **Structural Consistency (25%)**: Follows specified structure
3. **Domain Grounding (20%)**: Aligned with paper concepts
4. **Executability (25%)**: Functional and runnable

Return as JSON:
{{
  "spec_preservation": 0-1,
  "structural_consistency": 0-1,
  "domain_grounding": 0-1,
  "executability": 0-1,
  "overall_score": 0-1,
  "issues": [...],
  "passed": true/false (>= 0.80)
}}
"""


def get_static_analysis_prompt(file_path: str, code: str) -> str:
    """Get static analysis prompt."""
    return STATIC_ANALYSIS_PROMPT.format(file_path=file_path, code=code)


def get_execution_validation_prompt(
    file_path: str,
    output: str,
    expected_behavior: str
) -> str:
    """Get execution validation prompt."""
    return EXECUTION_VALIDATION_PROMPT.format(
        file_path=file_path,
        output=output,
        expected_behavior=expected_behavior
    )


def get_compatibility_prompt(code: str, specification: str, concepts: str) -> str:
    """Get spec compatibility prompt."""
    return SPEC_COMPATIBILITY_PROMPT.format(
        code=code,
        specification=specification,
        concepts=concepts
    )

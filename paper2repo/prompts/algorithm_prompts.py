"""Prompt templates for Algorithm Analysis Agent."""


ALGORITHM_EXTRACTION_PROMPT = """You are an Algorithm Analysis Agent for the Paper2Repo system.

Extract algorithms and equations from the following content.

Content:
{content}

For each algorithm, extract:
1. **Name**: Algorithm name
2. **Description**: What it does
3. **Pseudocode**: Step-by-step logic
4. **Inputs**: Input parameters and types
5. **Outputs**: Output parameters and types
6. **Complexity**: Time and space complexity
7. **Implementation Notes**: Key considerations

For equations, extract:
1. **LaTeX**: Mathematical notation
2. **Variables**: Variable definitions
3. **Description**: What the equation represents

Format as JSON following the algorithm_schema.
"""


PSEUDOCODE_GENERATION_PROMPT = """Convert the following algorithm description to pseudocode:

Description:
{description}

Generate clear, structured pseudocode that:
- Uses standard control structures (if, for, while)
- Clearly indicates inputs and outputs
- Includes key variable names
- Shows computational steps

Format:
```
ALGORITHM Name(inputs)
    Step 1: ...
    Step 2: ...
    RETURN output
```
"""


COMPLEXITY_ANALYSIS_PROMPT = """Analyze the complexity of this algorithm:

Algorithm:
{algorithm}

Provide:
1. **Time Complexity**: Big-O notation with explanation
2. **Space Complexity**: Big-O notation with explanation
3. **Best Case**: Scenario and complexity
4. **Worst Case**: Scenario and complexity
5. **Average Case**: Scenario and complexity

Format as JSON.
"""


def get_algorithm_extraction_prompt(content: str) -> str:
    """Get algorithm extraction prompt."""
    return ALGORITHM_EXTRACTION_PROMPT.format(content=content)


def get_pseudocode_prompt(description: str) -> str:
    """Get pseudocode generation prompt."""
    return PSEUDOCODE_GENERATION_PROMPT.format(description=description)


def get_complexity_prompt(algorithm: str) -> str:
    """Get complexity analysis prompt."""
    return COMPLEXITY_ANALYSIS_PROMPT.format(algorithm=algorithm)

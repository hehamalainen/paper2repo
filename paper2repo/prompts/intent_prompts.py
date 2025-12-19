"""Prompt templates for Intent Understanding Agent."""


INTENT_UNDERSTANDING_PROMPT = """You are an Intent Understanding Agent for the Paper2Repo system.

Your task is to analyze user requirements and extract clear, actionable intent.

User Input:
{user_input}

Analyze and extract:
1. **Primary Goal**: What is the main objective?
2. **Input Type**: (research paper, arxiv link, PDF, etc.)
3. **Output Requirements**: What should be generated?
4. **Constraints**: Any specific requirements or limitations
5. **Success Criteria**: How to measure success

Return ONLY a JSON object with your analysis. Do not include any other text or explanation.
Example format:
{{
  "primary_goal": "...",
  "input_type": "...",
  "output_requirements": [...],
  "constraints": [...],
  "success_criteria": [...]
}}
"""


INTENT_REFINEMENT_PROMPT = """Refine the following intent based on additional context:

Original Intent:
{original_intent}

Additional Context:
{context}

Provide refined intent in the same JSON format.
"""


def get_intent_prompt(user_input: str) -> str:
    """Get intent understanding prompt."""
    return INTENT_UNDERSTANDING_PROMPT.format(user_input=user_input)


def get_refinement_prompt(original_intent: str, context: str) -> str:
    """Get intent refinement prompt."""
    return INTENT_REFINEMENT_PROMPT.format(
        original_intent=original_intent,
        context=context
    )

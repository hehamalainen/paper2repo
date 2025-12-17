"""Prompt templates for Concept Analysis Agent."""


CONCEPT_EXTRACTION_PROMPT = """You are a Concept Analysis Agent for the Paper2Repo system.

Analyze the following research paper content and extract key concepts.

Content:
{content}

Extract:
1. **Data Structures**: Novel data structures introduced
2. **Algorithms**: Core algorithms described
3. **Models**: Mathematical or computational models
4. **Techniques**: Implementation techniques
5. **Metrics**: Evaluation metrics and performance measures

For each concept, provide:
- Name
- Description
- Type (data_structure, algorithm, model, technique, metric)
- Properties/Attributes
- Relationships to other concepts

Format as JSON following the concept_schema.
"""


CONCEPT_RELATIONSHIP_PROMPT = """Analyze relationships between the following concepts:

Concepts:
{concepts}

Identify relationships:
- depends_on: Concept A requires Concept B
- extends: Concept A extends Concept B
- uses: Concept A uses Concept B
- related_to: Concepts are related

Return relationships as JSON array:
[
  {{"source": "...", "target": "...", "type": "...", "description": "..."}}
]
"""


def get_concept_extraction_prompt(content: str) -> str:
    """Get concept extraction prompt."""
    return CONCEPT_EXTRACTION_PROMPT.format(content=content)


def get_relationship_prompt(concepts: str) -> str:
    """Get concept relationship prompt."""
    return CONCEPT_RELATIONSHIP_PROMPT.format(concepts=concepts)

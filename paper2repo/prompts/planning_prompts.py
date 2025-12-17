"""Prompt templates for Code Planning Agent."""


BLUEPRINT_GENERATION_PROMPT = """You are a Code Planning Agent for the Paper2Repo system.

Generate a comprehensive code blueprint based on the following artifacts:

Concepts:
{concepts}

Algorithms:
{algorithms}

Requirements:
{requirements}

Generate a blueprint with ALL required sections:

1. **project_file_hierarchy**: Complete directory and file structure
2. **component_specification**: Detailed component specs with interfaces
3. **verification_protocol**: Testing strategy and validation criteria
4. **execution_environment**: Language, dependencies, build system
5. **staged_development_plan**: Phased development approach
6. **build_order**: Dependency-based build order
7. **entrypoints**: Main entry points for the application
8. **traceability_matrix**: Map concepts to components

Format as YAML following blueprint_schema.json specification.

Ensure the blueprint is:
- Complete and actionable
- Properly structured with clear dependencies
- Includes all verification requirements
- Maps back to paper concepts
"""


COMPONENT_DESIGN_PROMPT = """Design a software component for the following concept:

Concept:
{concept}

Design should include:
1. **Component Name**: Clear, descriptive name
2. **Type**: module, class, function, or interface
3. **Purpose**: What it does
4. **Public Interface**: Exposed methods/functions
5. **Dependencies**: Required components
6. **Implementation Strategy**: High-level approach

Format as JSON component specification.
"""


DEPENDENCY_ANALYSIS_PROMPT = """Analyze dependencies for the following components:

Components:
{components}

Determine:
1. **Build Order**: Order of implementation based on dependencies
2. **Circular Dependencies**: Identify any cycles
3. **Critical Path**: Key components that others depend on
4. **Suggested Phases**: Group components into development phases

Format as JSON with build_order array and analysis.
"""


def get_blueprint_prompt(concepts: str, algorithms: str, requirements: str) -> str:
    """Get blueprint generation prompt."""
    return BLUEPRINT_GENERATION_PROMPT.format(
        concepts=concepts,
        algorithms=algorithms,
        requirements=requirements
    )


def get_component_design_prompt(concept: str) -> str:
    """Get component design prompt."""
    return COMPONENT_DESIGN_PROMPT.format(concept=concept)


def get_dependency_analysis_prompt(components: str) -> str:
    """Get dependency analysis prompt."""
    return DEPENDENCY_ANALYSIS_PROMPT.format(components=components)

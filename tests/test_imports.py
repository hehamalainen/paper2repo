"""Test module imports."""
import pytest


def test_import_main_package():
    """Test importing main package."""
    import paper2repo
    assert hasattr(paper2repo, '__version__')


def test_import_agents():
    """Test importing agents."""
    from paper2repo.agents import orchestrator
    from paper2repo.agents import intent_understanding
    from paper2repo.agents import document_parsing
    from paper2repo.agents import concept_analysis
    from paper2repo.agents import algorithm_analysis
    from paper2repo.agents import code_planning
    from paper2repo.agents import reference_mining
    from paper2repo.agents import memory_manager
    from paper2repo.agents import code_generator
    from paper2repo.agents import validator


def test_import_workflows():
    """Test importing workflows."""
    from paper2repo.workflows import pipeline_orchestrator
    from paper2repo.workflows import p1_blueprint_workflow
    from paper2repo.workflows import p2_codegen_workflow
    from paper2repo.workflows import p3_verify_workflow


def test_import_memory():
    """Test importing memory systems."""
    from paper2repo.memory import codemem
    from paper2repo.memory import coderag
    from paper2repo.memory import skill_memory


def test_import_tools_perception():
    """Test importing perception tools."""
    from paper2repo.tools.perception import pdf_ingest
    from paper2repo.tools.perception import web_fetch
    from paper2repo.tools.perception import github_search


def test_import_tools_cognitive():
    """Test importing cognitive tools."""
    from paper2repo.tools.cognitive import segmentation
    from paper2repo.tools.cognitive import semantic_index
    from paper2repo.tools.cognitive import retrieval


def test_import_tools_action():
    """Test importing action tools."""
    from paper2repo.tools.action import filesystem
    from paper2repo.tools.action import command_exec
    from paper2repo.tools.action import sandbox
    from paper2repo.tools.action import git_patch


def test_import_prompts():
    """Test importing prompts."""
    from paper2repo.prompts import intent_prompts
    from paper2repo.prompts import concept_prompts
    from paper2repo.prompts import algorithm_prompts
    from paper2repo.prompts import planning_prompts
    from paper2repo.prompts import codegen_prompts
    from paper2repo.prompts import validation_prompts


def test_import_utils():
    """Test importing utilities."""
    from paper2repo.utils import config_loader
    from paper2repo.utils import llm_utils
    from paper2repo.utils import file_utils


def test_import_cli():
    """Test importing CLI."""
    from paper2repo.cli import main

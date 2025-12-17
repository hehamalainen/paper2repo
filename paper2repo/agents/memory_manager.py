"""Memory Manager Agent for context and code memory management."""
from typing import Dict, Any
import logging
from paper2repo.memory.codemem import CodeMemory, CodeMemEntry
from paper2repo.memory.coderag import CodeRAG
from paper2repo.memory.skill_memory import SkillMemory

logger = logging.getLogger(__name__)


class MemoryManagerAgent:
    """Agent for managing code memory with clean-slate approach."""
    
    def __init__(self):
        """Initialize memory manager agent."""
        self.code_memory = CodeMemory()
        self.code_rag = CodeRAG()
        self.skill_memory = SkillMemory()
        self.agent_name = "memory_manager"
    
    def clear_memory(self) -> None:
        """Clear code memory (clean-slate approach)."""
        self.code_memory.clear()
        logger.info("Code memory cleared (clean-slate)")
    
    def add_code_entry(
        self,
        file: str,
        core_purpose: str,
        public_interface: list,
        dependency_edges: list
    ) -> None:
        """Add code memory entry.
        
        Args:
            file: File path
            core_purpose: Purpose description
            public_interface: Public API
            dependency_edges: Dependencies
        """
        entry = CodeMemEntry(
            file=file,
            core_purpose=core_purpose,
            public_interface=public_interface,
            dependency_edges=dependency_edges
        )
        self.code_memory.add_entry(entry)
    
    def get_dependency_context(self, file: str) -> Dict[str, Any]:
        """Get dependency context for a file.
        
        Args:
            file: File path
            
        Returns:
            Dependency context
        """
        dependencies = self.code_memory.get_dependencies(file)
        
        context = {
            'file': file,
            'dependencies': [],
            'dependents': self.code_memory.get_dependents(file)
        }
        
        for dep_file in dependencies:
            dep_interface = self.code_memory.get_public_interface(dep_file)
            context['dependencies'].append({
                'file': dep_file,
                'interface': dep_interface
            })
        
        return context
    
    def compute_build_order(self) -> list:
        """Compute build order based on dependencies."""
        return self.code_memory.compute_build_order()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process memory management request.
        
        Args:
            input_data: Management request
            
        Returns:
            Memory stats
        """
        action = input_data.get('action', 'stats')
        
        if action == 'clear':
            self.clear_memory()
        elif action == 'add_entry':
            self.add_code_entry(
                file=input_data.get('file', ''),
                core_purpose=input_data.get('core_purpose', ''),
                public_interface=input_data.get('public_interface', []),
                dependency_edges=input_data.get('dependency_edges', [])
            )
        elif action == 'build_order':
            return {
                'build_order': self.compute_build_order()
            }
        
        return {
            'code_memory_stats': self.code_memory.get_stats(),
            'code_rag_stats': self.code_rag.get_stats(),
            'skill_memory_stats': self.skill_memory.get_stats()
        }

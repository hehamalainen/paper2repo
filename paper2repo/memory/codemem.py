"""Code memory system for tracking per-file interfaces and dependencies."""
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class CodeMemEntry:
    """Represents a single code memory entry."""
    
    def __init__(
        self,
        file: str,
        core_purpose: str,
        public_interface: List[Dict[str, Any]],
        dependency_edges: List[Dict[str, Any]],
        implementation_notes: str = "",
        tests: Optional[List[str]] = None
    ):
        """Initialize code memory entry.
        
        Args:
            file: File path relative to project root
            core_purpose: Brief description of file's purpose
            public_interface: Exported functions, classes, and APIs
            dependency_edges: Files this file depends on
            implementation_notes: Additional implementation details
            tests: Associated test files
        """
        self.file = file
        self.core_purpose = core_purpose
        self.public_interface = public_interface
        self.dependency_edges = dependency_edges
        self.implementation_notes = implementation_notes
        self.tests = tests or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'file': self.file,
            'core_purpose': self.core_purpose,
            'public_interface': self.public_interface,
            'dependency_edges': self.dependency_edges,
            'implementation_notes': self.implementation_notes,
            'tests': self.tests
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeMemEntry':
        """Create from dictionary."""
        return cls(
            file=data['file'],
            core_purpose=data['core_purpose'],
            public_interface=data['public_interface'],
            dependency_edges=data['dependency_edges'],
            implementation_notes=data.get('implementation_notes', ''),
            tests=data.get('tests', [])
        )


class CodeMemory:
    """Code memory system for tracking file interfaces and dependencies."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize code memory.
        
        Args:
            storage_path: Path to store memory state
        """
        self.storage_path = storage_path
        self.entries: Dict[str, CodeMemEntry] = {}
        
        if storage_path and storage_path.exists():
            self.load()
    
    def add_entry(self, entry: CodeMemEntry) -> None:
        """Add or update a code memory entry.
        
        Args:
            entry: Code memory entry to add
        """
        self.entries[entry.file] = entry
        logger.info(f"Added code memory entry for: {entry.file}")
    
    def get_entry(self, file: str) -> Optional[CodeMemEntry]:
        """Get code memory entry for a file.
        
        Args:
            file: File path
            
        Returns:
            Code memory entry or None
        """
        return self.entries.get(file)
    
    def get_dependencies(self, file: str) -> List[str]:
        """Get dependencies for a file.
        
        Args:
            file: File path
            
        Returns:
            List of dependency file paths
        """
        entry = self.get_entry(file)
        if not entry:
            return []
        
        return [dep['target'] for dep in entry.dependency_edges]
    
    def get_dependents(self, file: str) -> List[str]:
        """Get files that depend on given file.
        
        Args:
            file: File path
            
        Returns:
            List of dependent file paths
        """
        dependents = []
        
        for entry in self.entries.values():
            dependencies = [dep['target'] for dep in entry.dependency_edges]
            if file in dependencies:
                dependents.append(entry.file)
        
        return dependents
    
    def get_public_interface(self, file: str) -> List[Dict[str, Any]]:
        """Get public interface for a file.
        
        Args:
            file: File path
            
        Returns:
            List of public interface items
        """
        entry = self.get_entry(file)
        if not entry:
            return []
        
        return entry.public_interface
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get full dependency graph.
        
        Returns:
            Dictionary mapping files to their dependencies
        """
        graph = {}
        
        for file, entry in self.entries.items():
            graph[file] = [dep['target'] for dep in entry.dependency_edges]
        
        return graph
    
    def compute_build_order(self) -> List[str]:
        """Compute build order based on dependencies (topological sort).
        
        Returns:
            List of files in build order
        """
        # Build dependency graph
        graph = self.get_dependency_graph()
        
        # Topological sort using Kahn's algorithm
        in_degree = {file: 0 for file in graph}
        
        for dependencies in graph.values():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Find files with no dependencies
        queue = [file for file, degree in in_degree.items() if degree == 0]
        build_order = []
        
        while queue:
            file = queue.pop(0)
            build_order.append(file)
            
            # Reduce in-degree for dependents
            for dependent in self.get_dependents(file):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for cycles
        if len(build_order) != len(graph):
            logger.warning("Circular dependencies detected in code memory")
        
        return build_order
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save code memory to file.
        
        Args:
            path: Optional path to save to (overrides storage_path)
        """
        save_path = path or self.storage_path
        
        if not save_path:
            raise ValueError("No storage path specified")
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'entries': {
                file: entry.to_dict()
                for file, entry in self.entries.items()
            }
        }
        
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved code memory to: {save_path}")
    
    def load(self, path: Optional[Path] = None) -> None:
        """Load code memory from file.
        
        Args:
            path: Optional path to load from (overrides storage_path)
        """
        load_path = path or self.storage_path
        
        if not load_path or not load_path.exists():
            logger.warning("No code memory file to load")
            return
        
        with open(load_path, 'r') as f:
            data = json.load(f)
        
        self.entries = {
            file: CodeMemEntry.from_dict(entry_data)
            for file, entry_data in data.get('entries', {}).items()
        }
        
        logger.info(f"Loaded {len(self.entries)} code memory entries from: {load_path}")
    
    def clear(self) -> None:
        """Clear all code memory entries (clean-slate approach)."""
        self.entries.clear()
        logger.info("Code memory cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get code memory statistics.
        
        Returns:
            Statistics dictionary
        """
        total_dependencies = sum(
            len(entry.dependency_edges)
            for entry in self.entries.values()
        )
        
        total_interface_items = sum(
            len(entry.public_interface)
            for entry in self.entries.values()
        )
        
        return {
            'total_files': len(self.entries),
            'total_dependencies': total_dependencies,
            'total_interface_items': total_interface_items,
            'avg_dependencies_per_file': total_dependencies / len(self.entries) if self.entries else 0
        }

"""Sandbox environment tool - isolated execution environment."""
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)


class Sandbox:
    """Tool for managing isolated sandbox environments."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize sandbox manager.
        
        Args:
            base_dir: Base directory for sandboxes
        """
        if base_dir is None:
            base_dir = Path(tempfile.gettempdir()) / "paper2repo_sandboxes"
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.active_sandboxes: Dict[str, Path] = {}
        logger.info(f"Sandbox manager initialized: {self.base_dir}")
    
    def create_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Create a new sandbox environment.
        
        Args:
            sandbox_id: Unique identifier for the sandbox
            
        Returns:
            Sandbox information
        """
        try:
            if sandbox_id in self.active_sandboxes:
                return {
                    'success': False,
                    'error': f'Sandbox already exists: {sandbox_id}'
                }
            
            # Create sandbox directory
            sandbox_path = self.base_dir / sandbox_id
            sandbox_path.mkdir(parents=True, exist_ok=True)
            
            # Create standard directories
            (sandbox_path / "src").mkdir(exist_ok=True)
            (sandbox_path / "tests").mkdir(exist_ok=True)
            (sandbox_path / "output").mkdir(exist_ok=True)
            
            self.active_sandboxes[sandbox_id] = sandbox_path
            
            return {
                'success': True,
                'sandbox_id': sandbox_id,
                'path': str(sandbox_path),
                'directories': ['src', 'tests', 'output']
            }
        except Exception as e:
            logger.error(f"Failed to create sandbox {sandbox_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sandbox_path(self, sandbox_id: str) -> Optional[Path]:
        """Get the path to a sandbox.
        
        Args:
            sandbox_id: Sandbox identifier
            
        Returns:
            Sandbox path or None if not found
        """
        return self.active_sandboxes.get(sandbox_id)
    
    def destroy_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Destroy a sandbox environment.
        
        Args:
            sandbox_id: Sandbox identifier
            
        Returns:
            Operation result
        """
        try:
            if sandbox_id not in self.active_sandboxes:
                return {
                    'success': False,
                    'error': f'Sandbox not found: {sandbox_id}'
                }
            
            sandbox_path = self.active_sandboxes[sandbox_id]
            
            # Remove sandbox directory
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path)
            
            del self.active_sandboxes[sandbox_id]
            
            return {
                'success': True,
                'sandbox_id': sandbox_id,
                'destroyed': True
            }
        except Exception as e:
            logger.error(f"Failed to destroy sandbox {sandbox_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_all_sandboxes(self) -> Dict[str, Any]:
        """Clean up all active sandboxes.
        
        Returns:
            Cleanup summary
        """
        cleaned = []
        failed = []
        
        for sandbox_id in list(self.active_sandboxes.keys()):
            result = self.destroy_sandbox(sandbox_id)
            if result['success']:
                cleaned.append(sandbox_id)
            else:
                failed.append({'sandbox_id': sandbox_id, 'error': result.get('error')})
        
        return {
            'success': len(failed) == 0,
            'cleaned': cleaned,
            'failed': failed,
            'total_cleaned': len(cleaned),
            'total_failed': len(failed)
        }
    
    def list_sandboxes(self) -> Dict[str, Any]:
        """List all active sandboxes.
        
        Returns:
            List of sandbox information
        """
        sandboxes = []
        
        for sandbox_id, path in self.active_sandboxes.items():
            # Get directory size
            total_size = 0
            file_count = 0
            
            try:
                for item in path.rglob('*'):
                    if item.is_file():
                        total_size += item.stat().st_size
                        file_count += 1
            except Exception as e:
                logger.warning(f"Failed to compute size for {sandbox_id}: {e}")
            
            sandboxes.append({
                'sandbox_id': sandbox_id,
                'path': str(path),
                'exists': path.exists(),
                'file_count': file_count,
                'total_size': total_size
            })
        
        return {
            'success': True,
            'sandboxes': sandboxes,
            'total_count': len(sandboxes)
        }
    
    def execute_in_sandbox(
        self,
        sandbox_id: str,
        command: str,
        working_subdir: str = "src"
    ) -> Dict[str, Any]:
        """Execute a command in a sandbox environment.
        
        Args:
            sandbox_id: Sandbox identifier
            command: Command to execute
            working_subdir: Subdirectory to execute in
            
        Returns:
            Execution result
        """
        if sandbox_id not in self.active_sandboxes:
            return {
                'success': False,
                'error': f'Sandbox not found: {sandbox_id}'
            }
        
        from paper2repo.tools.action.command_exec import CommandExec
        
        sandbox_path = self.active_sandboxes[sandbox_id]
        working_dir = sandbox_path / working_subdir
        
        if not working_dir.exists():
            return {
                'success': False,
                'error': f'Working directory not found: {working_subdir}'
            }
        
        executor = CommandExec(working_dir=working_dir)
        result = executor.execute(command)
        
        result['sandbox_id'] = sandbox_id
        return result

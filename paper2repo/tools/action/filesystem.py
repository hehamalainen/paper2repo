"""Filesystem operations tool - sandboxed side effects."""
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import shutil
from paper2repo.utils.file_utils import FileUtils

logger = logging.getLogger(__name__)


class Filesystem:
    """Tool for sandboxed filesystem operations."""
    
    def __init__(self, sandbox_dir: Optional[Path] = None):
        """Initialize filesystem tool.
        
        Args:
            sandbox_dir: Sandbox directory for all operations
        """
        if sandbox_dir is None:
            sandbox_dir = Path.cwd() / "output"
        
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Filesystem sandbox: {self.sandbox_dir}")
    
    def create_file(
        self,
        relative_path: str,
        content: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Create a file in the sandbox.
        
        Args:
            relative_path: Path relative to sandbox
            content: File content
            overwrite: Whether to overwrite existing file
            
        Returns:
            Operation result
        """
        try:
            file_path = self.sandbox_dir / relative_path
            
            # Validate path is within sandbox
            FileUtils.validate_path(file_path, self.sandbox_dir)
            
            if file_path.exists() and not overwrite:
                return {
                    'success': False,
                    'error': f'File already exists: {relative_path}'
                }
            
            FileUtils.safe_write(file_path, content, create_parents=True)
            
            return {
                'success': True,
                'path': str(file_path),
                'relative_path': relative_path,
                'size': len(content)
            }
        except Exception as e:
            logger.error(f"Failed to create file {relative_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def read_file(self, relative_path: str) -> Dict[str, Any]:
        """Read a file from the sandbox.
        
        Args:
            relative_path: Path relative to sandbox
            
        Returns:
            File content and metadata
        """
        try:
            file_path = self.sandbox_dir / relative_path
            FileUtils.validate_path(file_path, self.sandbox_dir)
            
            content = FileUtils.safe_read(file_path)
            
            return {
                'success': True,
                'path': str(file_path),
                'relative_path': relative_path,
                'content': content,
                'size': len(content)
            }
        except Exception as e:
            logger.error(f"Failed to read file {relative_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, relative_path: str) -> Dict[str, Any]:
        """Delete a file from the sandbox.
        
        Args:
            relative_path: Path relative to sandbox
            
        Returns:
            Operation result
        """
        try:
            file_path = self.sandbox_dir / relative_path
            FileUtils.validate_path(file_path, self.sandbox_dir)
            
            FileUtils.safe_remove(file_path)
            
            return {
                'success': True,
                'path': str(file_path),
                'relative_path': relative_path
            }
        except Exception as e:
            logger.error(f"Failed to delete file {relative_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_directory(self, relative_path: str) -> Dict[str, Any]:
        """Create a directory in the sandbox.
        
        Args:
            relative_path: Path relative to sandbox
            
        Returns:
            Operation result
        """
        try:
            dir_path = self.sandbox_dir / relative_path
            FileUtils.validate_path(dir_path, self.sandbox_dir)
            
            FileUtils.ensure_directory(dir_path)
            
            return {
                'success': True,
                'path': str(dir_path),
                'relative_path': relative_path
            }
        except Exception as e:
            logger.error(f"Failed to create directory {relative_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_directory(
        self,
        relative_path: str = "",
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List directory contents.
        
        Args:
            relative_path: Path relative to sandbox
            recursive: Whether to list recursively
            
        Returns:
            Directory listing
        """
        try:
            dir_path = self.sandbox_dir / relative_path if relative_path else self.sandbox_dir
            FileUtils.validate_path(dir_path, self.sandbox_dir)
            
            if not dir_path.is_dir():
                return {
                    'success': False,
                    'error': f'Not a directory: {relative_path}'
                }
            
            files = []
            directories = []
            
            if recursive:
                items = dir_path.rglob('*')
            else:
                items = dir_path.glob('*')
            
            for item in items:
                relative = item.relative_to(self.sandbox_dir)
                if item.is_file():
                    files.append(str(relative))
                elif item.is_dir():
                    directories.append(str(relative))
            
            return {
                'success': True,
                'path': str(dir_path),
                'relative_path': relative_path,
                'files': sorted(files),
                'directories': sorted(directories),
                'total_files': len(files),
                'total_directories': len(directories)
            }
        except Exception as e:
            logger.error(f"Failed to list directory {relative_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def copy_file(
        self,
        src_relative_path: str,
        dst_relative_path: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Copy a file within the sandbox.
        
        Args:
            src_relative_path: Source path
            dst_relative_path: Destination path
            overwrite: Whether to overwrite existing file
            
        Returns:
            Operation result
        """
        try:
            src_path = self.sandbox_dir / src_relative_path
            dst_path = self.sandbox_dir / dst_relative_path
            
            FileUtils.validate_path(src_path, self.sandbox_dir)
            FileUtils.validate_path(dst_path, self.sandbox_dir)
            
            FileUtils.safe_copy(src_path, dst_path, overwrite=overwrite)
            
            return {
                'success': True,
                'source': str(src_path),
                'destination': str(dst_path),
                'src_relative': src_relative_path,
                'dst_relative': dst_relative_path
            }
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sandbox_path(self) -> Path:
        """Get the sandbox directory path."""
        return self.sandbox_dir

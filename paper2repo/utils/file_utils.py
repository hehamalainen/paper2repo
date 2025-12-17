"""Safe file operations with path validation."""
import os
import shutil
from pathlib import Path
from typing import Optional, List
import hashlib


class FileUtils:
    """Utility class for safe file operations."""
    
    @staticmethod
    def validate_path(path: Path, base_dir: Optional[Path] = None) -> Path:
        """Validate and resolve path, preventing directory traversal.
        
        Args:
            path: Path to validate
            base_dir: Base directory to constrain operations to
            
        Returns:
            Resolved absolute path
            
        Raises:
            ValueError: If path is invalid or outside base_dir
        """
        # Resolve to absolute path
        resolved = path.resolve()
        
        # Check if within base_dir if provided
        if base_dir is not None:
            base_resolved = base_dir.resolve()
            try:
                resolved.relative_to(base_resolved)
            except ValueError:
                raise ValueError(f"Path {path} is outside base directory {base_dir}")
        
        return resolved
    
    @staticmethod
    def safe_read(path: Path, encoding: str = 'utf-8') -> str:
        """Safely read file contents.
        
        Args:
            path: Path to file
            encoding: Text encoding
            
        Returns:
            File contents
        """
        validated_path = FileUtils.validate_path(path)
        
        if not validated_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not validated_path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        with open(validated_path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def safe_write(
        path: Path,
        content: str,
        encoding: str = 'utf-8',
        create_parents: bool = True
    ) -> None:
        """Safely write content to file.
        
        Args:
            path: Path to file
            content: Content to write
            encoding: Text encoding
            create_parents: Whether to create parent directories
        """
        validated_path = FileUtils.validate_path(path)
        
        if create_parents:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(validated_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> None:
        """Safely copy file.
        
        Args:
            src: Source path
            dst: Destination path
            overwrite: Whether to overwrite existing files
        """
        validated_src = FileUtils.validate_path(src)
        validated_dst = FileUtils.validate_path(dst)
        
        if not validated_src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
        
        if validated_dst.exists() and not overwrite:
            raise FileExistsError(f"Destination exists: {dst}")
        
        validated_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(validated_src, validated_dst)
    
    @staticmethod
    def safe_remove(path: Path, recursive: bool = False) -> None:
        """Safely remove file or directory.
        
        Args:
            path: Path to remove
            recursive: Whether to remove directories recursively
        """
        validated_path = FileUtils.validate_path(path)
        
        if not validated_path.exists():
            return
        
        if validated_path.is_file():
            validated_path.unlink()
        elif validated_path.is_dir():
            if recursive:
                shutil.rmtree(validated_path)
            else:
                validated_path.rmdir()
    
    @staticmethod
    def list_files(
        directory: Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory.
        
        Args:
            directory: Directory to list
            pattern: Glob pattern
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        validated_dir = FileUtils.validate_path(directory)
        
        if not validated_dir.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not validated_dir.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        if recursive:
            return list(validated_dir.rglob(pattern))
        else:
            return list(validated_dir.glob(pattern))
    
    @staticmethod
    def compute_hash(path: Path, algorithm: str = 'sha256') -> str:
        """Compute file hash.
        
        Args:
            path: Path to file
            algorithm: Hash algorithm (sha256, md5, etc.)
            
        Returns:
            Hex digest of file hash
        """
        validated_path = FileUtils.validate_path(path)
        
        if not validated_path.exists() or not validated_path.is_file():
            raise ValueError(f"Invalid file: {path}")
        
        hash_obj = hashlib.new(algorithm)
        
        with open(validated_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure directory exists, creating if necessary.
        
        Args:
            path: Directory path
            
        Returns:
            Validated directory path
        """
        validated_path = FileUtils.validate_path(path)
        validated_path.mkdir(parents=True, exist_ok=True)
        return validated_path

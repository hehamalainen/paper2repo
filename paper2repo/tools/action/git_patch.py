"""Git patch generation tool - sandboxed side effects."""
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)


class GitPatch:
    """Tool for generating and applying git patches."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize git patch tool.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._git_available = self._check_git_available()
        
        if not self._git_available:
            logger.warning("Git is not available. Git patch operations will fail.")
    
    def _check_git_available(self) -> bool:
        """Check if git is available."""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_git_command(self, args: List[str]) -> Dict[str, Any]:
        """Run a git command.
        
        Args:
            args: Git command arguments
            
        Returns:
            Command result
        """
        if not self._git_available:
            return {
                'success': False,
                'error': 'Git is not available'
            }
        
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_patch(
        self,
        from_commit: str = "HEAD~1",
        to_commit: str = "HEAD",
        output_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Create a git patch.
        
        Args:
            from_commit: Starting commit
            to_commit: Ending commit
            output_file: Optional output file path
            
        Returns:
            Patch information
        """
        try:
            # Generate patch
            args = ['diff', from_commit, to_commit]
            result = self._run_git_command(args)
            
            if not result['success']:
                return result
            
            patch_content = result['stdout']
            
            # Write to file if specified
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w') as f:
                    f.write(patch_content)
                
                return {
                    'success': True,
                    'patch_file': str(output_path),
                    'patch_size': len(patch_content)
                }
            else:
                return {
                    'success': True,
                    'patch_content': patch_content,
                    'patch_size': len(patch_content)
                }
        except Exception as e:
            logger.error(f"Failed to create patch: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_patch(
        self,
        patch_file: Path,
        check: bool = True
    ) -> Dict[str, Any]:
        """Apply a git patch.
        
        Args:
            patch_file: Path to patch file
            check: Whether to check patch applicability first
            
        Returns:
            Operation result
        """
        try:
            patch_path = Path(patch_file)
            
            if not patch_path.exists():
                return {
                    'success': False,
                    'error': f'Patch file not found: {patch_file}'
                }
            
            # Check if patch can be applied
            if check:
                check_result = self._run_git_command(
                    ['apply', '--check', str(patch_path)]
                )
                
                if not check_result['success']:
                    return {
                        'success': False,
                        'error': 'Patch cannot be applied',
                        'details': check_result.get('stderr', '')
                    }
            
            # Apply patch
            result = self._run_git_command(['apply', str(patch_path)])
            
            if result['success']:
                return {
                    'success': True,
                    'patch_file': str(patch_path),
                    'message': 'Patch applied successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to apply patch',
                    'details': result.get('stderr', '')
                }
        except Exception as e:
            logger.error(f"Failed to apply patch: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_diff_stats(
        self,
        from_commit: str = "HEAD~1",
        to_commit: str = "HEAD"
    ) -> Dict[str, Any]:
        """Get diff statistics.
        
        Args:
            from_commit: Starting commit
            to_commit: Ending commit
            
        Returns:
            Diff statistics
        """
        result = self._run_git_command(['diff', '--stat', from_commit, to_commit])
        
        if not result['success']:
            return result
        
        stats_text = result['stdout']
        
        # Parse stats
        lines = stats_text.strip().split('\n')
        files_changed = []
        
        for line in lines[:-1]:  # Last line is summary
            parts = line.split('|')
            if len(parts) == 2:
                file_path = parts[0].strip()
                changes = parts[1].strip()
                files_changed.append({
                    'file': file_path,
                    'changes': changes
                })
        
        # Parse summary line
        summary = {}
        if lines:
            summary_line = lines[-1].strip()
            # Example: "2 files changed, 10 insertions(+), 5 deletions(-)"
            import re
            match = re.search(r'(\d+) files? changed', summary_line)
            if match:
                summary['files_changed'] = int(match.group(1))
            
            match = re.search(r'(\d+) insertions?\(\+\)', summary_line)
            if match:
                summary['insertions'] = int(match.group(1))
            
            match = re.search(r'(\d+) deletions?\(-\)', summary_line)
            if match:
                summary['deletions'] = int(match.group(1))
        
        return {
            'success': True,
            'files_changed': files_changed,
            'summary': summary,
            'stats_text': stats_text
        }

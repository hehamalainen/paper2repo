"""Command execution tool - sandboxed side effects."""
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import subprocess
import shlex

logger = logging.getLogger(__name__)


class CommandExec:
    """Tool for executing commands in a sandboxed environment."""
    
    def __init__(
        self,
        working_dir: Optional[Path] = None,
        allowed_commands: Optional[List[str]] = None,
        timeout: int = 300
    ):
        """Initialize command execution tool.
        
        Args:
            working_dir: Working directory for command execution
            allowed_commands: List of allowed command prefixes (None = all allowed)
            timeout: Command timeout in seconds
        """
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.allowed_commands = allowed_commands
        self.timeout = timeout
        logger.info(f"Command execution working dir: {self.working_dir}")
    
    def execute(
        self,
        command: str,
        capture_output: bool = True,
        check: bool = False
    ) -> Dict[str, Any]:
        """Execute a shell command.
        
        Args:
            command: Command to execute
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit code
            
        Returns:
            Execution result
        """
        # Validate command
        if not self._is_command_allowed(command):
            return {
                'success': False,
                'error': f'Command not allowed: {command}',
                'allowed_commands': self.allowed_commands
            }
        
        try:
            # Execute command
            result = subprocess.run(
                shlex.split(command),
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout,
                check=check
            )
            
            return {
                'success': result.returncode == 0,
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else None,
                'stderr': result.stderr if capture_output else None,
                'working_dir': str(self.working_dir)
            }
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timeout: {command}")
            return {
                'success': False,
                'command': command,
                'error': f'Command timed out after {self.timeout}s',
                'timeout': self.timeout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}, exit code: {e.returncode}")
            return {
                'success': False,
                'command': command,
                'returncode': e.returncode,
                'stdout': e.stdout if capture_output else None,
                'stderr': e.stderr if capture_output else None,
                'error': f'Command failed with exit code {e.returncode}'
            }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'success': False,
                'command': command,
                'error': str(e)
            }
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is allowed.
        
        Args:
            command: Command to check
            
        Returns:
            True if allowed, False otherwise
        """
        # If no allowlist, all commands are allowed
        if self.allowed_commands is None:
            return True
        
        # Check if command starts with any allowed prefix
        command_parts = shlex.split(command)
        if not command_parts:
            return False
        
        command_name = command_parts[0]
        
        for allowed in self.allowed_commands:
            if command_name.startswith(allowed):
                return True
        
        return False
    
    def execute_script(
        self,
        script_content: str,
        script_type: str = "bash"
    ) -> Dict[str, Any]:
        """Execute a script.
        
        Args:
            script_content: Script content
            script_type: Script type (bash, python, etc.)
            
        Returns:
            Execution result
        """
        # Create temporary script file
        script_path = self.working_dir / f"temp_script.{script_type}"
        
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable
            script_path.chmod(0o755)
            
            # Execute based on type
            if script_type == "bash":
                command = f"bash {script_path}"
            elif script_type == "python":
                command = f"python {script_path}"
            else:
                return {
                    'success': False,
                    'error': f'Unsupported script type: {script_type}'
                }
            
            result = self.execute(command)
            
            return result
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Clean up script file
            if script_path.exists():
                script_path.unlink()
    
    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system.
        
        Args:
            command: Command to check
            
        Returns:
            True if available, False otherwise
        """
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

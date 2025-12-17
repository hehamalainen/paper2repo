"""Configuration loader with YAML support and environment variable substitution."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration from YAML files with env var substitution."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config loader.
        
        Args:
            config_path: Path to config file. If None, uses default config directory.
        """
        load_dotenv()  # Load .env file if present
        
        if config_path is None:
            # Default to config/mcp_agent.config.yaml
            config_path = Path(__file__).parent.parent / "config" / "mcp_agent.config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        
        if self.config_path.exists():
            self.load()

    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        # Substitute environment variables
        self._config = self._substitute_env_vars(raw_config)
        return self._config

    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in config.
        
        Args:
            obj: Configuration object (dict, list, or string)
            
        Returns:
            Object with environment variables substituted
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Handle ${VAR_NAME} and ${VAR_NAME:-default} patterns
            if "${" in obj:
                # Simple substitution
                import re
                pattern = r'\$\{([^:}]+)(?::-(.*?))?\}'
                
                def replace_var(match):
                    var_name = match.group(1)
                    default_val = match.group(2) if match.group(2) else ""
                    return os.environ.get(var_name, default_val)
                
                return re.sub(pattern, replace_var, obj)
        return obj

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Dot-separated key path (e.g., "llm.provider")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config


# Global config instance
_global_config: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """Get global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = ConfigLoader()
    return _global_config

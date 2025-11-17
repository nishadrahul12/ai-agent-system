import json
import os
from .typing import Dict, Any

class OrchestratorConfig:
    """
    Load and manage orchestrator configuration.
    """
    
    def __init__(self, config_path: str = "orchestrator_config.json"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Return defaults if file not found
            return self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "orchestrator": {
                "version": "1.0",
                "name": "AI Orchestrator",
                "enabled": True
            },
            "agents": {
                "max_agents": 10,
                "timeout_seconds": 30
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., "agents.max_agents")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key
            value: New value
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return full configuration as dictionary."""
        return self.config
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)


# Global config instance
config = OrchestratorConfig()

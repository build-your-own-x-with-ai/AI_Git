"""
Configuration Manager
Handles Git configuration and user settings
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class ConfigManager:
    """Manages Git client configuration"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize Configuration Manager

        Args:
            config_dir: Custom config directory path
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".gitc"

        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self.config = self._load_config()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(mode=0o700, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "user": {
                "name": "",
                "email": ""
            },
            "ssh": {
                "key_path": str(Path.home() / ".ssh" / "id_rsa")
            },
            "defaults": {
                "remote": "origin",
                "branch": "main"
            },
            "preferences": {
                "auto_add_ssh_key": True,
                "verbose": False,
                "color": True
            }
        }

    def save_config(self) -> Tuple[bool, str]:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True, f"Configuration saved to {self.config_file}"
        except Exception as e:
            return False, f"Error saving configuration: {str(e)}"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports dot notation, e.g., 'user.name')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> Tuple[bool, str]:
        """
        Set configuration value

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set

        Returns:
            Tuple of (success, message)
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

        return self.save_config()

    def delete(self, key: str) -> Tuple[bool, str]:
        """
        Delete configuration value

        Args:
            key: Configuration key to delete

        Returns:
            Tuple of (success, message)
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                return False, f"Key '{key}' not found"
            config = config[k]

        # Delete the key
        if keys[-1] in config:
            del config[keys[-1]]
            return self.save_config()
        else:
            return False, f"Key '{key}' not found"

    def list_config(self) -> Dict[str, Any]:
        """
        List all configuration values

        Returns:
            Configuration dictionary
        """
        return self.config

    def reset(self) -> Tuple[bool, str]:
        """
        Reset configuration to defaults

        Returns:
            Tuple of (success, message)
        """
        self.config = self._default_config()
        return self.save_config()

    def validate_config(self) -> Tuple[bool, list]:
        """
        Validate configuration

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate user email format
        email = self.get('user.email')
        if email and '@' not in email:
            errors.append("Invalid email format in user.email")

        # Validate SSH key path
        ssh_key_path = self.get('ssh.key_path')
        if ssh_key_path and not Path(ssh_key_path).exists():
            errors.append(f"SSH key not found at {ssh_key_path}")

        return len(errors) == 0, errors

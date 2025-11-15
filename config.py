"""
Configuration and preset management.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


# Built-in presets
BUILTIN_PRESETS = {
    "standard": {
        "description": "UPS label (Q1,Q2) + notes (Q3 rotated -90°)",
        "quadrants": {
            1: {"source": "{input}", "page": "last", "rotation": 0},
            2: {"source": "{input}", "page": "last", "rotation": 0},
            3: {"source": "{input}", "page": "second-last", "rotation": -90},
        }
    },
    "label-only-q1-q2": {
        "description": "Just the shipping label in Q1 and Q2",
        "quadrants": {
            1: {"source": "{input}", "page": "last", "rotation": 0},
            2: {"source": "{input}", "page": "last", "rotation": 0},
        }
    },
    "notes-q4": {
        "description": "Notes in bottom-right quadrant",
        "quadrants": {
            4: {"source": "{input}", "page": "second-last", "rotation": 0},
        }
    },
    "notes-q3": {
        "description": "Notes in bottom-left quadrant, rotated -90°",
        "quadrants": {
            3: {"source": "{input}", "page": "second-last", "rotation": -90},
        }
    },
}


class ConfigManager:
    """Manages configuration and presets."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for config files (defaults to ~/.label-sheet)
        """
        if config_dir is None:
            config_dir = Path.home() / ".label-sheet"
        
        self.config_dir = config_dir
        self.config_file = config_dir / "config.yaml"
        self.presets_file = config_dir / "presets.yaml"
        
        self._ensure_config_dir()
        self._user_config = self._load_user_config()
        self._user_presets = self._load_user_presets()
    
    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def _load_user_presets(self) -> Dict[str, Any]:
        """Load user-defined presets from file."""
        if not self.presets_file.exists():
            return {}
        
        try:
            with open(self.presets_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a preset by name.
        
        Args:
            name: Preset name
            
        Returns:
            Preset configuration dict, or None if not found
        """
        # Check user presets first, then built-in
        if name in self._user_presets:
            return self._user_presets[name]
        return BUILTIN_PRESETS.get(name)
    
    def list_presets(self) -> Dict[str, str]:
        """
        List all available presets with descriptions.
        
        Returns:
            Dict mapping preset name to description
        """
        presets = {}
        
        # Add built-in presets
        for name, config in BUILTIN_PRESETS.items():
            presets[name] = config.get("description", "")
        
        # Add user presets (override built-in if same name)
        for name, config in self._user_presets.items():
            presets[name] = config.get("description", "Custom preset")
        
        return presets
    
    def get_default(self, key: str, default: Any = None) -> Any:
        """
        Get a default configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        defaults = self._user_config.get("defaults", {})
        return defaults.get(key, default)
    
    def resolve_preset(
        self, 
        preset_name: str, 
        input_file: Path,
        overrides: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Dict[int, Dict[str, Any]]:
        """
        Resolve a preset configuration with input file and overrides.
        
        Args:
            preset_name: Name of the preset
            input_file: Input file path
            overrides: Manual overrides for specific quadrants
            
        Returns:
            Dict mapping quadrant number to configuration
            
        Raises:
            ValueError: If preset not found
        """
        preset = self.get_preset(preset_name)
        if not preset:
            raise ValueError(f"Preset not found: {preset_name}")
        
        quadrants = preset.get("quadrants", {})
        result = {}
        
        # Process each quadrant in preset
        for quad_num, config in quadrants.items():
            quad_num = int(quad_num)
            
            # Skip if override provided for this quadrant
            if overrides and quad_num in overrides:
                continue
            
            # Replace {input} placeholder
            source = config["source"]
            if source == "{input}":
                source = str(input_file)
            
            result[quad_num] = {
                "source": source,
                "page": config.get("page", "last"),
                "rotation": config.get("rotation", 0),
            }
        
        # Add overrides
        if overrides:
            result.update(overrides)
        
        return result
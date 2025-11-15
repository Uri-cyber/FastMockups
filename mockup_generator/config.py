"""
Configuration management for FastMockups
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """
    Configuration manager for mockup generator
    Supports YAML and JSON config files
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/config.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            return self._get_default_config()

        try:
            with open(self.config_path) as f:
                if self.config_path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif self.config_path.suffix == '.json':
                    return json.load(f)
                else:
                    print(f"Unsupported config format: {self.config_path.suffix}")
                    return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'folders': {
                'designs': 'designs',
                'templates': 'templates',
                'output': 'mockup_output'
            },
            'template_placements': {},
            'auto_detection': {
                'enabled': True,
                'method': 'contour',
                'min_area_ratio': 0.05,
                'max_area_ratio': 0.7
            },
            'effects': {
                'shadow': {
                    'enabled': False,
                    'offset': [5, 5],
                    'blur_radius': 10,
                    'opacity': 0.5
                }
            },
            'export': {
                'formats': ['png']
            },
            'processing': {
                'parallel': True,
                'max_workers': 4,
                'progress_bar': True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'folders.designs')"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: Optional[Path] = None):
        """Save configuration to file"""
        save_path = path or self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_path, 'w') as f:
                if save_path.suffix in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                elif save_path.suffix == '.json':
                    json.dump(self.config, f, indent=2)

            print(f"Configuration saved to: {save_path}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_folders(self) -> Dict[str, str]:
        """Get folder configuration"""
        return self.get('folders', {})

    def get_template_placements(self) -> Dict[str, tuple]:
        """Get template placement configuration"""
        placements = self.get('template_placements', {})
        # Convert lists to tuples
        return {k: tuple(v) if isinstance(v, list) else v for k, v in placements.items()}

    def get_effects(self) -> Dict[str, Any]:
        """Get effects configuration"""
        effects = {}

        shadow = self.get('effects.shadow', {})
        if shadow.get('enabled'):
            effects['shadow'] = {
                'offset': tuple(shadow.get('offset', [5, 5])),
                'blur': shadow.get('blur_radius', 10),
                'opacity': shadow.get('opacity', 0.5)
            }

        return effects

    def get_export_formats(self) -> list:
        """Get export formats"""
        return self.get('export.formats', ['png'])

    def get_processing_settings(self) -> Dict[str, Any]:
        """Get processing settings"""
        return {
            'parallel': self.get('processing.parallel', True),
            'max_workers': self.get('processing.max_workers', 4),
            'progress_bar': self.get('processing.progress_bar', True)
        }

    def is_auto_detection_enabled(self) -> bool:
        """Check if auto-detection is enabled"""
        return self.get('auto_detection.enabled', True)

    def get_cloud_storage_config(self) -> Optional[Dict[str, Any]]:
        """Get cloud storage configuration"""
        if not self.get('cloud_storage.enabled', False):
            return None

        provider = self.get('cloud_storage.provider', 's3')
        config = self.get(f'cloud_storage.{provider}', {})

        return {
            'provider': provider,
            **config
        }

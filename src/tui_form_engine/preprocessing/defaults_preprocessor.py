"""
Virtual Defaults Merging Preprocessor

Implements hierarchical defaults merging from global and sublayout defaults files.
Creates a unified defaults object with proper priority: sublayout > global > hardcoded.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DefaultsPreprocessor:
    """
    Preprocesses defaults by merging global and sublayout defaults hierarchically.
    
    Priority Order (highest to lowest):
    1. Sublayout defaults (from sublayout_defaults files)
    2. Global defaults (from main layout defaults_file)
    3. Hardcoded step defaults (fallback in step definitions)
    """
    
    def __init__(self, layouts_dir: Optional[Path] = None):
        """
        Initialize the DefaultsPreprocessor.
        
        Args:
            layouts_dir: Base directory for layout files
        """
        self.layouts_dir = Path(layouts_dir) if layouts_dir else Path.cwd()
    
    def merge_defaults(
        self,
        layout_path: Path,
        layout_data: Dict[str, Any],
        save_unified: bool = False,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Merge global and sublayout defaults into a unified defaults dictionary.
        
        Args:
            layout_path: Path to the main layout file
            layout_data: The loaded layout data (main layout YAML)
            save_unified: Whether to save the unified defaults to a file
            output_path: Where to save the unified defaults (if save_unified=True)
            
        Returns:
            Dictionary of merged defaults with proper hierarchy applied
        """
        logger.info(f"📊 Merging hierarchical defaults for {layout_path.name}")
        
        merged_defaults = {}
        layout_dir = layout_path.parent
        
        # Step 1: Load global defaults (base layer)
        if 'defaults_file' in layout_data:
            defaults_file_path = layout_dir / layout_data['defaults_file']
            global_defaults = self._load_defaults_file(defaults_file_path)
            
            if global_defaults:
                merged_defaults.update(global_defaults)
                logger.info(f"📊 Loaded {len(global_defaults)} global defaults")
        
        # Step 2: Load and merge sublayout defaults (override layer)
        for step in layout_data.get('steps', []):
            if 'sublayout' in step:
                sublayout_path = layout_dir / step['sublayout']
                
                if sublayout_path.exists():
                    sublayout_data = self._load_yaml(sublayout_path)
                    
                    # Check for sublayout_defaults declaration
                    if 'sublayout_defaults' in sublayout_data:
                        # Path is relative to main layout dir
                        sublayout_defaults_path = layout_dir / sublayout_data['sublayout_defaults']
                        sublayout_defaults = self._load_defaults_file(sublayout_defaults_path)
                        
                        if sublayout_defaults:
                            # Sublayout defaults override global defaults
                            merged_defaults.update(sublayout_defaults)
                            logger.info(f"📦 Merged {len(sublayout_defaults)} defaults from {sublayout_path.name}")
        
        logger.info(f"✅ Total unified defaults: {len(merged_defaults)}")
        
        # Save unified defaults if requested
        if save_unified:
            save_path = output_path or layout_dir.parent / "outputs" / "unified_defaults.yml"
            self._save_unified_defaults(merged_defaults, save_path)
        
        return merged_defaults
    
    def _load_defaults_file(self, defaults_path: Path) -> Dict[str, Any]:
        """
        Load defaults from a YAML file.
        
        Args:
            defaults_path: Path to the defaults file
            
        Returns:
            Dictionary of defaults (key: value pairs), or empty dict if not found
        """
        if not defaults_path.exists():
            logger.debug(f"Defaults file not found: {defaults_path}")
            return {}
        
        try:
            defaults_data = self._load_yaml(defaults_path)
            
            if defaults_data and 'defaults' in defaults_data:
                return defaults_data['defaults']
            
            logger.warning(f"⚠️  No 'defaults' section in {defaults_path}")
            return {}
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to load defaults from {defaults_path}: {e}")
            return {}
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _save_unified_defaults(self, merged_defaults: Dict[str, Any], output_path: Path):
        """
        Save the unified defaults to a YAML file.
        
        Args:
            merged_defaults: The merged defaults dictionary
            output_path: Where to save the file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        unified_data = {'defaults': merged_defaults}
        
        with open(output_path, 'w') as f:
            yaml.safe_dump(
                unified_data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
        
        logger.info(f"💾 Unified defaults saved to: {output_path}")

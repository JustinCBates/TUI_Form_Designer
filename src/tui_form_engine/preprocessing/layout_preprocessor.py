"""
Virtual Layout Reconstruction Preprocessor

Merges main layout + sublayouts into a single unified virtual layout structure.
The TUI Form Engine receives a complete layout after sublayout resolution and step merging.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class LayoutPreprocessor:
    """
    Preprocesses modular layouts by merging sublayouts into a unified virtual layout.
    
    Features:
    - Resolves sublayout references (subid + sublayout fields)
    - Merges steps from all sublayouts in order
    - Preserves main layout metadata
    - Validates step ID uniqueness
    """
    
    def __init__(self, layouts_dir: Optional[Path] = None):
        """
        Initialize the LayoutPreprocessor.
        
        Args:
            layouts_dir: Base directory for layout files (for relative path resolution)
        """
        self.layouts_dir = Path(layouts_dir) if layouts_dir else Path.cwd()
        self.loaded_sublayouts = set()  # Track loaded files for circular reference detection
        
    def reconstruct_virtual_layout(
        self, 
        layout_path: Path,
        save_virtual: bool = False,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Merge main layout + sublayouts into a unified virtual layout.
        
        Args:
            layout_path: Path to the main layout file
            save_virtual: Whether to save the virtual layout to a file
            output_path: Where to save the virtual layout (if save_virtual=True)
            
        Returns:
            Dictionary containing the unified virtual layout
            
        Raises:
            FileNotFoundError: If layout file or sublayout not found
            ValueError: If circular sublayout references detected
        """
        logger.info(f"🔄 Reconstructing virtual layout from {layout_path.name}")
        
        # Reset tracking for this reconstruction
        self.loaded_sublayouts = set()
        
        # Load main layout
        main_layout = self._load_yaml(layout_path)
        layout_dir = layout_path.parent
        
        # Initialize virtual layout with main metadata
        virtual_layout = {
            'title': main_layout.get('title', 'Untitled Layout'),
            'description': main_layout.get('description', ''),
            'icon': main_layout.get('icon'),
            'version': main_layout.get('version', '1.0.0'),
            'metadata': main_layout.get('metadata', {}),
            'defaults_file': main_layout.get('defaults_file'),
            'steps': []
        }
        
        # Process each step/subid in order
        step_count = 0
        sublayout_count = 0
        
        for step in main_layout.get('steps', []):
            if 'sublayout' in step:
                # This is a sublayout reference
                sublayout_path = layout_dir / step['sublayout']
                subid = step.get('subid', sublayout_path.stem)
                
                logger.info(f"📦 Processing sublayout '{subid}': {sublayout_path.name}")
                
                # Load and merge sublayout steps
                sublayout_steps = self._load_sublayout(sublayout_path, layout_dir)
                virtual_layout['steps'].extend(sublayout_steps)
                
                step_count += len(sublayout_steps)
                sublayout_count += 1
            else:
                # Regular inline step
                virtual_layout['steps'].append(step)
                step_count += 1
        
        logger.info(f"✅ Virtual layout created: {step_count} steps from {sublayout_count} sublayouts")
        
        # Validate step ID uniqueness
        self._validate_step_ids(virtual_layout['steps'])
        
        # Save virtual layout if requested
        if save_virtual:
            save_path = output_path or layout_path.parent / f"{layout_path.stem}_virtual.yml"
            self._save_virtual_layout(virtual_layout, save_path)
        
        return virtual_layout
    
    def _load_sublayout(self, sublayout_path: Path, base_dir: Path) -> List[Dict[str, Any]]:
        """
        Load a sublayout file and return its steps.
        
        Args:
            sublayout_path: Path to the sublayout file
            base_dir: Base directory for resolving relative paths
            
        Returns:
            List of step dictionaries from the sublayout
            
        Raises:
            FileNotFoundError: If sublayout file not found
            ValueError: If circular reference detected
        """
        # Check for circular references
        abs_path = sublayout_path.resolve()
        if abs_path in self.loaded_sublayouts:
            raise ValueError(f"Circular sublayout reference detected: {sublayout_path}")
        
        if not sublayout_path.exists():
            raise FileNotFoundError(f"Sublayout not found: {sublayout_path}")
        
        # Track this sublayout
        self.loaded_sublayouts.add(abs_path)
        
        # Load sublayout YAML
        sublayout_data = self._load_yaml(sublayout_path)
        
        # Extract steps
        steps = sublayout_data.get('steps', [])
        
        if not steps:
            logger.warning(f"⚠️  Sublayout {sublayout_path.name} contains no steps")
        
        return steps
    
    def _validate_step_ids(self, steps: List[Dict[str, Any]]):
        """
        Validate that all step IDs are unique.
        
        Args:
            steps: List of step dictionaries
            
        Raises:
            ValueError: If duplicate step IDs found
        """
        step_ids = set()
        duplicates = []
        
        for step in steps:
            step_id = step.get('id')
            if step_id:
                if step_id in step_ids:
                    duplicates.append(step_id)
                step_ids.add(step_id)
        
        if duplicates:
            raise ValueError(f"Duplicate step IDs found: {', '.join(duplicates)}")
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ValueError(f"Empty or invalid YAML file: {file_path}")
        
        return data
    
    def _save_virtual_layout(self, virtual_layout: Dict[str, Any], output_path: Path):
        """
        Save the virtual layout to a YAML file.
        
        Args:
            virtual_layout: The unified virtual layout dictionary
            output_path: Where to save the file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.safe_dump(
                virtual_layout,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
        
        logger.info(f"💾 Virtual layout saved to: {output_path}")

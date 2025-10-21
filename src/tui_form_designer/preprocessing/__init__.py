"""
Preprocessing module for TUI Form Designer.

Exports:
- LayoutPreprocessor: reconstructs a virtual layout by expanding sublayouts
- DefaultsPreprocessor: merges hierarchical defaults into a unified file
"""

from .layout_preprocessor import LayoutPreprocessor
from .defaults_preprocessor import DefaultsPreprocessor

__all__ = [
    "LayoutPreprocessor",
    "DefaultsPreprocessor",
]

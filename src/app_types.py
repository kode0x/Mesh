"""
Type definitions and dataclasses for the Mesh application.

Provides strongly-typed structures for application state and data transfer.
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from pathlib import Path
from enum import Enum

if TYPE_CHECKING:
    from textual.widgets import Static


class NoteFormat(str, Enum):
    """Enumeration of supported note formats."""
    
    DETAILED = "Detailed"
    SIMPLE = "Simple"
    FAST = "Fast"
    BULLET_NOTES = "Bullet Notes"
    STEP_BY_STEP = "Step-By-Step"


class RecursiveDepth(int, Enum):
    """Enumeration of recursion depth levels."""
    
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5


@dataclass
class ProjectSettings:
    """Immutable project configuration."""
    
    name: str
    api_key: str = field(repr=False)  # Don't include in repr for security
    notes_format: NoteFormat
    generate_recursive_notes: bool = False
    recursive_depth: RecursiveDepth = RecursiveDepth.LEVEL_2
    
    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if not self.name:
            raise ValueError("Project name cannot be empty")
        if not self.api_key:
            raise ValueError("API key cannot be empty")


@dataclass
class CleanupStep:
    """Represents a single cleanup step."""
    
    text: str
    widget: Optional["Static"] = None  # Textual Static widget reference
    
    def __post_init__(self) -> None:
        """Validate step data."""
        if not self.text:
            raise ValueError("Cleanup step text cannot be empty")


@dataclass
class UIState:
    """Centralized application UI state."""
    
    project_name: str = ""
    selected_format: Optional[NoteFormat] = None
    api_key: str = field(default="", repr=False)
    generate_recursive: bool = False
    recursion_depth: RecursiveDepth = RecursiveDepth.LEVEL_2
    project_root: Optional[Path] = None
    index_path: Optional[Path] = None
    index_md: Optional[str] = None
    is_cleaning_up: bool = False
    is_generating: bool = False
    
    def reset(self) -> None:
        """Reset state to initial values."""
        self.project_name = ""
        self.selected_format = None
        self.api_key = ""
        self.generate_recursive = False
        self.recursion_depth = RecursiveDepth.LEVEL_2
        self.project_root = None
        self.index_path = None
        self.index_md = None
        self.is_cleaning_up = False
        self.is_generating = False
    
    def to_project_settings(self) -> ProjectSettings:
        """Convert UI state to project settings."""
        if not self.selected_format:
            raise ValueError("Note format not selected")
        
        return ProjectSettings(
            name=self.project_name,
            api_key=self.api_key,
            notes_format=self.selected_format,
            generate_recursive_notes=self.generate_recursive,
            recursive_depth=self.recursion_depth,
        )
"""
Service layer for external integrations.

Wraps external dependencies like ProjectConfig and IndexGenerator with
cleaner interfaces and error handling.
"""

from pathlib import Path

from config import (
    DEFAULT_LLM_MODEL,
    OPENROUTER_API_URL,
    API_TIMEOUT_SECONDS,
    API_TEMPERATURE,
    INDEX_FILENAME,
)
from exceptions import APIError, FileNotFoundError as MeshFileNotFoundError, ProjectError
from app_types import NoteFormat
from logger import get_logger

# Import existing modules for compatibility
from project_config import ProjectConfig, IndexGenerator

logger = get_logger(__name__)


class ProjectService:
    """Wrapper for project configuration and management."""
    
    def __init__(self, project_name: str):
        """
        Initialize project service.
        
        Args:
            project_name: Name of the project.
        """
        self.project_name = project_name
        self._config = ProjectConfig(project_name=project_name)
        logger.info(f"Initialized ProjectService for: {project_name}")
    
    def create_project_folder(self) -> Path:
        """
        Create the project folder.
        
        Returns:
            Path to the created project folder.
            
        Raises:
            ProjectError: If folder creation fails.
        """
        try:
            self._config.create_folder()
            folder_path = self._config.project_folder_path()
            logger.info(f"Created project folder: {folder_path}")
            return folder_path
        except Exception as e:
            logger.error(f"Failed to create project folder: {e}")
            raise ProjectError(f"Failed to create project folder: {e}") from e
    
    def get_project_root(self) -> Path:
        """Get the project root path."""
        return self._config.project_folder_path()
    
    def get_index_path(self) -> Path:
        """Get the path to Index.md."""
        return self.get_project_root() / INDEX_FILENAME
    
    def index_exists(self) -> bool:
        """Check if Index.md exists."""
        return self.get_index_path().exists()
    
    @property
    def config(self) -> ProjectConfig:
        """Get the underlying ProjectConfig instance."""
        return self._config


class IndexService:
    """Wrapper for index generation and management."""
    
    def __init__(self, api_key: str, project_name: str):
        """
        Initialize index service.
        
        Args:
            api_key: OpenRouter API key.
            project_name: Name of the project.
        """
        self.api_key = api_key
        self.project_name = project_name
        self._generator = IndexGenerator(api_key=api_key, project_name=project_name)
        logger.info(f"Initialized IndexService for: {project_name}")
    
    def generate_index(self, notes_format: NoteFormat) -> str:
        """
        Generate the index markdown.
        
        Args:
            notes_format: The notes format to use.
            
        Returns:
            The generated index markdown.
            
        Raises:
            APIError: If API call fails.
        """
        try:
            logger.info(f"Generating index with format: {notes_format}")
            result = self._generator.generate_index_markdown(notes_format=notes_format.value)
            logger.info("Index generated successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to generate index: {e}")
            raise APIError(0, "Index generation failed", str(e)) from e
    
    def generate_note(
        self,
        topic: str,
        notes_format: NoteFormat,
        path: str,
    ) -> str:
        """
        Generate a note for a specific topic.
        
        Args:
            topic: The topic to generate notes for.
            notes_format: The notes format to use.
            path: The path where the note will be saved.
            
        Returns:
            The generated note markdown.
            
        Raises:
            APIError: If API call fails.
        """
        try:
            logger.debug(f"Generating note for topic: {topic}")
            result = self._generator.generate_note_markdown(
                topic=topic,
                notes_format=notes_format.value,
                path=path,
            )
            return result
        except Exception as e:
            logger.error(f"Failed to generate note for {topic}: {e}")
            raise APIError(0, "Note generation failed", str(e)) from e
    
    def get_index_root_folder(self, index_md: str) -> str:
        """Get the root folder name from index."""
        return self._generator.index_root_folder_name(index_md)
    
    def plan_notes(
        self,
        index_md: str,
        project_root: Path,
        max_depth: int,
    ) -> list:
        """
        Plan notes generation based on index.
        
        Args:
            index_md: The index markdown content.
            project_root: The root path for notes.
            max_depth: Maximum recursion depth.
            
        Returns:
            List of note tasks.
        """
        return self._generator.plan_notes_depth_first(
            index_markdown=index_md,
            project_root=project_root,
            max_depth=max_depth,
        )
    
    def cleanup(self) -> None:
        """Clean up temporary files and sensitive data."""
        try:
            logger.info("Cleaning up temporary files")
            self._generator.cleanup()
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
    
    @property
    def generator(self) -> IndexGenerator:
        """Get the underlying IndexGenerator instance."""
        return self._generator

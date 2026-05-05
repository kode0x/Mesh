# Libraries
import atexit
import os
import tempfile

from pathlib import Path


class ProjectConfig:
    """Project configuration and setup handler."""

    def _desktop_path(self) -> str:
        user_home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        desktop_path = os.path.join(user_home, "Desktop")
        return desktop_path

    def __init__(
        self,
        project_name: str,
        recursive_depth: int,
        api_key: str,
        notes_format: str,
    ):
        """Initialize project configuration.

        Args:
            project_name: Name of the project
            recursive_depth: Maximum recursion depth for file scanning
            api_key: API key for AI services
        """
        self.project_name = project_name
        self.recursive_depth = recursive_depth
        self.api_key = api_key
        self.notes_format = notes_format

    def create_folder(self) -> None:
        """Create project folder on Desktop."""
        desktop_path = self._desktop_path()
        folder_path = os.path.join(desktop_path, self.project_name)
        os.makedirs(folder_path, exist_ok=True)

    def validate(self) -> bool:
        """Check if project folder already exists on Desktop.

        Returns:
            True if folder doesn't exist (valid), False otherwise
        """
        desktop_path = self._desktop_path()
        folder_path = os.path.join(desktop_path, self.project_name)
        return not os.path.exists(folder_path)

class Research:
    """Research handler with API key management."""

    def __init__(self, api_key: str, project_name: str):
        """Initialize Research with API key.

        Args:
            api_key: API key for AI services
        """
        self.api_key = api_key
        self.project_name = project_name
        self._api_key_file_path = os.path.join(tempfile.gettempdir(), "mesh_api_key.tmp")
        with open(self._api_key_file_path, "w", encoding="utf-8") as f:
            f.write(self.api_key)
        atexit.register(self.cleanup)

    def create_index(self) -> str:
        """Create index using stored API key."""
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "generate-index.prompt.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
        return template.replace("{pName}", self.project_name)

    def cleanup(self) -> None:
        """Clear API key from memory when program ends."""
        if not hasattr(self, "api_key"):
            return

        print("API Deleting")

        try:
            if hasattr(self, "_api_key_file_path") and os.path.exists(self._api_key_file_path):
                os.remove(self._api_key_file_path)
        except OSError:
            pass

        self.api_key = ""
        del self.api_key
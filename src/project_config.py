# Libraries
import atexit
import json
import os
import tempfile
import urllib.error
import urllib.request

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
        api_key: str = "",
        notes_format: str = "",
    ):
        """Initialize project configuration.

        Args:
            project_name: Name of the project
            api_key: API key for AI services
            notes_format: Format style for generated notes
        """
        self.project_name = project_name
        self.api_key = api_key
        self.notes_format = notes_format

    def create_folder(self) -> None:
        """Create project folder on Desktop."""
        desktop_path = self._desktop_path()
        folder_path = os.path.join(desktop_path, self.project_name)
        os.makedirs(folder_path, exist_ok=True)

    def project_folder_path(self) -> Path:
        desktop_path = self._desktop_path()
        return Path(desktop_path) / self.project_name

    def validate(self) -> bool:
        """Check if project folder already exists on Desktop.

        Returns:
            True if folder doesn't exist (valid), False otherwise
        """
        desktop_path = self._desktop_path()
        folder_path = os.path.join(desktop_path, self.project_name)
        return not os.path.exists(folder_path)

class IndexGenerator:
    """Generates vault index via OpenRouter LLM API."""

    # Default model when using OpenRouter
    _DEFAULT_MODEL: str = "openai/gpt-4o-mini"

    def __init__(self, api_key: str, project_name: str):
        """Initialize IndexGenerator with API key.

        Args:
            api_key: OpenRouter API key
            project_name: Name of the vault project
        """
        self.api_key = api_key
        self.project_name = project_name
        self._api_key_file_path = os.path.join(tempfile.gettempdir(), "mesh_api_key.tmp")
        with open(self._api_key_file_path, "w", encoding="utf-8") as f:
            f.write(self.api_key)
        atexit.register(self.cleanup)

    def create_index(self) -> str:
        """Load index prompt template and substitute `{pName}`."""
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "generate-index.prompt.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
        return template.replace("{pName}", self.project_name)

    def generate_index_markdown(self, notes_format: str) -> str:
        """Generate index using OpenRouter API."""
        prompt = self.create_index()
        return self._openrouter_chat(prompt=prompt, notes_format=notes_format, model=self._DEFAULT_MODEL)

    def _openrouter_chat(self, prompt: str, notes_format: str, model: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": f"You format outputs as {notes_format} notes.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            details = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenRouter API error: {e.code} {e.reason}: {details}"
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"OpenRouter request failed: {e.reason}") from e

        parsed = json.loads(body)
        return parsed["choices"][0]["message"]["content"].strip()

    def cleanup(self) -> None:
        """Clear API key from memory when program ends."""
        if getattr(self, "_cleaned_up", False):
            return
        self._cleaned_up = True

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
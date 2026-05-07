# Libraries
import json
import os
import re
import tempfile
import urllib.error
import urllib.request

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

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

    _FORMAT_PROMPT_MAP: dict[str, str] = {
        "Detailed": "detailed.prompt.md",
        "Simple": "simple.prompt.md",
        "Fast": "fast.prompt.md",
        "Bullet Notes": "bullet-notes.prompt.md",
        "Step-By-Step": "step-by-step.prompt.md",
    }

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

    def generate_note_markdown(self, topic: str, notes_format: str, path: str) -> str:
        prompts_dir = Path(__file__).resolve().parent.parent / "prompts"

        # 1. Pick the per-format prompt if we have one
        prompt_file = self._FORMAT_PROMPT_MAP.get(notes_format, "generate-note.prompt.md")
        prompt_path = prompts_dir / prompt_file

        # 2. Fall back to the generic prompt when the per-format file is missing
        if not prompt_path.exists():
            prompt_path = prompts_dir / "generate-note.prompt.md"
            if not prompt_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        # 3. Load template and inject context
        template = prompt_path.read_text(encoding="utf-8")
        prompt = (
            template.replace("{pName}", self.project_name)
            .replace("{topic}", topic)
            .replace("{path}", path)
            .replace("{notes_format}", notes_format)
        )

        # 4. Send to LLM
        return self._openrouter_chat(prompt=prompt, notes_format=notes_format, model=self._DEFAULT_MODEL)

    @dataclass(frozen=True)
    class _TopicItem:
        title: str
        level: int

    def _parse_index(self, index_markdown: str) -> list["IndexGenerator._TopicItem"]:
        items: list[IndexGenerator._TopicItem] = []
        for raw_line in index_markdown.splitlines():
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue

            stripped = line.lstrip()

            if stripped.startswith("#"):
                hashes = len(stripped) - len(stripped.lstrip("#"))
                title = stripped[hashes:].strip()
                if title:
                    items.append(IndexGenerator._TopicItem(title=title, level=hashes))
                continue

            if stripped.startswith(("- ", "* ", "+ ")):
                indent = len(line) - len(stripped)
                title = stripped[2:].strip()
                if title:
                    level = 1 + (indent // 2)
                    items.append(IndexGenerator._TopicItem(title=title, level=level))

            m = re.match(r"^(?P<indent>\s*)(?P<num>\d+(?:\.\d+)*)\.\s+(?P<title>.+?)\s*$", line)
            if m:
                num = m.group("num")
                title = m.group("title").strip()
                if title:
                    level = num.count(".") + 1
                    items.append(IndexGenerator._TopicItem(title=title, level=level))

        return items

    def _sanitize_fs_name(self, name: str) -> str:
        invalid = '<>:"/\\|?*'
        cleaned = "".join("_" if ch in invalid else ch for ch in name).strip().rstrip(".")
        return cleaned or "Untitled"

    def index_root_folder_name(self, index_markdown: str) -> str:
        for raw_line in index_markdown.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                if title:
                    return self._sanitize_fs_name(title)
        return self._sanitize_fs_name(self.project_name)

    def generate_notes_from_index(
        self,
        index_markdown: str,
        project_root: Path,
        notes_format: str,
        max_depth: int,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> None:
        plan = self.plan_notes_from_index(
            index_markdown=index_markdown,
            project_root=project_root,
            max_depth=max_depth,
        )
        total = len(plan)
        completed = 0

        for note_path, topic, vault_rel_path in plan:
            note_md = self.generate_note_markdown(topic=topic, notes_format=notes_format, path=vault_rel_path)
            note_path.write_text(note_md + "\n", encoding="utf-8")
            completed += 1
            if progress_callback is not None:
                progress_callback(completed, total, topic)

    def plan_notes_from_index(
        self,
        index_markdown: str,
        project_root: Path,
        max_depth: int,
    ) -> list[tuple[Path, str, str]]:
        items = self._parse_index(index_markdown)
        if not items:
            return []

        plan: list[tuple[Path, str, str]] = []
        stack: list[tuple[int, str]] = []

        for item in items:
            if item.level > max_depth:
                continue

            while stack and stack[-1][0] >= item.level:
                stack.pop()
            stack.append((item.level, item.title))

            parts = [self._sanitize_fs_name(title) for _, title in stack]
            folder_path = project_root.joinpath(*parts)
            folder_path.mkdir(parents=True, exist_ok=True)

            note_filename = f"{parts[-1]}.md"
            note_path = folder_path / note_filename
            if note_path.exists():
                continue

            vault_rel_path = str(note_path.relative_to(project_root)).replace("\\", "/")
            plan.append((note_path, item.title, vault_rel_path))

        return plan

    def plan_notes_by_top_level(
        self,
        index_markdown: str,
        project_root: Path,
        max_depth: int,
    ) -> list[tuple[str, list[tuple[Path, str, str]]]]:
        items = self._parse_index(index_markdown)
        if not items:
            return []

        top_level: int | None = None
        for item in items:
            if item.level > 0:
                top_level = item.level
                break
        if top_level is None:
            return []

        result: list[tuple[str, list[tuple[Path, str, str]]]] = []
        current_block: list[IndexGenerator._TopicItem] = []

        def flush(block: list[IndexGenerator._TopicItem]) -> None:
            if not block:
                return
            title = block[0].title
            result.append((title, self._plan_from_items(block, project_root, max_depth)))

        for item in items:
            if item.level == top_level:
                flush(current_block)
                current_block = [item]
            elif current_block:
                current_block.append(item)
        flush(current_block)

        numbered: list[tuple[str, list[tuple[Path, str, str]]]] = []
        for i, (title, plan) in enumerate(result, start=1):
            folder_name = f"{i} {self._sanitize_fs_name(title)}"
            root = project_root / folder_name
            root.mkdir(parents=True, exist_ok=True)
            remapped: list[tuple[Path, str, str]] = []
            for note_path, topic, _vault_rel in plan:
                rel = note_path.relative_to(project_root)
                new_path = root / rel
                new_path.parent.mkdir(parents=True, exist_ok=True)
                vault_rel_path = str(new_path.relative_to(project_root)).replace("\\", "/")
                remapped.append((new_path, topic, vault_rel_path))
            numbered.append((title, remapped))
        return numbered

    @dataclass(frozen=True)
    class NoteTask:
        note_path: Path
        topic: str
        vault_rel_path: str
        exists: bool

    def plan_notes_depth_first(
        self,
        index_markdown: str,
        project_root: Path,
        max_depth: int,
    ) -> list["IndexGenerator.NoteTask"]:
        items = self._parse_index(index_markdown)
        if not items:
            return []

        first_h1_index: int | None = None
        for i, item in enumerate(items):
            if item.level == 1:
                first_h1_index = i
                break

        if first_h1_index is not None:
            h1_count = sum(1 for item in items if item.level == 1)
            has_deeper = any(item.level > 1 for item in items[first_h1_index + 1 :])
            if h1_count == 1 and has_deeper:
                items = items[first_h1_index + 1 :]

        if not items:
            return []

        top_level = min(item.level for item in items)
        tasks: list[IndexGenerator.NoteTask] = []
        stack: list[tuple[int, str]] = []

        for item in items:
            if item.level < top_level:
                continue
            relative_level = (item.level - top_level) + 1
            if relative_level > max_depth:
                continue

            while stack and stack[-1][0] >= item.level:
                stack.pop()
            stack.append((item.level, item.title))

            parts = [self._sanitize_fs_name(title) for _, title in stack]
            folder_path = project_root.joinpath(*parts)
            folder_path.mkdir(parents=True, exist_ok=True)

            note_filename = f"{parts[-1]}.md"
            note_path = folder_path / note_filename
            vault_rel_path = str(note_path.relative_to(project_root)).replace("\\", "/")
            tasks.append(
                IndexGenerator.NoteTask(
                    note_path=note_path,
                    topic=item.title,
                    vault_rel_path=vault_rel_path,
                    exists=note_path.exists(),
                )
            )

        return tasks

    def _plan_from_items(
        self,
        items: list["IndexGenerator._TopicItem"],
        project_root: Path,
        max_depth: int,
    ) -> list[tuple[Path, str, str]]:
        plan: list[tuple[Path, str, str]] = []
        stack: list[tuple[int, str]] = []
        for item in items:
            if item.level > max_depth:
                continue
            while stack and stack[-1][0] >= item.level:
                stack.pop()
            stack.append((item.level, item.title))
            parts = [self._sanitize_fs_name(title) for _, title in stack]
            folder_path = project_root.joinpath(*parts)
            folder_path.mkdir(parents=True, exist_ok=True)
            note_filename = f"{parts[-1]}.md"
            note_path = folder_path / note_filename
            if note_path.exists():
                continue
            vault_rel_path = str(note_path.relative_to(project_root)).replace("\\", "/")
            plan.append((note_path, item.title, vault_rel_path))
        return plan

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
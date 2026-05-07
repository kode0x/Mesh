"""
Application configuration and constants.

Centralizes all hardcoded values and configuration settings for easy maintenance
and environment-based customization.
"""

from dataclasses import dataclass
from typing import ClassVar


# API Configuration
DEFAULT_LLM_MODEL = "openai/gpt-4o-mini"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_TIMEOUT_SECONDS = 60
API_TEMPERATURE = 0.4

# Note Format Mapping
NOTE_FORMAT_MAP: dict[str, str] = {
    "1": "Detailed",
    "2": "Simple",
    "3": "Fast",
    "4": "Bullet Notes",
    "5": "Step-By-Step",
}

PROMPT_FILE_MAP: dict[str, str] = {
    "Detailed": "detailed.prompt.md",
    "Simple": "simple.prompt.md",
    "Fast": "fast.prompt.md",
    "Bullet Notes": "bullet-notes.prompt.md",
    "Step-By-Step": "step-by-step.prompt.md",
}

# Recursion Depth
DEPTH_MAP: dict[str, int] = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
}

# Validation
INVALID_FILENAME_CHARS = r'[<>:|?"*\\/]'
MIN_PROJECT_NAME_LENGTH = 1
MAX_PROJECT_NAME_LENGTH = 255

# File Paths
INDEX_FILENAME = "Index.md"
DEFAULT_PROMPT_FILENAME = "generate-note.prompt.md"

# UI Messages
MESSAGES: dict[str, str] = {
    "project_name_empty": "Project Name Cannot Be Empty",
    "project_name_invalid": "Project name contains invalid characters. Use only letters, numbers, spaces, and basic punctuation.",
    "project_exists": "Folder '{name}' Already Exists!",
    "api_key_empty": "API Key Cannot Be Empty",
    "api_error": "OpenRouter API error: {code} {reason}",
    "request_failed": "OpenRouter request failed: {reason}",
    "index_missing": "Index.md not found. Please re-run.",
    "index_path_not_set": "Index path not set. Please re-run.",
    "missing_index_content": "Missing index content. Please re-run.",
    "index_created": "Index created successfully",
    "cleanup_title": "Cleaning up...",
    "cleanup_done": "Done — see you next time.",
    "generating_notes": "Generating notes...",
    "preparing": "preparing...",
}

# UI Prompts
UI_PROMPTS: dict[str, str] = {
    "enter_project_name": "Enter Project Name:",
    "choose_format": "Choose Notes Format",
    "recursive_choice": "Generate notes for topics / subtopics?",
    "select_depth": "Select recursion depth",
    "index_ready": "Index ready",
    "start_generation": "Start generating notes now?",
    "index_not_found": "Index.md not found",
    "create_index": "Create it now?",
    "enter_api_key": "Enter OpenRouter API Key",
    "api_key_info": "Your key stays local — it is never logged",
}

# UI Navigation
UI_NAVIGATION: dict[str, str] = {
    "navigate_hint": "Navigate with ↑ / ↓  ·  Press Enter to select",
    "start_now": "Start Now",
    "quit": "Quit",
    "yes": "Yes",
    "no": "No",
    "create_index_btn": "Create Index",
}

# Cleanup Steps
CLEANUP_STEPS: list[str] = [
    "○  Deleting temporary API key file",
    "○  Clearing sensitive data from memory",
]

# Time delays (seconds)
CLEANUP_STEP_DELAY = 0.2
CLEANUP_STEP_TRANSITION_DELAY = 0.15
CLEANUP_FINAL_DELAY = 0.3
CLEANUP_EXIT_DELAY = 0.8


@dataclass
class UIConstants:
    """Centralized UI-related constants."""
    
    LOGO: ClassVar[str] = r""" 
/$$       /$$                     /$$      
| $$$    /$$$                    | $$      
| $$$$  /$$$$  /$$$$$$   /$$$$$$$| $$$$$$$ 
| $$ $$/$$ $$ /$$__  $$ /$$_____/| $$__  $$
| $$  $$$| $$| $$$$$$$$|  $$$$$$ | $$  \ $$
| $$\  $ | $$| $$_____/ \____  $$| $$  | $$
| $$ \/  | $$|  $$$$$$$ /$$$$$$$/| $$  | $$
|__/     |__/ \_______/|_______/ |__/  |__/

"""
    
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]
    
    INPUT_WIDTH = 50
    MAX_OPTION_HEIGHT = 15
    PROGRESS_PANEL_WIDTH = 60
    LOADING_PANEL_WIDTH = 44
    CLEANUP_PANEL_WIDTH = 50

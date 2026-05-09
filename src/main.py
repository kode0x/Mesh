import sys
from pathlib import Path

# Add the parent directory to sys.path when this module is imported
# This handles the case when running the script directly
script_dir = Path(__file__).parent
if script_dir.name == "src" and script_dir.parent not in sys.path:
    sys.path.insert(0, str(script_dir.parent))

import time

from textual.app import App, ComposeResult
from textual.widgets import Input, Static, OptionList, ProgressBar
from textual.containers import Center, Vertical
from textual.notifications import SeverityLevel

from config import (
    UIConstants,
    NOTE_FORMAT_MAP,
    DEPTH_MAP,
    MESSAGES,
    UI_PROMPTS,
    UI_NAVIGATION,
    CLEANUP_STEPS,
    CLEANUP_STEP_DELAY,
    CLEANUP_STEP_TRANSITION_DELAY,
    CLEANUP_FINAL_DELAY,
    CLEANUP_EXIT_DELAY,
)
from exceptions import ValidationError, ProjectError, APIError
from app_types import NoteFormat, RecursiveDepth, UIState, CleanupStep
from validators import validate_project_name, validate_api_key
from services import ProjectService, IndexService
from styles import CSS_STYLES
from logger import get_logger, setup_logging

logger = get_logger(__name__)


class MeshApp(App):    
    BINDINGS: list = UIConstants.BINDINGS
    CSS = CSS_STYLES
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.state = UIState()
        self.project_service: ProjectService | None = None
        self.index_service: IndexService | None = None
        self._cleanup_steps: list[CleanupStep] = []
        self._current_cleanup_widget: Static | None = None
        self._progress_bar: ProgressBar | None = None
        self._progress_label: Static | None = None
        self._progress_status: Static | None = None
        logger.info("Initialized MeshApp")
    
    def compose(self) -> ComposeResult:
        """Compose the initial UI."""
        with Center():
            yield Static(UIConstants.LOGO, id="logo")
            yield Static(UI_PROMPTS["enter_project_name"], id="prompt")
            yield Input(placeholder="> ", id="pname_input")
    
    # ─── State Management ───
    
    def _reset_center(self) -> Center:
        """Reset the center container while preserving the logo."""
        container = self.query_one(Center)
        existing_logo: Static | None = None
        
        try:
            existing_logo = container.query_one("#logo", Static)
        except Exception:
            pass
        
        for child in list(container.children):
            if child is existing_logo:
                continue
            child.remove()
        
        if existing_logo is None:
            container.mount(Static(UIConstants.LOGO, id="logo"))
        else:
            existing_logo.update(UIConstants.LOGO)
        
        return container
    
    def _notify_user(self, message: str, severity: str = "warning") -> None:
        """
        Notify the user with a message.
        
        Args:
            message: The message to display.
            severity: The severity level ("error", "warning", "information").
        """
        self.notify(message, severity=severity)  # type: ignore
        logger.info(f"User notification ({severity}): {message}")
    
    # ─── UI Screen Methods ───
    
    def show_format_selection(self) -> None:
        """Display format selection screen."""
        container = self._reset_center()
        container.mount(Static(UI_PROMPTS["choose_format"], classes="prompt_header"))
        container.mount(Static(UI_NAVIGATION["navigate_hint"], classes="prompt_sub"))
        format_options = list(NOTE_FORMAT_MAP.values())
        container.mount(OptionList(*format_options, id="format_select"))
    
    def show_recursive_choice(self) -> None:
        """Display recursive generation choice screen."""
        container = self._reset_center()
        container.mount(Static(UI_PROMPTS["recursive_choice"], classes="prompt_header"))
        container.mount(Static(UI_NAVIGATION["navigate_hint"], classes="prompt_sub"))
        container.mount(OptionList(UI_NAVIGATION["yes"], UI_NAVIGATION["no"], id="recursive_select"))
    
    def show_depth_selection(self) -> None:
        """Display recursion depth selection screen."""
        container = self._reset_center()
        container.mount(Static(UI_PROMPTS["select_depth"], classes="prompt_header"))
        container.mount(Static(UI_NAVIGATION["navigate_hint"], classes="prompt_sub"))
        depth_options = list(DEPTH_MAP.values())
        depth_labels = [str(v) for v in depth_options]
        container.mount(OptionList(*depth_labels, id="depth_select"))
    
    def show_api_input(self) -> None:
        """Display API key input screen."""
        container = self._reset_center()
        container.mount(Static(UI_PROMPTS["enter_api_key"], classes="prompt_header"))
        container.mount(Static(UI_PROMPTS["api_key_info"], classes="prompt_sub"))
        container.mount(Input(placeholder="> ", id="api_input", password=True))
    
    def show_start_generation_choice(self) -> None:
        """Display start generation choice screen."""
        container = self._reset_center()
        container.mount(Static(UI_PROMPTS["index_ready"], classes="prompt_header"))
        container.mount(Static(UI_PROMPTS["start_generation"], classes="prompt_sub"))
        container.mount(OptionList(UI_NAVIGATION["start_now"], UI_NAVIGATION["quit"], id="start_select"))
    
    def show_create_index_choice(self) -> None:
        """Display create index choice screen."""
        container = self._reset_center()
        container.mount(Static(UI_PROMPTS["index_not_found"], classes="prompt_header"))
        container.mount(Static(UI_PROMPTS["create_index"], classes="prompt_sub"))
        container.mount(OptionList(UI_NAVIGATION["create_index_btn"], UI_NAVIGATION["quit"], id="index_create_select"))
    
    def show_progress(self, total: int) -> None:
        """
        Display progress panel.
        
        Args:
            total: Total number of items to process.
        """
        container = self._reset_center()
        panel = Vertical(id="progress_panel")
        container.mount(panel)
        
        self._progress_status = Static(MESSAGES["generating_notes"], id="progress_status")
        panel.mount(self._progress_status)
        
        self._progress_bar = ProgressBar(total=total, id="progress_bar")
        panel.mount(self._progress_bar)
        
        self._progress_label = Static(f"0% — {MESSAGES['preparing']}", id="progress_detail")
        panel.mount(self._progress_label)
    
    def _update_progress(self, completed: int, total: int, topic: str) -> None:
        """
        Update the progress display.
        
        Args:
            completed: Number of items completed.
            total: Total number of items.
            topic: Current topic being processed.
        """
        pct = int((completed / total) * 100) if total else 0
        
        if self._progress_bar:
            self._progress_bar.progress = completed
        if self._progress_label:
            self._progress_label.update(f"{pct}%  —  {completed}/{total}  —  {topic}")
        if self._progress_status and completed == total:
            self._progress_status.update(MESSAGES["cleanup_done"])
    
    # ─── Cleanup UI ───
    
    def show_cleanup(self) -> None:
        """Display cleanup progress panel."""
        container = self._reset_center()
        panel = Vertical(id="cleanup_panel")
        container.mount(panel)
        
        panel.mount(Static(MESSAGES["cleanup_title"], id="cleanup_title"))
        
        self._cleanup_steps = []
        for step_text in CLEANUP_STEPS:
            widget = Static(step_text, classes="cleanup_step")
            self._cleanup_steps.append(CleanupStep(text=step_text, widget=widget))
            panel.mount(widget)
        
        cleanup_done = Static("", id="cleanup_done")
        panel.mount(cleanup_done)
    
    def _update_cleanup_step(self, index: int, status: str) -> None:
        """
        Update a cleanup step's visual state.
        
        Args:
            index: Step index (0-based).
            status: Step status ("active", "done", or "pending").
        """
        if index >= len(self._cleanup_steps):
            return
        
        step = self._cleanup_steps[index]
        if step.widget is None:
            return
        widget: Static = step.widget
        text = step.text
        
        if status == "active":
            widget.update(f"◐  {text[3:]}")
            widget.remove_class("cleanup_step")
            widget.remove_class("cleanup_step_done")
            widget.add_class("cleanup_step_active")
        elif status == "done":
            widget.update(f"✓  {text[3:]}")
            widget.remove_class("cleanup_step")
            widget.remove_class("cleanup_step_active")
            widget.add_class("cleanup_step_done")
        else:
            widget.update(f"○  {text[3:]}")
            widget.remove_class("cleanup_step_active")
            widget.remove_class("cleanup_step_done")
            widget.add_class("cleanup_step")
    
    def _run_cleanup_sequence(self) -> None:
        """Execute cleanup steps with UI feedback."""
        try:
            # Step 1: Delete API key file
            self.call_from_thread(self._update_cleanup_step, 0, "active")
            time.sleep(CLEANUP_STEP_DELAY)
            
            if self.index_service:
                try:
                    self.index_service.cleanup()
                except Exception as e:
                    logger.warning(f"Cleanup step 1 error: {e}")
            
            self.call_from_thread(self._update_cleanup_step, 0, "done")
            time.sleep(CLEANUP_STEP_TRANSITION_DELAY)
            
            # Step 2: Clear sensitive data
            self.call_from_thread(self._update_cleanup_step, 1, "active")
            time.sleep(CLEANUP_STEP_DELAY)
            
            self.state.reset()
            self.index_service = None
            
            self.call_from_thread(self._update_cleanup_step, 1, "done")
            time.sleep(CLEANUP_FINAL_DELAY)
            
            # Show completion message
            try:
                cleanup_done = self.query_one("#cleanup_done", expect_type=Static)
                cleanup_done.update(MESSAGES["cleanup_done"])
            except Exception:
                pass
            
            time.sleep(CLEANUP_EXIT_DELAY)
            self.call_from_thread(self.exit)
        except Exception as e:
            logger.error(f"Cleanup sequence error: {e}")
            self.call_from_thread(self.exit)
    
    def begin_cleanup(self) -> None:
        """Show cleanup UI and start cleanup sequence."""
        if self.state.is_cleaning_up:
            return
        
        self.state.is_cleaning_up = True
        
        if self.index_service is None:
            self.exit()
            return
        
        self.show_cleanup()
        self.run_worker(self._run_cleanup_sequence, thread=True)
    
    # ─── Event Handlers ───
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option list selections."""
        option_id = event.option_list.id
        option_text = str(event.option.prompt) if event.option.prompt else ""
        
        try:
            if option_id == "format_select":
                self._handle_format_selection(option_text)
            elif option_id == "recursive_select":
                self._handle_recursive_selection(option_text)
            elif option_id == "depth_select":
                self._handle_depth_selection(option_text)
            elif option_id == "start_select":
                self._handle_start_selection(option_text)
            elif option_id == "index_create_select":
                self._handle_index_create_selection(option_text)
        except Exception as e:
            logger.error(f"Option selection error: {e}")
            self._notify_user(str(e), "error")
    
    def _handle_format_selection(self, format_text: str) -> None:
        """Handle notes format selection."""
        try:
            self.state.selected_format = NoteFormat(format_text)
            logger.info(f"Format selected: {format_text}")
            self.show_recursive_choice()
        except ValueError:
            self._notify_user("Invalid format selected", "error")
    
    def _handle_recursive_selection(self, choice: str) -> None:
        """Handle recursive notes choice."""
        self.state.generate_recursive = choice == UI_NAVIGATION["yes"]
        logger.info(f"Recursive notes: {self.state.generate_recursive}")
        
        if self.state.generate_recursive:
            self.show_depth_selection()
        else:
            self.show_api_input()
    
    def _handle_depth_selection(self, depth_text: str) -> None:
        """Handle recursion depth selection."""
        try:
            depth_value = int(depth_text)
            self.state.recursion_depth = RecursiveDepth(depth_value)
            logger.info(f"Recursion depth: {depth_value}")
            self.show_api_input()
        except ValueError:
            self._notify_user("Invalid depth selected", "error")
    
    def _handle_start_selection(self, choice: str) -> None:
        """Handle start generation choice."""
        if choice == UI_NAVIGATION["quit"]:
            self.begin_cleanup()
            return
        
        self._start_note_generation()
    
    def _handle_index_create_selection(self, choice: str) -> None:
        """Handle create index choice."""
        if choice == UI_NAVIGATION["quit"]:
            self.begin_cleanup()
            return
        
        self._create_index()
    
    def _start_note_generation(self) -> None:
        """Start the note generation process."""
        try:
            if not self.state.project_root or not self.state.index_path:
                self._notify_user(MESSAGES["missing_index_content"], "error")
                self.begin_cleanup()
                return
            
            index_path = self.state.index_path
            if not index_path.exists():
                self._notify_user(MESSAGES["index_missing"], "error")
                self.begin_cleanup()
                return
            
            self.state.index_md = index_path.read_text(encoding="utf-8")
            
            # Null check for index_md
            if self.state.index_md is None:
                raise ProjectError("Index file is missing. Please generate it first.")
            
            if not self.index_service:
                raise ProjectError("Index service not initialized")
            
            root_folder = self.index_service.get_index_root_folder(self.state.index_md)
            notes_root = self.state.project_root / root_folder
            notes_root.mkdir(parents=True, exist_ok=True)
            
            # Null check before plan_notes call
            if self.state.index_md is None:
                raise ProjectError("Index file is missing. Please generate it first.")
            
            tasks = self.index_service.plan_notes(
                self.state.index_md,
                notes_root,
                self.state.recursion_depth.value,
            )
            
            if not tasks:
                self.begin_cleanup()
                return
            
            # Filter to only tasks that need processing
            tasks_to_process = [task for task in tasks if not task.exists]
            
            if not tasks_to_process:
                logger.info("All notes already exist, skipping generation")
                self.begin_cleanup()
                return
            
            logger.info(f"Starting generation of {len(tasks_to_process)} notes ({len(tasks) - len(tasks_to_process)} already exist)")
            self.show_progress(len(tasks_to_process))
            self.run_worker(self._generate_notes_worker(tasks_to_process), thread=True)
        except Exception as e:
            logger.error(f"Generation start error: {e}")
            self._notify_user(str(e), "error")
            self.begin_cleanup()
    
    def _generate_notes_worker(self, tasks_to_process):
        """Worker function for note generation."""
        def worker():
            try:
                total_to_process = len(tasks_to_process)
                processed = 0
                
                for task in tasks_to_process:
                    if self.index_service:
                        note_md = self.index_service.generate_note(
                            topic=task.topic,
                            notes_format=self.state.selected_format or NoteFormat.DETAILED,
                            path=task.vault_rel_path,
                        )
                        task.note_path.write_text(note_md + "\n", encoding="utf-8")
                        processed += 1
                        self.call_from_thread(self._update_progress, processed, total_to_process, task.topic)
                
                logger.info(f"Note generation completed: {processed} notes created")
                self.call_from_thread(self.begin_cleanup)
            except Exception as e:
                logger.error(f"Generation worker error: {e}")
                self.call_from_thread(lambda: self._notify_user(str(e), "error"))
                self.call_from_thread(self.begin_cleanup)
        
        return worker
    
    def _create_index(self) -> None:
        """Create the index file."""
        try:
            if not self.state.index_path:
                self._notify_user(MESSAGES["index_path_not_set"], "error")
                self.begin_cleanup()
                return
            
            if not self.index_service:
                raise ProjectError("Index service not initialized")
            
            logger.info("Creating index...")
            index_md = self.index_service.generate_index(
                self.state.selected_format or NoteFormat.DETAILED
            )
            self.state.index_path.write_text(index_md + "\n", encoding="utf-8")
            self.state.index_md = index_md
            
            logger.info("Index created successfully")
            self.show_start_generation_choice()
        except APIError as e:
            logger.error(f"API error creating index: {e}")
            self._notify_user(f"Failed to create index: {e}", "error")
            self.begin_cleanup()
        except Exception as e:
            logger.error(f"Unexpected error creating index: {e}")
            self._notify_user(str(e), "error")
            self.begin_cleanup()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submissions."""
        input_id = event.input.id
        value = event.value.strip()
        
        try:
            if input_id == "pname_input":
                self._handle_project_name_input(value)
            elif input_id == "api_input":
                self._handle_api_key_input(value)
        except Exception as e:
            logger.error(f"Input handling error: {e}")
            self._notify_user(str(e), "error")
    
    def _handle_project_name_input(self, project_name: str) -> None:
        """Handle project name input."""
        # Validate input
        is_valid, error_msg = validate_project_name(project_name)
        if not is_valid:
            self._notify_user(error_msg, "error")
            return
        
        # Create project
        try:
            self.state.project_name = project_name
            self.project_service = ProjectService(project_name)
            
            if self.project_service.index_exists():
                self._notify_user(MESSAGES["project_exists"].format(name=project_name), "error")
                return
            
            self.project_service.create_project_folder()
            logger.info(f"Project created: {project_name}")
            
            self.show_format_selection()
        except ProjectError as e:
            logger.error(f"Project creation error: {e}")
            self._notify_user(str(e), "error")
    
    def _handle_api_key_input(self, api_key: str) -> None:
        """Handle API key input."""
        # Validate input
        is_valid, error_msg = validate_api_key(api_key)
        if not is_valid:
            self._notify_user(error_msg, "error")
            return
        
        # Initialize services
        try:
            self.state.api_key = api_key
            
            if not self.project_service:
                raise ProjectError("Project service not initialized")
            
            self.index_service = IndexService(
                api_key=api_key,
                project_name=self.state.project_name,
            )
            
            self.state.project_root = self.project_service.get_project_root()
            self.state.index_path = self.project_service.get_index_path()
            
            logger.info("Services initialized successfully")
            
            # Determine next step
            if self.state.index_path.exists():
                self.state.index_md = self.state.index_path.read_text(encoding="utf-8")
                
                if self.state.generate_recursive:
                    self.show_start_generation_choice()
                else:
                    self.begin_cleanup()
            else:
                if self.state.generate_recursive:
                    self.show_create_index_choice()
                else:
                    self.begin_cleanup()
        except Exception as e:
            logger.error(f"API key handling error: {e}")
            self._notify_user(str(e), "error")
            self.begin_cleanup()
    
    def action_quit(self) -> None:
        """Handle quit action."""
        self.begin_cleanup()


def run_application() -> None:
    """Initialize and run the application."""
    setup_logging()
    logger.info("Starting Mesh Application")
    app = MeshApp()
    app.run()


if __name__ == "__main__":
    run_application()

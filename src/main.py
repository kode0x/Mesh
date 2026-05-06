# Libraries
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Input, Static, OptionList
from textual.containers import Center

from typing import ClassVar

# Local Imports
from project_config import ProjectConfig, IndexGenerator


class MeshApp(App):
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

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

    FORMAT_MAP: ClassVar[dict[str, str]] = {
        "1": "Detailed",
        "2": "Simple",
        "3": "Fast",
        "4": "Bullet Notes",
        "5": "Step-By-Step",
    }

    DEPTH_MAP: ClassVar[dict[str, str]] = {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
    }

    CSS = """
    Screen { align: center middle; }
    #logo { color: $success; text-style: bold; }
    #prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    #format_prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    #api_prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    Input { width: 40; }
    OptionList { width: 40; height: auto; max-height: 15; }
    """

    def __init__(self):
        super().__init__()
        self.pName = ""
        self.selected_llm = ""
        self.notes_format = ""
        self.generate_recursive_notes = False
        self.recursive_depth = 2
        self.api_key = ""

    def _option_list(self, mapping: dict[str, str]) -> list[str]:
        return list(mapping.values())

    def compose(self) -> ComposeResult:
        with Center():
            yield Static(self.LOGO, id="logo")
            yield Static("Enter Project Name:", id="prompt")
            yield Input(placeholder="> ", id="pname_input")

    def _reset_center(self) -> Center:
        container = self.query_one(Center)
        existing_logo: Static | None
        try:
            existing_logo = container.query_one("#logo", Static)
        except Exception:
            existing_logo = None

        for child in list(container.children):
            if child is existing_logo:
                continue
            child.remove()

        if existing_logo is None:
            container.mount(Static(self.LOGO, id="logo"))
        else:
            existing_logo.update(self.LOGO)
        return container

    def show_api_input(self) -> None:
        container = self._reset_center()
        container.mount(Static("Enter OpenRouter API Key:", id="api_prompt"))
        container.mount(Input(placeholder="> ", id="api_input", password=True))

    def show_format_selection(self) -> None:
        container = self._reset_center()
        container.mount(Static("Choose Notes Answer Format: (Use \u2191/\u2193 arrows, Enter to select)", id="format_prompt"))
        format_options = self._option_list(self.FORMAT_MAP)
        container.mount(OptionList(*format_options, id="format_select"))

    def show_recursive_choice(self) -> None:
        container = self._reset_center()
        container.mount(Static("Generate notes for topics/subtopics? (Use \u2191/\u2193 arrows, Enter to select)", id="format_prompt"))
        container.mount(OptionList("Yes", "No", id="recursive_select"))

    def show_depth_selection(self) -> None:
        container = self._reset_center()
        container.mount(Static("Select recursion depth: (Use \u2191/\u2193 arrows, Enter to select)", id="format_prompt"))
        depth_options = self._option_list(self.DEPTH_MAP)
        container.mount(OptionList(*depth_options, id="depth_select"))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id == "format_select":
            self.notes_format = event.option.prompt
            self.show_recursive_choice()
        elif event.option_list.id == "recursive_select":
            self.generate_recursive_notes = event.option.prompt == "Yes"
            if self.generate_recursive_notes:
                self.show_depth_selection()
            else:
                self.show_api_input()
        elif event.option_list.id == "depth_select":
            try:
                self.recursive_depth = int(event.option.prompt)
            except ValueError:
                self.recursive_depth = 2
            self.show_api_input()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "pname_input":
            self.pName = event.value.strip()
            if not self.pName:
                self.notify("Project Name Cannot Be Empty", severity="error")
                return

            self.project_config = ProjectConfig(project_name=self.pName)
            if not self.project_config.validate():
                self.notify(f"Folder '{self.pName}' Already Exists!", severity="error")
                return
            self.project_config.create_folder()
            self.selected_llm = "OpenRouter"
            self.show_format_selection()
        elif event.input.id == "api_input":
            self.api_key = event.value.strip()
            if not self.api_key:
                self.notify("API Key Cannot Be Empty", severity="error")
                return

            self.project_config.api_key = self.api_key
            self.project_config.notes_format = self.notes_format
            self.index_generator = IndexGenerator(api_key=self.api_key, project_name=self.pName)
            try:
                index_md = self.index_generator.generate_index_markdown(
                    notes_format=self.notes_format,
                )
                index_path = Path(self.project_config.project_folder_path()) / "Index.md"
                index_path.write_text(index_md + "\n", encoding="utf-8")

                if self.generate_recursive_notes:
                    self.index_generator.generate_notes_from_index(
                        index_markdown=index_md,
                        project_root=Path(self.project_config.project_folder_path()),
                        notes_format=self.notes_format,
                        max_depth=self.recursive_depth,
                    )
                self.exit()
            except Exception as e:
                self.notify(str(e), severity="error")


if __name__ == "__main__":
    app = MeshApp()
    app.run()
    if hasattr(app, "project_config"):
        print(f"Project '{app.pName}' Created At Desktop/{app.pName}")
        print(f"Index Created For '{app.pName}' Using {app.selected_llm}")
        if hasattr(app, "index_generator"):
            app.index_generator.cleanup()

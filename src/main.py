# Libraries
from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Center

from typing import ClassVar

# Local imports
from project_config import ProjectConfig, Research


class MeshApp(App):
    LOGO: ClassVar[str] = r""" /$$      /$$                     /$$      
| $$$    /$$$                    | $$      
| $$$$  /$$$$  /$$$$$$   /$$$$$$$| $$$$$$$ 
| $$ $$/$$ $$ /$$__  $$ /$$_____/| $$__  $$
| $$  $$$| $$| $$$$$$$$|  $$$$$$ | $$  \ $$
| $$\  $ | $$| $$_____/ \____  $$| $$  | $$
| $$ \/  | $$|  $$$$$$$ /$$$$$$$/| $$  | $$
|__/     |__/ \_______/|_______/ |__/  |__/"""

    LLM_MAP: ClassVar[dict[str, str]] = {
        "1": "OpenAI",
        "2": "Anthropic",
        "3": "Google DeepMind",
        "4": "Meta AI",
        "5": "Microsoft",
        "6": "Mistral AI",
        "7": "Groq",
    }

    FORMAT_MAP: ClassVar[dict[str, str]] = {
        "1": "Detailed",
        "2": "Simple",
        "3": "Fast",
        "4": "Bullet Notes",
        "5": "Step-by-Step",
    }

    CSS = """
    Screen { align: center middle; }
    #logo { color: $success; text-style: bold; }
    #prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    #llm_prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    #format_prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    #api_prompt { color: $success; text-style: bold; margin: 1 0 0 0; }
    Input { width: 40; }
    #llm_list { color: $text; margin: 0 0 1 0; }
    #format_list { color: $text; margin: 0 0 1 0; }
    """

    def __init__(self):
        super().__init__()
        self.pName = ""
        self.selected_llm = ""
        self.notes_format = ""
        self.api_key = ""

    def _numbered_list(self, mapping: dict[str, str]) -> str:
        lines = [f"{k}. {v}" for k, v in mapping.items()]
        return "\n" + "\n".join(lines)

    def compose(self) -> ComposeResult:
        with Center():
            yield Static(self.LOGO, id="logo")
            yield Static("Enter Project Name:", id="prompt")
            yield Input(placeholder="> ", id="pname_input")

    def _reset_center(self) -> Center:
        container = self.query_one(Center)
        container.remove_children()
        container.mount(Static(self.LOGO, id="logo"))
        return container

    def show_llm_selection(self) -> None:
        container = self._reset_center()
        container.mount(Static("What LLM Would You Like To Use?", id="llm_prompt"))
        llm_options = self._numbered_list(self.LLM_MAP)
        container.mount(Static(llm_options, id="llm_list"))
        container.mount(Input(placeholder="> Select LLM (1-7) ", id="llm_input"))

    def show_api_input(self) -> None:
        container = self._reset_center()
        container.mount(Static(f"Enter API Key For {self.selected_llm}:", id="api_prompt"))
        container.mount(Input(placeholder="> ", id="api_input", password=True))

    def show_format_selection(self) -> None:
        container = self._reset_center()
        container.mount(Static("Choose Notes Answer Format:", id="format_prompt"))
        format_options = self._numbered_list(self.FORMAT_MAP)
        container.mount(Static(format_options, id="format_list"))
        container.mount(Input(placeholder="> Select Format (1-5) ", id="format_input"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "pname_input":
            self.pName = event.value.strip()
            if not self.pName:
                self.notify("Project Name Cannot Be Empty", severity="error")
                return
            self.show_llm_selection()
        elif event.input.id == "llm_input":
            choice = event.value.strip()
            if choice in self.LLM_MAP:
                self.selected_llm = self.LLM_MAP[choice]
                self.show_format_selection()
            else:
                self.notify("Invalid Selection! Enter 1-7", severity="error")
        elif event.input.id == "format_input":
            choice = event.value.strip()
            if choice in self.FORMAT_MAP:
                self.notes_format = self.FORMAT_MAP[choice]
                self.show_api_input()
            else:
                self.notify("Invalid Selection! Enter 1-5", severity="error")
        elif event.input.id == "api_input":
            self.api_key = event.value.strip()
            if not self.api_key:
                self.notify("API Key Cannot Be Empty", severity="error")
                return
            self.project_config = ProjectConfig(
                project_name=self.pName,
                recursive_depth=3,
                api_key=self.api_key,
                notes_format=self.notes_format,
            )
            if self.project_config.validate():
                self.project_config.create_folder()
                self.research = Research(api_key=self.api_key, project_name=self.pName)
                self.research.create_index()
                self.exit()
            else:
                self.notify(f"Folder '{self.pName}' Already Exists!", severity="error")


if __name__ == "__main__":
    app = MeshApp()
    app.run()
    if hasattr(app, "project_config"):
        print(f"Project '{app.pName}' Created At Desktop/{app.pName}")
        print(f"Index Created For '{app.pName}' Using {app.selected_llm}")
        if hasattr(app, "research"):
            app.research.cleanup()

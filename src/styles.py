"""
Textual CSS styles for the Mesh application.

Centralized styling configuration for UI components.
"""


CSS_STYLES = """
/* ── Global ── */
Screen {
    align: center middle;
    background: $background;
}

/* ── Logo ── */
#logo {
    color: $primary;
    text-style: bold;
    margin: 1 0 1 0;
}

/* ── Prompts & Headers ── */
#prompt, .prompt_header {
    color: $text;
    text-style: bold;
    margin: 1 0 0 0;
}

.prompt_sub {
    color: $text-muted;
    margin: 0 0 1 0;
}

/* ── Input ── */
Input {
    width: 50;
    border: tall $primary;
    background: $surface;
    color: $text;
}

Input:focus {
    border: solid $primary;
}

/* ── OptionList ── */
OptionList {
    width: 50;
    height: auto;
    max-height: 15;
    border: tall $primary;
    background: $surface;
}

OptionList > .option-list--option {
    color: $text;
}

OptionList > .option-list--option-highlighted {
    background: $primary 30%;
    color: $text;
    text-style: bold;
}

OptionList > .option-list--option-hover {
    background: $primary 15%;
}

/* ── Progress Panel ── */
#progress_panel {
    width: 60;
    height: auto;
    padding: 1 2;
    border: round $primary;
    background: $surface;
}

#progress_status {
    color: $primary;
    text-style: bold;
    content-align: center middle;
    margin: 0 0 1 0;
}

#progress_bar {
    width: 100%;
}

#progress_detail {
    color: $text-muted;
    content-align: center middle;
    margin: 1 0 0 0;
}

/* ── Loading Panel ── */
#loading_panel {
    width: 44;
    height: auto;
    padding: 2;
    border: round $primary;
    background: $surface;
}

#loading_title {
    color: $primary;
    text-style: bold;
    content-align: center middle;
}

#loading_sub {
    color: $text-muted;
    content-align: center middle;
    margin: 1 0 0 0;
}

/* ── Cleanup Panel ── */
#cleanup_panel {
    width: 50;
    height: auto;
    padding: 2;
    border: round $primary;
    background: $surface;
}

#cleanup_title {
    color: $primary;
    text-style: bold;
    content-align: center middle;
    margin: 0 0 1 0;
}

.cleanup_step {
    color: $text-muted;
    margin: 0 0 0 2;
}

.cleanup_step_active {
    color: $primary;
    text-style: bold;
    margin: 0 0 0 2;
}

.cleanup_step_done {
    color: $text;
    margin: 0 0 0 2;
}

#cleanup_done {
    color: $primary;
    text-style: bold;
    content-align: center middle;
    margin: 1 0 0 0;
}
"""

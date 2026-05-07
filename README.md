# Mesh

Mesh is a small Python + Textual app that helps you start an **Obsidian-friendly** notes vault from a single topic.

It collects:

- **Project name** (used as the learning topic)
- **LLM provider** (selection)
- **Answer format** for notes (Detailed/Simple/Fast/etc.)
- **API key** (stored temporarily and deleted on exit)

Mesh currently focuses on generating the **index / table of contents prompt** and preparing your local workspace.

## Goal (Obsidian Knowledge Vault)

Mesh is designed to build an Obsidian-compatible knowledge vault by:

- Generating a **Table of Contents / Index** (topics + subtopics)
- Recursively expanding that outline into a set of Markdown notes
- Linking notes using Obsidian-style `[[Wiki Links]]`

High-level idea:

1. Create `Index.md` for the topic
2. Parse `Index.md` into a topic tree
3. For each topic/subtopic:
   - Create a note file
   - Add links to parent/children topics
   - Optionally generate learning notes in your chosen format (Detailed/Simple/Fast/etc.)

## What Mesh Creates

When you finish the setup flow, Mesh:

- Creates a folder on your **Desktop** named after your project/topic
- Keeps a `prompts/` directory in this repo to store reusable prompt templates

## How To Run

From the repo root:

```bash
python -m src.main
# or
python src/main.py
```

## User Flow

1. Enter Project Name
2. Choose LLM provider
3. Choose Notes Answer Format
4. Enter API key

## Prompts

Prompt templates live in:

```
prompts/
```

The main prompt template used right now:

- `prompts/generate-index.prompt.md`

Mesh loads that template and replaces:

- `{pName}` with the Project Name you entered at the beginning

## Output Folder (Desktop)

Mesh creates:

```
Desktop/<ProjectName>/
```

This folder is intended to become your Obsidian vault (or a subfolder you import into a vault).

### Intended Vault Structure

Mesh will generate a vault that looks like:

```
Desktop/<ProjectName>/
├── Index.md
├── <Topic 1>.md
├── <Topic 2>.md
└── ...
```

Each topic note is intended to include:

- A `#` title heading
- Links like `[[Index]]`, `[[Parent Topic]]`, `[[Child Topic]]`
- Notes written in the selected answer format

## Security Notes (API Key)

Mesh temporarily stores your API key in a local temp file while the program is running.
When Mesh exits it:

- Prints `API Deleting`
- Deletes the temp file
- Clears the API key from memory

## Status

Mesh is under active development.
The LLM calling layer and full Markdown vault generation will be built on top of the current flow.

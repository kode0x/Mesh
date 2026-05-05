# Mesh

Mesh is a minimal agent-driven system for recursively generating structured knowledge bases from a single topic input

## Overview

Mesh takes a topic name and automates the creation of a deeply organized, Obsidian-compatible knowledge repository. It builds a hierarchical Table of Contents, expands each node into markdown files, and attaches curated learning resources for every topic.

## Workflow

1. Input a topic name
2. Create a folder on the Desktop using the topic name
3. Run the agent

## Agent Responsibilities

### 1. AI-Powered Table of Contents

* **LLM-Generated Curriculum**: Uses AI (OpenAI, Anthropic, or Google) to create optimal learning paths
* **Topic Analysis**: Intelligently identifies core concepts, dependencies, and subtopics
* **Smart Sequencing**: Structures topics in order of prerequisites and complexity

### 2. Recursive Content Expansion

* Create a markdown file for each topic and subtopic
* Follow Obsidian conventions:

  * Use `[[Wiki Links]]` for internal references
  * Maintain clean, consistent headings
  * Keep one concept per file

### 3. Intelligent Study Path

* **Phase-Based Learning**: Divides curriculum into logical phases (Foundation → Advanced)
* **Time Estimates**: Provides estimated hours for each topic and phase
* **Milestone Tracking**: Defines clear milestones for progress assessment
* **Personalized Tips**: AI-generated study tips based on topic complexity

### 4. Resource Compilation

* For each topic:

  * Collect high-quality learning resources
  * Add a resource table at the top of the file

#### Resource Table Format

| Type    | Title            | Link |
| ------- | ---------------- | ---- |
| Article | Example Resource | URL  |
| Video   | Example Lecture  | URL  |
| Book    | Example Book     | URL  |

## Output Structure

```
/<topic-name>/
│
├── README.md          # Overview with study path summary
├── Index.md           # Flat navigation index
├── Study-Path.md      # Detailed learning roadmap
├── <topic-1>.md       # Topic files with progress tracking
├── <topic-2>.md
├── <topic-1>/         # Nested subtopics (if depth > 1)
│   ├── <subtopic>.md
│   └── ...
└── /assets (optional)
```

## Principles

* Minimal structure, maximum clarity
* Recursive depth over shallow coverage
* Obsidian-native formatting
* Resource-first learning approach

## Usage

### CLI Installation

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Link for global usage
npm link
```

### Commands

```bash
# Create a new knowledge base
mesh new "Machine Learning"

# Interactive mode
mesh interactive

# Configure settings
mesh config

# Show help
mesh --help
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output <path>` | Output directory | `~/Desktop` |
| `-d, --depth <number>` | Maximum recursion depth | `3` |
| `--api-key <key>` | LLM API key | env var |
| `--provider <name>` | LLM provider (openai/anthropic/google) | `openai` |
| `--model <model>` | Specific model name | provider default |

### Examples

```bash
# Basic usage (template-based, no LLM)
mesh new "TypeScript"

# With LLM-generated curriculum (requires API key)
mesh new "Machine Learning" --api-key $OPENAI_API_KEY

# Using specific provider and model
mesh new "Psychology" --provider openai --model gpt-4o

# Custom output path and depth
mesh new "React" --output ./my-notes --depth 4

# Interactive mode
mesh i

# View configuration
mesh config
```

### Environment Variables

Set these to avoid passing `--api-key` every time:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."
```

## Tech Stack

- **TypeScript** - Primary language (like Gemini CLI)
- **Node.js** - Runtime environment
- **Commander** - CLI framework
- **Chalk** - Terminal styling
- **Ora** - Loading spinners
- **LLM Integration** - OpenAI, Anthropic, Google APIs

## LLM Features

When an API key is provided, Mesh uses AI to:

1. **Design Curriculum**: Creates topic-specific, pedagogically sound learning paths
2. **Estimate Time**: Suggests realistic time commitments for each topic
3. **Define Milestones**: Sets clear achievement markers
4. **Sequence Content**: Orders topics by dependency and complexity
5. **Generate Tips**: Provides context-aware study advice

Without an API key, Mesh uses intelligent templates based on common patterns for the topic.

---

Provide a topic and execute the agent. Mesh handles the rest.

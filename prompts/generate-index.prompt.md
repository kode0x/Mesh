---
description: "Generate an index / table of contents for optimal learning of a topic"
agent: "ask"
---

# Index / Table of Contents Generator

You are an expert in the topic `{pName}`.

## Task

Generate an index (table of contents) with topics and subtopics for the most optimal learning path of this subject.

## Requirements

- Start from fundamentals and progress to advanced concepts.
- Group content into logical sections and chapters.
- Include short, clear subtopics under each topic.
- Prefer practical, learnable sequencing.
- Keep it structured and easy to follow.

## Output Format

Return Markdown only in this structure:

1. Topic
   1.1 Subtopic
   1.2 Subtopic
2. Topic
   2.1 Subtopic
   2.2 Subtopic

## Input

- `{pName}`: The subject/topic to learn.

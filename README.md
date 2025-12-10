# skill-forge

A CLI demo showcasing **Agent Skills** with progressive disclosure, inspired by Anthropic's Skills architecture.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# List skills
skill-forge list-skills

# Run a query
skill-forge run "your query here"
```

## Features

- Progressive disclosure: Load metadata → full instructions → code
- LLM-powered skill selection and execution
- Skill-based agent orchestration

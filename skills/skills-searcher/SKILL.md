---
name: skills-searcher
description: Search and discover skills in the skills folder. Use when the agent needs to find existing skills by name, description, or functionality. This skill enables the agent to explore available skills, check if a specific skill exists, or find skills matching certain criteria.
---

# Skills Searcher

This skill enables the agent to search and discover skills in the skills folder.

## When to Use

Use this skill when:
- You need to check if a specific skill exists
- Searching for skills by name or description
- Finding skills that match certain functionality
- Exploring available skills before creating a new one
- Verifying skill availability before execution

## Inputs

This skill takes inputs as a dictionary:

- `query` (required): Search query - skill name, description keywords, or functionality
- `search_type` (optional): Type of search - 'name', 'description', or 'all' (default: 'all')

## Outputs

Returns a dictionary with:
- `matches`: List of matching skills with their metadata
- `count`: Number of matches found

## Usage Examples

### Search by Name
```python
inputs = {
    'query': 'factorial',
    'search_type': 'name'
}
```

### Search by Description
```python
inputs = {
    'query': 'calculate',
    'search_type': 'description'
}
```

### Search All
```python
inputs = {
    'query': 'math',
    'search_type': 'all'
}
```

## Implementation Details

- Uses skills_loader to access skills folder
- Searches through skill metadata (name, description)
- Returns matching skills with their metadata
- Read-only access to skills folder


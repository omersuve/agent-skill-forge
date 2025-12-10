---
name: Example Todo Skill
description: Breaks a messy todo description into prioritized structured tasks.
---

# Example Todo Skill

Use this skill when a user describes tasks and wants a prioritized breakdown.

## Inputs

- `raw_todo`: free-form text describing tasks.

## Outputs

Return:

```json
{
  "tasks": [{ "title": "...", "priority": "high", "notes": "..." }]
}
```

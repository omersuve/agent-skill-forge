---
name: code-executor
description: Execute Python code in a sandboxed environment to solve problems, filter data, perform calculations, or process information. Use when the agent needs to write and execute deterministic Python code dynamically. This skill enables code-first problem solving for tasks like data filtering, mathematical computations, text processing, or any deterministic operation that benefits from code execution rather than LLM reasoning.
---

# Code Executor

This skill enables the agent to write and execute Python code in a secure sandbox environment.

## When to Use

Use this skill when:
- You need to filter, process, or transform large datasets
- Performing mathematical calculations or aggregations
- Processing structured data (lists, dictionaries)
- Any deterministic operation that would benefit from code execution
- When code execution would be faster and more cost-effective than LLM reasoning

Avoid using this skill if:
- The task requires non-deterministic reasoning or creativity
- You need to access external APIs or filesystem
- The operation requires network access

## Inputs

This skill takes inputs as a dictionary:

- `code` (required): Python code string that defines a `run_skill(inputs: dict) -> dict` function
- `inputs` (optional): Input data dictionary to pass to the code

## Outputs

Returns a dictionary with execution results.

## Usage Examples

### Data Filtering
```python
code = """
def run_skill(inputs: dict) -> dict:
    data = inputs.get('data', [])
    filtered = [item for item in data if item.get('status') == 'pending']
    return {'filtered': filtered, 'count': len(filtered)}
"""
```

### Mathematical Calculation
```python
code = """
def run_skill(inputs: dict) -> dict:
    numbers = inputs.get('numbers', [])
    return {
        'sum': sum(numbers),
        'average': sum(numbers) / len(numbers) if numbers else 0,
        'max': max(numbers) if numbers else None,
        'min': min(numbers) if numbers else None
    }
"""
```

## Implementation Details

- Code runs in a restricted sandbox with only safe modules: json, math, csv, re, statistics
- No filesystem or network access
- Must define `run_skill(inputs: dict) -> dict` function
- Returns results as a dictionary


---
name: factorial-calculator
description: Calculates the factorial of a positive integer. Use this skill when you need to find the product of all positive integers less than or equal to a given number. Triggers for this skill include phrases like "factorial of [number]" or "calculate [number]!".
---

# Factorial Calculator

This skill calculates the factorial of a positive integer.

## When to Use

Use this skill when:
- You need to calculate the factorial of a specific number
- The input is a positive integer

Avoid using this skill if:
- The input is not a positive integer
- You need to calculate factorials for a large batch of numbers (consider a script instead)

## Inputs

This skill takes a single input:

1. `n` (required): The positive integer to calculate the factorial for

## Outputs

This skill returns a single output:

- The factorial of `n`, which is the product of all positive integers less than or equal to `n`

## Usage Examples

Here are some example inputs and their expected outputs:

| Input | Output |
|-------|--------|
| 0     | 1      |
| 1     | 1      |
| 5     | 120    |
| 10    | 3628800 |

## Implementation

To calculate the factorial of `n`:

1. If `n` is 0 or 1, return 1
2. Otherwise, multiply all positive integers from 1 to `n` together
3. Return the result

Use the following formula:

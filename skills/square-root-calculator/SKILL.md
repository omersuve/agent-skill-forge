---
name: calculate-square-root
description: "Calculates the square root of a number. The square root is the value that, when multiplied by itself, equals the original number. Use this skill when you need to find the square root of a positive real number."
---

# Calculate Square Root

This skill calculates the square root of a given number.

## When to Use

Use this skill when you need to calculate the square root of a positive real number. The square root of a number is the value that, when multiplied by itself, equals the original number.

## Inputs

This skill takes a single input:

- `number` (required): The positive real number to calculate the square root of.

## Output

The skill returns the square root of the given number, a positive real number.

## Usage

To use this skill, provide the `number` as input. The skill will return the calculated square root.

### Examples

Example 1:
- Input: `9`
- Output: `3`

Example 2: 
- Input: `2`
- Output: `1.4142135623730951` 

Example 3:
- Input: `0.25`
- Output: `0.5`

## Implementation Note

This skill uses Python's built-in `math.sqrt()` function to calculate the square root. No additional scripts or references are needed.

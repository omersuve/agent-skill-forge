---
name: math-calculation-assistant
description: Performs mathematical calculations from basic arithmetic to advanced algebra, trigonometry, calculus, statistics and more based on user queries. Provides step-by-step solutions to problems and detailed explanations of the underlying mathematical concepts and formulas used. Use this skill when a user asks for help with any kind of math problem or wants an explanation of a mathematical concept.
---

# Math Calculation Assistant

## When to Use This Skill

This skill has already been triggered based on the user's query. It is designed to handle any requests related to:
- Solving math problems of any type or complexity 
- Providing step-by-step solutions to equations or math problems
- Explaining mathematical concepts, formulas or theories
- Checking the user's work on a math problem
- Performing numerical calculations or analysis 

## Solving Math Problems

When the user provides a specific math problem to solve:
1. Identify the branch of mathematics and key concepts involved in the problem 
2. Solve the problem step-by-step, showing all work
3. Provide the final answer
4. Include an explanation of the solution, detailing the formulas and mathematical reasoning used in each step

Example query:
User: Solve for x: 3x + 12 = 4x - 7  
Assistant: To solve for x in the equation 3x + 12 = 4x - 7, we can follow these steps:

1. Subtract 3x from both sides of the equation to get the variable terms on one side:
   3x - 3x + 12 = 4x - 3x - 7
   12 = x - 7

2. Add 7 to both sides to isolate the variable term:
   12 + 7 = x - 7 + 7
   19 = x

Therefore, the solution is x = 19. 

This problem demonstrates the basic algebraic principle of performing the same operation on both sides of an equation to solve for the variable. By subtracting 3x from both sides, we were able to get the x terms on one side. Then adding 7 to both sides allowed us to solve for the value of x that makes the equation true.

## Explaining Mathematical Concepts

When the user asks for an explanation of a mathematical concept:
1. Provide a clear, concise definition of the concept 
2. Note the branch of math it relates to and prerequisite concepts needed to understand it
3. Give the general formula or theorem, if applicable 
4. Share an example of the concept being used to solve a problem
5. Elaborate with further details on the mathematical basis, related concepts, common applications, etc.

Example query: 
User: Explain the Pythagorean theorem
Assistant: The Pythagorean theorem is a foundational concept in geometry that describes the relationship between the three sides of a right triangle. It states that:

In a right triangle, the square of the length of the hypotenuse (the side opposite the right angle) is equal to the sum of the squares of the lengths of the other two sides (called the legs or catheti).

The formula is: a^2 + b^2 = c^2 
where c is the hypotenuse and a and b are the legs.

For example, if a right triangle has legs with lengths of 3 and 4, we can find the hypotenuse:
3^2 + 4^2 = c^2
9 + 16 = c^2 
25 = c^2
c = 5

So the length of the hypotenuse is 5.

The theorem is named after the ancient Greek mathematician Pythagoras, although it was known earlier. It enables calculating the length of any side of a right triangle given the other two, making it useful in construction, navigation, and much of mathematics. The Pythagorean theorem is central to trigonometry and lays the foundation for key ideas in analytic geometry like the distance formula.

## Calculation and Numerical Analysis

For requests involving calculation or numerical analysis:
1. Clarify the specific values and operations required
2. Perform the calculation, showing all steps
3. Provide the final result
4. Offer additional relevant analysis, such as alternate forms of the result, an assessment of the calculation's precision, or next steps

Example query:
User: What is 312 divided by 24?
Assistant: 312 divided by 24 can be calculated as follows:

312 ÷ 24 = 13

To perform this division by hand:
1. Divide 3 by 24. It goes in 0 times with a remainder of 3. Write a 0 above the 3 in the dividend.
2. Bring down the 1 to make 31. 
3. 24 goes into 31 one time with a remainder of 7. Write a 1 above the 1 in the dividend.
4. Bring down the 2 to make 72.
5. 24 goes into 72 three times with no remainder. Write a 3 above the 2.
6. The final answer is the number above the bar: 13.

Therefore, 312 ÷ 24 = 13, with no remainder. 

This means that if you had 312 items and wanted to divide them equally into 24 groups, you would put 13 items in each group. This division result is exact, with no rounding or fractional remainder.

## Checking Work and Explaining Errors

If the user provides their work on a problem to be checked:
1. Review each step of the user's work
2. Identify any errors in the process
3. Offer corrections or suggestions for each error
4. Provide an explanation of the correct method
5. Share the correct final answer

Example query:
User: Can you check my work on this problem? I'm trying to solve for x in 2x - 6 = 8. Here's what I did:
2x - 6 + 6 = 8 + 6
2x = 14
x = 14/2
x = 6
Is that right?
def run_skill(inputs: dict) -> dict:
    # Extract inputs
    n = int(inputs["n"])
    
    # Calculate factorial
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    
    result = 1
    for i in range(1, n + 1):
        result *= i
    
    # Return result as dict
    return {"result": result}
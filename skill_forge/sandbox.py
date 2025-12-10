"""Sandbox execution for skill_code.py files."""
import ast
import sys
from typing import Dict, Any, Optional
import json
import math
import csv
import re
import statistics


# Safe modules whitelist
SAFE_MODULES = {
    'json': json,
    'math': math,
    'csv': csv,
    're': re,
    'statistics': statistics,
}

# Safe builtins
SAFE_BUILTINS = {
    'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'float', 'int', 'len',
    'list', 'max', 'min', 'range', 'round', 'sorted', 'str', 'sum', 'tuple',
    'zip', 'print', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr',
    'ValueError', 'KeyError', 'TypeError', 'AttributeError', 'Exception',
}


class SandboxError(Exception):
    """Error raised during sandbox execution."""
    pass


class CodeValidator:
    """Validates Python code before execution."""
    
    @staticmethod
    def validate(code: str) -> tuple[bool, Optional[str]]:
        """Validate code for safety.
        
        Args:
            code: Python code to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        try:
            # Parse code to AST
            tree = ast.parse(code)
            
            # Check for dangerous operations
            for node in ast.walk(tree):
                # Check for imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in SAFE_MODULES:
                            return False, f"Import of '{alias.name}' is not allowed. Only safe modules are allowed: {list(SAFE_MODULES.keys())}"
                
                if isinstance(node, ast.ImportFrom):
                    if node.module not in SAFE_MODULES:
                        return False, f"Import from '{node.module}' is not allowed. Only safe modules are allowed: {list(SAFE_MODULES.keys())}"
                
                # Check for file operations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ('open', 'file', 'exec', 'eval', '__import__'):
                            return False, f"Use of '{node.func.id}' is not allowed in sandbox"
                
                # Check for dangerous attributes
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == '__builtins__':
                        return False, "Direct access to __builtins__ is not allowed"
            
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"


class SandboxExecutor:
    """Executes Python code in a restricted sandbox environment."""
    
    def __init__(self):
        """Initialize sandbox executor."""
        self.validator = CodeValidator()
        # Inject skills_loader for read-only access to skills folder
        from .skill_loader import SkillLoader
        self.skills_loader = SkillLoader()
    
    def execute(self, code: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code in sandbox with given inputs.
        
        Args:
            code: Python code to execute (must define run_skill function).
            inputs: Input dictionary for the skill.
            
        Returns:
            Result dictionary from run_skill function.
            
        Raises:
            SandboxError: If code is invalid or execution fails.
        """
        # Validate code
        is_valid, error = self.validator.validate(code)
        if not is_valid:
            raise SandboxError(f"Code validation failed: {error}")
        
        # Create restricted globals
        # Get builtins module
        import builtins
        safe_builtins_dict = {}
        for name in SAFE_BUILTINS:
            if hasattr(builtins, name):
                safe_builtins_dict[name] = getattr(builtins, name)
        
        # Create restricted globals with skills_loader access
        restricted_globals = {
            '__builtins__': safe_builtins_dict,
            **SAFE_MODULES,
            # Add type constructors directly
            'dict': dict,
            'list': list,
            'tuple': tuple,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            # Add exception types
            'Exception': Exception,
            'ValueError': ValueError,
            'KeyError': KeyError,
            'TypeError': TypeError,
            'AttributeError': AttributeError,
            # Add skills_loader for read-only access to skills folder
            'skills_loader': self.skills_loader,
        }
        
        # Add globals function that returns the restricted globals dict
        def get_globals():
            return restricted_globals
        restricted_globals['globals'] = get_globals
        
        # Create restricted locals
        restricted_locals = {}
        
        try:
            # Execute code in restricted environment
            exec(code, restricted_globals, restricted_locals)
            
            # Check if run_skill function exists
            if 'run_skill' not in restricted_locals:
                raise SandboxError("Code must define a 'run_skill' function with signature: def run_skill(inputs: dict) -> dict")
            
            run_skill = restricted_locals['run_skill']
            
            # Validate function signature
            if not callable(run_skill):
                raise SandboxError("run_skill must be a callable function")
            
            # Call run_skill with inputs
            result = run_skill(inputs)
            
            # Validate result is a dict
            if not isinstance(result, dict):
                raise SandboxError(f"run_skill must return a dict, got {type(result)}")
            
            return result
            
        except SandboxError:
            raise
        except Exception as e:
            raise SandboxError(f"Execution error: {e}")
    
    def execute_skill_code(self, skill_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load and execute skill_code.py for a skill.
        
        Args:
            skill_name: Name of the skill directory.
            inputs: Input dictionary for the skill.
            
        Returns:
            Result dictionary from run_skill function.
            
        Raises:
            SandboxError: If code loading or execution fails.
        """
        from .skill_loader import SkillLoader
        
        loader = SkillLoader()
        code = loader.load_skill_code(skill_name)
        
        if not code:
            raise SandboxError(f"skill_code.py not found for skill '{skill_name}'")
        
        return self.execute(code, inputs)


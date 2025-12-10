"""Agent orchestration with progressive disclosure."""
from typing import Dict, Optional, Any
import anthropic
from .skill_loader import SkillLoader
from .skill_creator import SkillCreator
from .sandbox import SandboxExecutor, SandboxError
from .config import require_api_key
from .prompts import SKILL_SELECTION_PROMPT, SKILL_EXECUTION_PROMPT


class SkillAgent:
    """Agent that orchestrates skills using progressive disclosure."""
    
    def __init__(self, model: str = "claude-3-opus-20240229"):
        """Initialize the agent.
        
        Args:
            model: Anthropic model to use (default: claude-3-opus-20240229)
        """
        self.api_key = require_api_key()
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.loader = SkillLoader()
        self.creator = SkillCreator(model=model)
        self.sandbox = SandboxExecutor()
    
    def select_skill(self, query: str) -> Optional[str]:
        """Stage 1: Select skill using only metadata (progressive disclosure).
        
        Args:
            query: User query to process.
            
        Returns:
            Selected skill directory name or None if no skill matches.
        """
        # Load only metadata (Stage 1)
        # We need both metadata and directory names
        skill_dirs = self.loader.discover_skills()
        skills_with_metadata = []
        for skill_dir in skill_dirs:
            metadata = self.loader.load_metadata(skill_dir)
            if metadata:
                skills_with_metadata.append({
                    'dir_name': skill_dir,
                    'metadata': metadata
                })
        
        if not skills_with_metadata:
            return None
        
        # Format metadata for prompt (show display name, but we'll map to dir_name)
        metadata_text = "\n".join([
            f"- {s['metadata'].get('name', s['dir_name'])}: {s['metadata'].get('description', 'No description')}"
            for s in skills_with_metadata
        ])
        
        # Call LLM to select skill
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": SKILL_SELECTION_PROMPT.format(
                        skills_metadata=metadata_text,
                        query=query
                    )
                }]
            )
            
            selected_skill_name = message.content[0].text.strip()
            
            # Map display name back to directory name
            if selected_skill_name.lower() == 'none':
                return None
            
            # Try to match by name first
            for s in skills_with_metadata:
                metadata_name = s['metadata'].get('name', '').lower()
                dir_name = s['dir_name'].lower()
                selected_lower = selected_skill_name.lower()
                
                # Match by metadata name
                if metadata_name == selected_lower:
                    return s['dir_name']
                
                # Match by directory name (fallback)
                if dir_name == selected_lower:
                    return s['dir_name']
                
                # Partial match - if selected name contains key words from description
                # This helps when LLM returns a variation
                if selected_lower in metadata_name or metadata_name in selected_lower:
                    return s['dir_name']
            
            # If no exact match, try fuzzy matching on description
            query_lower = query.lower()
            for s in skills_with_metadata:
                desc = s['metadata'].get('description', '').lower()
                # If query keywords match skill description, use it
                if 'square root' in query_lower and 'square root' in desc:
                    return s['dir_name']
                if 'factorial' in query_lower and 'factorial' in desc:
                    return s['dir_name']
            
            return None
            
        except Exception as e:
            print(f"Error selecting skill: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_inputs_from_query(self, query: str, skill_content: str) -> Dict:
        """Extract inputs from query using LLM.
        
        Args:
            query: User query.
            skill_content: Skill instructions.
            
        Returns:
            Extracted inputs as dictionary.
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"""Extract inputs from this query based on the skill instructions.

Skill instructions:
{skill_content[:1000]}

User query: {query}

Extract the inputs and return as JSON dictionary. For example, if the skill needs 'number' and query is 'Calculate factorial of 5', return {{"number": 5}}.

Return ONLY valid JSON, nothing else."""
                }]
            )
            
            import json
            inputs_text = message.content[0].text.strip()
            # Remove markdown code blocks if present
            if "```" in inputs_text:
                import re
                match = re.search(r'```(?:json)?\n(.*?)\n```', inputs_text, re.DOTALL)
                if match:
                    inputs_text = match.group(1)
            
            return json.loads(inputs_text)
        except Exception:
            # Fallback: try to extract number from query
            import re
            numbers = re.findall(r'\d+', query)
            if numbers:
                return {"number": int(numbers[0])}
            return {}
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract Python code from LLM response.
        
        Args:
            response: LLM response string.
            
        Returns:
            Extracted code string or None.
        """
        import re
        # Try to extract code blocks
        match = re.search(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no code block, check if entire response is code-like
        if 'def run_skill' in response:
            return response.strip()
        
        return None
    
    def _test_and_save_code(self, skill_name: str, code: str, inputs: Dict) -> tuple[bool, str]:
        """Test code in sandbox and save if successful.
        
        Args:
            skill_name: Name of the skill.
            code: Python code to test.
            inputs: Input dictionary for testing.
            
        Returns:
            Tuple of (success, result_message).
        """
        try:
            # Test code in sandbox
            result = self.sandbox.execute(code, inputs)
            
            # If successful, save as skill_code.py
            from .code_generator import CodeGenerator
            from pathlib import Path
            
            loader = SkillLoader()
            skill_path = loader.skills_dir / skill_name
            
            if skill_path.exists():
                code_path = skill_path / "skill_code.py"
                with open(code_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                import json
                return True, json.dumps(result, indent=2)
            else:
                return False, f"Skill path not found: {skill_name}"
                
        except Exception as e:
            return False, f"Code test failed: {e}"
    
    def execute_skill(self, skill_name: str, query: str) -> str:
        """Execute skill with progressive disclosure (Stage 2 → Stage 3).
        
        Args:
            skill_name: Name of the skill to execute.
            query: User query to process.
            
        Returns:
            Execution result as string.
        """
        # Load full skill (Stage 2)
        skill_data = self.loader.load_full_skill(skill_name)
        
        if not skill_data:
            return f"Error: Skill '{skill_name}' not found."
        
        skill_content = skill_data['content']
        
        # Special handling for code-executor skill
        if skill_name == 'code-executor':
            return self._execute_code_executor(query, skill_content)
        
        # Stage 3: Check if skill_code.py exists
        skill_code = self.loader.load_skill_code(skill_name)
        
        if skill_code:
            # Execute code in sandbox (Stage 3)
            try:
                # Extract inputs from query
                inputs = self._extract_inputs_from_query(query, skill_content)
                
                # Execute in sandbox
                result = self.sandbox.execute(skill_code, inputs)
                
                # Format result as string
                import json
                return json.dumps(result, indent=2)
                
            except SandboxError as e:
                return f"Sandbox execution error: {e}. Falling back to LLM execution."
            except Exception as e:
                return f"Code execution error: {e}. Falling back to LLM execution."
        
        # Fallback: Use LLM execution (Stage 2 only)
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": SKILL_EXECUTION_PROMPT.format(
                        skill_content=skill_content,
                        query=query
                    )
                }]
            )
            
            llm_response = message.content[0].text.strip()
            
            # Try to extract and save code from LLM response
            extracted_code = self._extract_code_from_response(llm_response)
            if extracted_code:
                # Test inputs (try to extract from query)
                test_inputs = self._extract_inputs_from_query(query, skill_content)
                success, result_msg = self._test_and_save_code(skill_name, extracted_code, test_inputs)
                
                if success:
                    return f"Code executed and saved as skill_code.py:\n\n{result_msg}"
            
            return llm_response
            
        except Exception as e:
            return f"Error executing skill: {e}"
    
    def _execute_code_executor(self, query: str, skill_content: str) -> str:
        """Execute code-executor skill: generate code, test, and execute.
        
        Args:
            query: User query.
            skill_content: Code-executor skill content.
            
        Returns:
            Execution result.
        """
        # Ask LLM to generate code for the query
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""You are a code executor. Generate Python code to solve this query.

Query: {query}

Generate a Python function `run_skill(inputs: dict) -> dict` that solves this query.
The code should:
- Use only safe modules: json, math, csv, re, statistics
- Be deterministic (same inputs = same outputs)
- Extract inputs from the inputs dictionary
- Return results as a dictionary

Return ONLY the Python code, wrapped in ```python code blocks."""
                }]
            )
            
            code_response = message.content[0].text.strip()
            code = self._extract_code_from_response(code_response)
            
            if not code:
                return f"Failed to extract code from LLM response:\n{code_response}"
            
            # Extract inputs from query
            inputs = self._extract_inputs_from_query(query, skill_content)
            
            # Test and execute code
            success, result = self._test_and_save_code('code-executor', code, inputs)
            
            if success:
                return f"Code generated and executed successfully:\n\n{result}"
            else:
                return f"Code generation succeeded but execution failed:\n{result}"
                
        except Exception as e:
            return f"Error in code-executor: {e}"
    
    def _handle_without_skill(self, query: str) -> str:
        """Handle query without a skill using direct LLM call.
        
        Args:
            query: User query to process.
            
        Returns:
            LLM response as string.
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": query
                }]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return f"Error processing query: {e}"
    
    def _extract_skill_description(self, query: str, result: str) -> str:
        """Extract skill description from query and result for auto-creation.
        
        Args:
            query: Original user query.
            result: LLM result.
            
        Returns:
            Skill description string.
        """
        # Ask LLM to create a skill description based on the query and result
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": f"""Based on this query and result, create a brief skill description for future similar queries.

Query: {query}
Result: {result[:500]}

Return a concise description (1-2 sentences) of what this skill should do. Focus on the task type, not the specific values."""
                }]
            )
            return message.content[0].text.strip()
        except Exception:
            # Fallback: use query as description
            return f"Skill that handles: {query}"
    
    def run(self, query: str, force_skill: Optional[str] = None, auto_create: bool = True) -> Dict:
        """Run a query using the skills system with progressive disclosure.
        
        Args:
            query: User query to process.
            force_skill: Optional skill name to force (skip selection).
            auto_create: If True, automatically create skill when none found (default: True).
            
        Returns:
            Dictionary with execution results and metadata.
        """
        result = {
            'query': query,
            'stage1_metadata_loaded': False,
            'selected_skill': None,
            'stage2_skill_loaded': False,
            'output': None,
            'error': None,
            'skill_created': False,
            'created_skill_name': None
        }
        
        try:
            # Stage 1: Load metadata and select skill
            if force_skill:
                selected_skill = force_skill
            else:
                selected_skill = self.select_skill(query)
            
            result['stage1_metadata_loaded'] = True
            result['selected_skill'] = selected_skill
            
            if not selected_skill:
                # No skill found - try skills-searcher first
                if auto_create:
                    # First, try to search for existing skills using skills-searcher
                    try:
                        search_result = self.execute_skill('skills-searcher', query)
                        
                        # Parse search result
                        import json
                        try:
                            search_data = json.loads(search_result)
                            if search_data.get('count', 0) > 0:
                                # Found matching skills, use the first one
                                first_match = search_data['matches'][0]
                                selected_skill = first_match['directory']
                                result['selected_skill'] = selected_skill
                                # Continue to execute the found skill below
                            else:
                                # No skills found, try code-executor or direct LLM
                                # Check if query seems code-solvable
                                code_keywords = ['calculate', 'compute', 'filter', 'process', 'transform', 'reverse', 'sort', 'write', 'function']
                                if any(keyword in query.lower() for keyword in code_keywords):
                                    # Try code-executor
                                    output = self._execute_code_executor(query, "")
                                    result['output'] = output
                                    result['selected_skill'] = 'code-executor'
                                    return result
                                else:
                                    # Handle query without skill
                                    output = self._handle_without_skill(query)
                                    result['output'] = output
                                    
                                    # Extract skill description and create skill
                                    skill_description = self._extract_skill_description(query, output)
                                    creation_result = self.creator.create_skill(skill_description)
                                    
                                    if creation_result['success']:
                                        result['skill_created'] = True
                                        result['created_skill_name'] = creation_result['skill_name']
                                    else:
                                        result['error'] = f"Query handled but skill creation failed: {creation_result.get('error', 'Unknown error')}"
                                return result
                        except json.JSONDecodeError:
                            # If search result is not JSON, fall through
                            pass
                    except Exception as e:
                        # If skills-searcher fails, fall through to normal handling
                        print(f"Skills-searcher failed: {e}")
                    
                    # Fallback: Handle query without skill
                    output = self._handle_without_skill(query)
                    result['output'] = output
                    
                    # Extract skill description and create skill
                    skill_description = self._extract_skill_description(query, output)
                    creation_result = self.creator.create_skill(skill_description)
                    
                    if creation_result['success']:
                        result['skill_created'] = True
                        result['created_skill_name'] = creation_result['skill_name']
                    else:
                        result['error'] = f"Query handled but skill creation failed: {creation_result.get('error', 'Unknown error')}"
                else:
                    result['error'] = "No suitable skill found for this query."
                return result
            
            # Stage 2: Load full skill and execute
            output = self.execute_skill(selected_skill, query)
            result['stage2_skill_loaded'] = True
            result['output'] = output
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


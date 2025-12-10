"""Agent orchestration with progressive disclosure."""
from typing import Dict, Optional
import anthropic
from .skill_loader import SkillLoader
from .skill_creator import SkillCreator
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
    
    def execute_skill(self, skill_name: str, query: str) -> str:
        """Stage 2: Execute skill using full instructions.
        
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
        
        # Call LLM to execute skill
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
            
            return message.content[0].text.strip()
            
        except Exception as e:
            return f"Error executing skill: {e}"
    
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
                # No skill found - handle based on auto_create flag
                if auto_create:
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
                        # Skill creation failed, but we still have the output
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


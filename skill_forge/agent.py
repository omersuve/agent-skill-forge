"""Agent orchestration with progressive disclosure."""
from typing import Dict, Optional
import anthropic
from .skill_loader import SkillLoader
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
            
            for s in skills_with_metadata:
                if s['metadata'].get('name', '').lower() == selected_skill_name.lower():
                    return s['dir_name']  # Return directory name, not display name
            
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
    
    def run(self, query: str, force_skill: Optional[str] = None) -> Dict:
        """Run a query using the skills system with progressive disclosure.
        
        Args:
            query: User query to process.
            force_skill: Optional skill name to force (skip selection).
            
        Returns:
            Dictionary with execution results and metadata.
        """
        result = {
            'query': query,
            'stage1_metadata_loaded': False,
            'selected_skill': None,
            'stage2_skill_loaded': False,
            'output': None,
            'error': None
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
                result['error'] = "No suitable skill found for this query."
                return result
            
            # Stage 2: Load full skill and execute
            output = self.execute_skill(selected_skill, query)
            result['stage2_skill_loaded'] = True
            result['output'] = output
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


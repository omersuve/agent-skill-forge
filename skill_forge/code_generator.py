"""Code generator for skill_code.py files."""
from typing import Dict, Optional
import anthropic
from .config import require_api_key
from .prompts import CODE_GENERATION_PROMPT


class CodeGenerator:
    """Generates deterministic Python code for skills."""
    
    def __init__(self, model: str = "claude-3-opus-20240229"):
        """Initialize code generator.
        
        Args:
            model: Anthropic model to use (default: claude-3-opus-20240229)
        """
        self.api_key = require_api_key()
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
    
    def generate_code(self, skill_name: str, skill_content: str, description: str) -> Optional[str]:
        """Generate skill_code.py for a skill.
        
        Args:
            skill_name: Name of the skill.
            skill_content: Full SKILL.md content.
            description: Skill description.
            
        Returns:
            Generated Python code as string, or None if failed.
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": CODE_GENERATION_PROMPT.format(
                        skill_name=skill_name,
                        skill_content=skill_content,
                        description=description
                    )
                }]
            )
            
            code = message.content[0].text.strip()
            
            # Extract code if wrapped in code blocks
            if "```" in code:
                import re
                match = re.search(r'```(?:python)?\n(.*?)\n```', code, re.DOTALL)
                if match:
                    code = match.group(1)
            
            return code
            
        except Exception as e:
            print(f"Error generating code: {e}")
            return None
    
    def generate_and_save(self, skill_name: str, skill_content: str, description: str) -> Dict:
        """Generate and save skill_code.py for a skill.
        
        Args:
            skill_name: Name of the skill directory.
            skill_content: Full SKILL.md content.
            description: Skill description.
            
        Returns:
            Dictionary with generation results.
        """
        result = {
            'success': False,
            'code_path': None,
            'error': None
        }
        
        try:
            from .skill_loader import SkillLoader
            from pathlib import Path
            
            loader = SkillLoader()
            skill_path = loader.skills_dir / skill_name
            
            if not skill_path.exists():
                result['error'] = f"Skill '{skill_name}' not found."
                return result
            
            # Generate code
            code = self.generate_code(skill_name, skill_content, description)
            
            if not code:
                result['error'] = "Failed to generate code."
                return result
            
            # Save code
            code_path = skill_path / "skill_code.py"
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            result['success'] = True
            result['code_path'] = str(code_path)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


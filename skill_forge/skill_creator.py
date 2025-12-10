"""Skill creator using the skill-creator skill."""
from pathlib import Path
from typing import Dict, Optional
import anthropic
import re
from .skill_loader import SkillLoader
from .config import require_api_key
from .prompts import SKILL_CREATION_PROMPT


class SkillCreator:
    """Creates new skills using the skill-creator skill."""
    
    def __init__(self, model: str = "claude-3-opus-20240229"):
        """Initialize the skill creator.
        
        Args:
            model: Anthropic model to use (default: claude-3-opus-20240229)
        """
        self.api_key = require_api_key()
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.loader = SkillLoader()
    
    def load_skill_creator_instructions(self) -> Optional[str]:
        """Load the skill-creator skill instructions.
        
        Returns:
            Skill-creator SKILL.md content or None if not found.
        """
        skill_data = self.loader.load_full_skill("skill-creator")
        if skill_data:
            return skill_data['content']
        return None
    
    def create_skill(self, description: str, skill_name: Optional[str] = None) -> Dict:
        """Create a new skill based on user description.
        
        Args:
            description: User's description of what the skill should do.
            skill_name: Optional skill name (directory name). If not provided, will be generated.
            
        Returns:
            Dictionary with creation results and skill path.
        """
        result = {
            'success': False,
            'skill_name': None,
            'skill_path': None,
            'error': None
        }
        
        try:
            # Load skill-creator instructions
            skill_creator_content = self.load_skill_creator_instructions()
            if not skill_creator_content:
                result['error'] = "skill-creator skill not found. Please ensure it exists in skills/skill-creator/"
                return result
            
            # Generate skill name if not provided
            if not skill_name:
                skill_name = self._generate_skill_name(description)
            
            # Validate skill name
            skill_name = self._sanitize_skill_name(skill_name)
            
            # Check if skill already exists
            skill_path = self.loader.skills_dir / skill_name
            if skill_path.exists():
                result['error'] = f"Skill '{skill_name}' already exists."
                return result
            
            # Create skill using LLM
            skill_md_content = self._generate_skill_md(description, skill_creator_content)
            
            if not skill_md_content:
                result['error'] = "Failed to generate SKILL.md content."
                return result
            
            # Create skill directory and save SKILL.md
            skill_path.mkdir(parents=True, exist_ok=True)
            skill_md_path = skill_path / "SKILL.md"
            
            with open(skill_md_path, 'w', encoding='utf-8') as f:
                f.write(skill_md_content)
            
            result['success'] = True
            result['skill_name'] = skill_name
            result['skill_path'] = str(skill_path)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _generate_skill_name(self, description: str) -> str:
        """Generate a skill name from description.
        
        Args:
            description: Skill description.
            
        Returns:
            Generated skill name (hyphenated, lowercase).
        """
        # Ask LLM to generate a skill name
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": f"""Generate a short, hyphenated skill name (like "example-todo" or "pdf-editor") for this skill description:

{description}

Return ONLY the skill name, nothing else. Use lowercase and hyphens."""
                }]
            )
            
            name = message.content[0].text.strip()
            return self._sanitize_skill_name(name)
        except Exception:
            # Fallback: simple sanitization
            name = description.lower()[:30]
            name = re.sub(r'[^a-z0-9]+', '-', name)
            return name.strip('-')
    
    def _sanitize_skill_name(self, name: str) -> str:
        """Sanitize skill name to valid directory name.
        
        Args:
            name: Raw skill name.
            
        Returns:
            Sanitized skill name.
        """
        # Convert to lowercase, replace spaces/special chars with hyphens
        name = name.lower().strip()
        name = re.sub(r'[^a-z0-9-]+', '-', name)
        name = re.sub(r'-+', '-', name)  # Multiple hyphens to single
        name = name.strip('-')  # Remove leading/trailing hyphens
        
        # Ensure it's not empty
        if not name:
            name = "new-skill"
        
        return name
    
    def _generate_skill_md(self, description: str, skill_creator_content: str) -> Optional[str]:
        """Generate SKILL.md content using LLM and skill-creator instructions.
        
        Args:
            description: User's skill description.
            skill_creator_content: Skill-creator skill instructions.
            
        Returns:
            Generated SKILL.md content or None if failed.
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": SKILL_CREATION_PROMPT.format(
                        skill_creator_instructions=skill_creator_content,
                        user_description=description
                    )
                }]
            )
            
            content = message.content[0].text.strip()
            
            # Extract SKILL.md if it's wrapped in markdown code blocks
            if "```" in content:
                # Try to extract content between ```markdown and ``` or ``` and ```
                match = re.search(r'```(?:markdown|yaml)?\n(.*?)\n```', content, re.DOTALL)
                if match:
                    content = match.group(1)
                    # Remove any yaml code block markers from frontmatter
                    content = re.sub(r'^```yaml\s*\n', '', content, flags=re.MULTILINE)
                    content = re.sub(r'\n```\s*$', '', content, flags=re.MULTILINE)
            
            # Ensure frontmatter is not in code blocks - it should start with ---
            if not content.startswith('---'):
                # Try to find and fix frontmatter
                content = re.sub(r'```yaml\s*\n---', '---', content)
                content = re.sub(r'---\s*\n```', '---', content)
            
            return content
            
        except Exception as e:
            print(f"Error generating skill: {e}")
            return None


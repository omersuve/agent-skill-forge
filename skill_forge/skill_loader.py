"""Skill loader with progressive disclosure support."""
from pathlib import Path
from typing import Dict, List, Optional
import frontmatter


class SkillLoader:
    """Handles loading skills with progressive disclosure."""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        """Initialize skill loader.
        
        Args:
            skills_dir: Path to skills directory. Defaults to skills/ in project root.
        """
        if skills_dir is None:
            # Assume we're in skill_forge package, go up one level
            project_root = Path(__file__).parent.parent
            skills_dir = project_root / "skills"
        self.skills_dir = Path(skills_dir)
    
    def discover_skills(self) -> List[str]:
        """Discover all skill directories.
        
        Returns:
            List of skill names (directory names).
        """
        if not self.skills_dir.exists():
            return []
        
        skills = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    skills.append(item.name)
        return sorted(skills)
    
    def load_metadata(self, skill_name: str) -> Optional[Dict]:
        """Load only metadata (Stage 1: Progressive Disclosure).
        
        Args:
            skill_name: Name of the skill directory.
            
        Returns:
            Dictionary with metadata (name, description, etc.) or None if not found.
        """
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        if not skill_path.exists():
            return None
        
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                metadata = dict(post.metadata)
                return metadata
        except Exception as e:
            print(f"Error loading metadata for {skill_name}: {e}")
            return None
    
    def load_full_skill(self, skill_name: str) -> Optional[Dict]:
        """Load full skill document (Stage 2: Progressive Disclosure).
        
        Args:
            skill_name: Name of the skill directory.
            
        Returns:
            Dictionary with metadata and content, or None if not found.
        """
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        if not skill_path.exists():
            return None
        
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                return {
                    'metadata': dict(post.metadata),
                    'content': post.content,
                    'name': skill_name,
                    'path': skill_path
                }
        except Exception as e:
            print(f"Error loading skill {skill_name}: {e}")
            return None
    
    def load_skill_code(self, skill_name: str) -> Optional[str]:
        """Load skill code if it exists (Stage 3: Progressive Disclosure).
        
        Args:
            skill_name: Name of the skill directory.
            
        Returns:
            Code content as string, or None if skill_code.py doesn't exist.
        """
        code_path = self.skills_dir / skill_name / "skill_code.py"
        if not code_path.exists():
            return None
        
        try:
            with open(code_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading code for {skill_name}: {e}")
            return None
    
    def get_all_metadata(self) -> List[Dict]:
        """Get metadata for all discovered skills.
        
        Returns:
            List of metadata dictionaries.
        """
        skills = self.discover_skills()
        metadata_list = []
        for skill_name in skills:
            metadata = self.load_metadata(skill_name)
            if metadata:
                metadata_list.append(metadata)
        return metadata_list


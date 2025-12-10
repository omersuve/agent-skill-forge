"""CLI entry point for skill-forge."""
import typer
from typing import Optional
from .skill_loader import SkillLoader
from .agent import SkillAgent
from .skill_creator import SkillCreator
from .config import require_api_key

app = typer.Typer(
    name="skill-forge",
    help="A CLI demo showcasing Agent Skills with progressive disclosure"
)


@app.command()
def list_skills(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full skill details")
):
    """List all available skills (shows metadata only by default)."""
    loader = SkillLoader()
    skills = loader.discover_skills()
    
    if not skills:
        typer.echo("No skills found. Use 'skill-forge new' to create one.")
        return
    
    typer.echo(f"\n📚 Found {len(skills)} skill(s):\n")
    
    for skill_name in skills:
        metadata = loader.load_metadata(skill_name)
        if metadata:
            name = metadata.get('name', skill_name)
            description = metadata.get('description', 'No description')
            
            typer.echo(f"  • {name}")
            typer.echo(f"    {description}")
            
            if verbose:
                skill_data = loader.load_full_skill(skill_name)
                if skill_data:
                    typer.echo(f"\n    Full content preview:")
                    # Show first 200 chars of content
                    content_preview = skill_data['content'][:200]
                    if len(skill_data['content']) > 200:
                        content_preview += "..."
                    typer.echo(f"    {content_preview}\n")
            typer.echo()


@app.command()
def new(
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Skill description"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Skill name (directory name)")
):
    """Interactively create a new skill using the skill-creator skill."""
    try:
        # Check API key
        require_api_key()
    except ValueError as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo("🚀 Skill Creator")
    typer.echo("Creating a new skill using the skill-creator skill...\n")
    
    # Get skill description
    if not description:
        description = typer.prompt("Describe what this skill should do")
    
    if not description.strip():
        typer.echo("❌ Skill description cannot be empty.")
        raise typer.Exit(1)
    
    typer.echo(f"\n📝 Description: {description}\n")
    
    # Initialize skill creator
    creator = SkillCreator()
    
    # Check if skill-creator skill exists
    if not creator.load_skill_creator_instructions():
        typer.echo("❌ skill-creator skill not found.")
        typer.echo("Please ensure skills/skill-creator/SKILL.md exists.")
        raise typer.Exit(1)
    
    typer.echo("🤖 Generating skill using LLM...\n")
    
    # Create skill
    result = creator.create_skill(description, skill_name=name)
    
    if result['error']:
        typer.echo(f"❌ Error: {result['error']}")
        raise typer.Exit(1)
    
    if result['success']:
        typer.echo("✅ Skill created successfully!\n")
        typer.echo(f"📁 Skill name: {result['skill_name']}")
        typer.echo(f"📂 Location: {result['skill_path']}")
        typer.echo(f"\n📄 File: {result['skill_path']}/SKILL.md")
        typer.echo("\n✨ You can now use this skill with:")
        typer.echo(f"   skill-forge run \"your query\" --skill {result['skill_name']}")


@app.command()
def run(
    query: str = typer.Argument(..., help="Query to execute using skills"),
    skill: Optional[str] = typer.Option(None, "--skill", "-s", help="Force use of specific skill"),
    auto_create: bool = typer.Option(True, "--auto-create/--no-auto-create", help="Automatically create skill if none found (default: True)")
):
    """Run a query using the skills system with progressive disclosure."""
    try:
        # Check API key
        require_api_key()
    except ValueError as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"🔍 Processing query: {query}\n")
    
    # Initialize agent
    agent = SkillAgent()
    
    # Show Stage 1: Loading metadata
    typer.echo("📋 Stage 1: Loading skill metadata...")
    loader = SkillLoader()
    metadata_list = loader.get_all_metadata()
    typer.echo(f"   Found {len(metadata_list)} skill(s)\n")
    
    # Run agent
    if skill:
        typer.echo(f"🎯 Using forced skill: {skill}\n")
    
    typer.echo("🤖 Selecting and executing skill...\n")
    result = agent.run(query, force_skill=skill, auto_create=auto_create)
    
    # Display results
    if result['error']:
        typer.echo(f"❌ Error: {result['error']}")
        raise typer.Exit(1)
    
    if not result['selected_skill']:
        # No skill found - check if auto-create was used
        if result.get('skill_created'):
            typer.echo("⚠️  No suitable skill found, handled query directly.")
            typer.echo(f"✨ Created new skill: {result['created_skill_name']}")
            typer.echo("   (Next time, this skill will be used automatically)\n")
            typer.echo("─" * 60)
            typer.echo("\n📤 Result:\n")
            typer.echo(result['output'])
            typer.echo("\n" + "─" * 60)
        else:
            typer.echo("⚠️  No suitable skill found for this query.")
            typer.echo("\nAvailable skills:")
            for skill_name in loader.discover_skills():
                metadata = loader.load_metadata(skill_name)
                if metadata:
                    typer.echo(f"  • {metadata.get('name')}: {metadata.get('description')}")
            typer.echo("\n💡 Tip: Use --auto-create (default) to automatically create skills for new queries.")
            raise typer.Exit(1)
    else:
        typer.echo(f"✅ Selected skill: {result['selected_skill']}")
        typer.echo(f"📄 Stage 2: Loaded full skill instructions")
        
        # Check if code was executed (Stage 3)
        skill_code = loader.load_skill_code(result['selected_skill'])
        if skill_code:
            typer.echo(f"⚡ Stage 3: Executed skill_code.py in sandbox (0 tokens, fast!)\n")
        else:
            typer.echo(f"📝 Stage 2: Using LLM execution\n")
        
        typer.echo("─" * 60)
        typer.echo("\n📤 Result:\n")
        typer.echo(result['output'])
        typer.echo("\n" + "─" * 60)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()


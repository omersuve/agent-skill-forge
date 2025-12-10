"""CLI entry point for skill-forge."""
import typer
from typing import Optional
from .skill_loader import SkillLoader
from .agent import SkillAgent
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
def new():
    """Interactively create a new skill."""
    typer.echo("🚀 Skill Creator")
    typer.echo("This will guide you through creating a new skill.\n")
    typer.echo("⚠️  Skill creation with LLM not yet implemented.")
    typer.echo("For now, create skills manually in the skills/ directory.")
    typer.echo("\nExample structure:")
    typer.echo("  skills/my-skill/")
    typer.echo("    SKILL.md")
    typer.echo("    (optional) skill_code.py")


@app.command()
def run(
    query: str = typer.Argument(..., help="Query to execute using skills"),
    skill: Optional[str] = typer.Option(None, "--skill", "-s", help="Force use of specific skill")
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
    result = agent.run(query, force_skill=skill)
    
    # Display results
    if result['error']:
        typer.echo(f"❌ Error: {result['error']}")
        raise typer.Exit(1)
    
    if not result['selected_skill']:
        typer.echo("⚠️  No suitable skill found for this query.")
        typer.echo("\nAvailable skills:")
        for skill_name in loader.discover_skills():
            metadata = loader.load_metadata(skill_name)
            if metadata:
                typer.echo(f"  • {metadata.get('name')}: {metadata.get('description')}")
        raise typer.Exit(1)
    
    typer.echo(f"✅ Selected skill: {result['selected_skill']}")
    typer.echo(f"📄 Stage 2: Loaded full skill instructions\n")
    typer.echo("─" * 60)
    typer.echo("\n📤 Result:\n")
    typer.echo(result['output'])
    typer.echo("\n" + "─" * 60)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()


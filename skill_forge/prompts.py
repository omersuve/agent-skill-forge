"""LLM prompts for skill selection and execution."""


SKILL_SELECTION_PROMPT = """You are an AI agent that needs to select the most appropriate skill to handle a user query.

Available skills (metadata only):
{skills_metadata}

User query: {query}

Your task:
1. Analyze the user query
2. Select the most appropriate skill from the list above
3. Return ONLY the skill name (exactly as shown in the "name" field) or "none" if no skill matches

Response format: Just the skill name, nothing else."""


SKILL_EXECUTION_PROMPT = """You are an AI agent executing a skill to answer a user query.

Skill instructions:
{skill_content}

User query: {query}

Your task:
1. Follow the skill instructions above
2. Process the user query according to the skill's inputs/outputs
3. Return the result in the format specified by the skill

Response:"""


SKILL_CREATION_PROMPT = """You are creating a new skill using the skill-creator guidelines.

Skill Creator Instructions:
{skill_creator_instructions}

User's Skill Description:
{user_description}

Your task:
1. Follow the skill-creator instructions above to create a complete SKILL.md file
2. Include proper YAML frontmatter with:
   - name: (hyphenated skill name)
   - description: (clear description of what the skill does and when to use it)
3. Write the skill body with:
   - Clear instructions on when to use the skill
   - Input/output specifications
   - Usage examples if helpful
   - Keep it concise and focused

Return the complete SKILL.md file content, including the YAML frontmatter and markdown body."""


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

